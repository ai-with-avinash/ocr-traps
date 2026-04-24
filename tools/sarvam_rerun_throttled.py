#!/usr/bin/env python3
"""Throttled Sarvam OCR rerun — friendly to free-tier rate limits.

Runs Sarvam only on ground-truth-backed documents, sleeps between calls,
and halts on repeated 429s so we do not burn credits against a wall.

Usage:
    source venv/bin/activate
    python tools/sarvam_rerun_throttled.py           # full GT subset
    python tools/sarvam_rerun_throttled.py --limit 1 # smoke test one doc
    python tools/sarvam_rerun_throttled.py --sleep 6 # custom inter-call delay
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from models import get_model  # noqa: E402
from utils.helpers import (  # noqa: E402
    get_document_category,
    get_ground_truth,
    load_config,
)
from utils.metrics import compute_all_metrics  # noqa: E402


def _find_gt_backed_docs(dataset_dir: Path, gt_dir: Path) -> list[Path]:
    """Return source documents that have a matching ``<stem>_gt.txt`` sibling."""
    exts = {".png", ".jpg", ".jpeg", ".pdf"}
    gt_stems = {p.stem[:-3] for p in gt_dir.rglob("*_gt.txt")}
    docs: list[Path] = []
    seen: set[str] = set()
    for p in sorted(dataset_dir.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in exts:
            continue
        if "ground_truth" in p.parts:
            continue
        if p.stem in gt_stems and p.stem not in seen:
            docs.append(p)
            seen.add(p.stem)
    return docs


def _is_rate_limit(err: str) -> bool:
    if not err:
        return False
    low = err.lower()
    return "rate limit" in low or "too many requests" in low


def _is_quota_exhausted(err: str) -> bool:
    if not err:
        return False
    low = err.lower()
    return (
        "insufficient_quota" in low
        or "no credits" in low
        or "quota exceeded" in low
    )


def _is_auth_failure(err: str) -> bool:
    if not err:
        return False
    low = err.lower()
    # Require word-ish boundaries around HTTP status codes to avoid UUID
    # collisions (e.g. an x-request-id containing "4039").
    return (
        "status_code: 401" in low
        or "status_code: 403" in low
        or "unauthorized" in low
        or "forbidden" in low
        or "invalid api" in low
        or "invalid_api_key" in low
        or "authentication" in low and "fail" in low
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/config.local.yaml")
    parser.add_argument("--sleep", type=float, default=4.0,
                        help="Seconds to wait between successful calls (default 4).")
    parser.add_argument("--backoff", type=float, default=60.0,
                        help="Seconds to wait after a 429 before retrying (default 60).")
    parser.add_argument("--max-429", type=int, default=3,
                        help="Abort after this many consecutive 429 responses (default 3).")
    parser.add_argument("--limit", type=int, default=0,
                        help="Process at most this many docs (0 = all).")
    args = parser.parse_args()

    config = load_config(args.config)
    api_key = (config.get("sarvam") or {}).get("api_key", "")
    if not api_key:
        print("❌ SARVAM_API_KEY not set in .env — aborting.", file=sys.stderr)
        return 2
    print(f"🔑 Sarvam key loaded (suffix ...{api_key[-6:]})")

    dataset_dir = Path(config["paths"]["dataset_dir"])
    gt_dir = Path(config["paths"]["ground_truth_dir"])
    results_base = Path(config["paths"]["results_dir"])

    docs = _find_gt_backed_docs(dataset_dir, gt_dir)
    if args.limit:
        docs = docs[: args.limit]
    if not docs:
        print("⚠ No ground-truth-backed documents found — nothing to do.")
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = results_base / f"{ts}_sarvam_rerun"
    (run_dir / "raw_outputs").mkdir(parents=True, exist_ok=True)
    (run_dir / "metrics").mkdir(parents=True, exist_ok=True)

    print(f"📁 Writing to {run_dir}")
    print(f"📊 {len(docs)} GT-backed documents queued | sleep={args.sleep}s | "
          f"backoff={args.backoff}s | max_429={args.max_429}")

    model = get_model("sarvam_ocr", config)

    results: list[dict] = []
    metrics_list: list[dict] = []
    consecutive_429 = 0
    aborted = False
    abort_reason = ""

    results_path = run_dir / "sarvam_ocr_results.json"
    metrics_path = run_dir / "metrics" / "sarvam_ocr_metrics.json"

    for idx, doc_path in enumerate(docs, 1):
        print(f"[{idx:>3}/{len(docs)}] {doc_path.name}", flush=True)
        try:
            result = model.ocr(str(doc_path))
        except Exception as exc:  # pragma: no cover — defensive against SDK raise
            result = None
            err = f"{type(exc).__name__}: {exc}"
            print(f"    ❌ exception: {err[:200]}")
            results.append({
                "document_path": str(doc_path.resolve()),
                "document_name": doc_path.name,
                "category": get_document_category(str(doc_path)),
                "success": False,
                "error": err,
                "latency_ms": 0,
            })
        else:
            rd = result.to_dict()
            rd["category"] = get_document_category(str(doc_path))
            results.append(rd)

            if result.success:
                consecutive_429 = 0
                print(f"    ✅ {len(result.raw_text)} chars in {result.latency_ms:.0f}ms")
                cat_slug = rd["category"].replace("/", "_")
                out_file = run_dir / "raw_outputs" / f"sarvam_ocr__{cat_slug}__{doc_path.stem}.txt"
                out_file.write_text(result.raw_text, encoding="utf-8")

                gt = get_ground_truth(str(doc_path), str(gt_dir))
                if gt:
                    m = compute_all_metrics(result.raw_text, gt, str(doc_path), "sarvam_ocr")
                    metrics_list.append(m.to_dict())
                    print(f"    📈 CER={m.cer:.4f} F1={m.f1:.4f}")
            else:
                err = result.error or ""
                print(f"    ❌ {err[:200]}")
                if _is_quota_exhausted(err):
                    aborted = True
                    abort_reason = f"quota exhausted on doc {idx}: {err[:300]}"
                    break
                if _is_auth_failure(err):
                    aborted = True
                    abort_reason = f"authentication failure on doc {idx}: {err[:300]}"
                    break
                if _is_rate_limit(err):
                    consecutive_429 += 1
                    print(f"    ⏳ rate limit hit ({consecutive_429}/{args.max_429}) — "
                          f"sleeping {args.backoff:.0f}s")
                    time.sleep(args.backoff)
                    if consecutive_429 >= args.max_429:
                        aborted = True
                        abort_reason = f"{consecutive_429} consecutive 429s at doc {idx}"
                        break
                else:
                    consecutive_429 = 0

        # Persist after every doc so a kill mid-run loses nothing.
        with results_path.open("w") as fh:
            json.dump(results, fh, indent=2, ensure_ascii=False)
        if metrics_list:
            with metrics_path.open("w") as fh:
                json.dump(metrics_list, fh, indent=2)

        if idx < len(docs):
            time.sleep(args.sleep)

    model.teardown()

    successful = sum(1 for r in results if r.get("success"))
    summary = {
        "run_dir": str(run_dir),
        "model": "sarvam_ocr",
        "total_queued": len(docs),
        "attempted": len(results),
        "successful": successful,
        "docs_with_metrics": len(metrics_list),
        "aborted": aborted,
        "abort_reason": abort_reason,
        "config": {"sleep": args.sleep, "backoff": args.backoff, "max_429": args.max_429,
                   "limit": args.limit},
    }
    if metrics_list:
        summary["avg_cer"] = round(sum(m["cer"] for m in metrics_list) / len(metrics_list), 4)
        summary["avg_wer"] = round(sum(m["wer"] for m in metrics_list) / len(metrics_list), 4)
        summary["avg_f1"] = round(sum(m["f1"] for m in metrics_list) / len(metrics_list), 4)
    with (run_dir / "run_summary.json").open("w") as fh:
        json.dump(summary, fh, indent=2)

    print("\n" + "=" * 60)
    print(f"  Attempted: {len(results)} | Success: {successful} | "
          f"GT-scored: {len(metrics_list)}")
    if "avg_cer" in summary:
        print(f"  Avg CER={summary['avg_cer']} WER={summary['avg_wer']} F1={summary['avg_f1']}")
    if aborted:
        print(f"  ⚠ Aborted early: {abort_reason}")
    print(f"  Artifacts: {run_dir}")
    print("=" * 60)

    return 0 if successful > 0 else 3


if __name__ == "__main__":
    sys.exit(main())
