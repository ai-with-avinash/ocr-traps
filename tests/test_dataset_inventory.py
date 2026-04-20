from pathlib import Path

from utils.dataset_inventory import build_manifest, category_counts, find_documents
from recompute_metrics import build_corpus_summary


def write_file(path: Path, content: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_find_documents_ignores_hidden_and_ground_truth(tmp_path: Path):
    write_file(tmp_path / "02_complex_tables/forms/doc1.png")
    write_file(tmp_path / "06_mixed_content/receipts/doc2.jpg")
    write_file(tmp_path / "02_complex_tables/forms/.hidden.png")
    write_file(tmp_path / "02_complex_tables/forms/._sidecar.png")
    write_file(tmp_path / "ground_truth/02_complex_tables/doc1_gt.txt")
    write_file(tmp_path / "manifest.json")
    write_file(tmp_path / "download_log.txt")

    docs = find_documents(tmp_path)

    assert [doc.name for doc in docs] == ["doc1.png", "doc2.jpg"]
    assert category_counts(docs) == {
        "02_complex_tables/forms": 1,
        "06_mixed_content/receipts": 1,
    }


def test_build_manifest_matches_visible_document_rules(tmp_path: Path):
    write_file(tmp_path / "02_complex_tables/forms/doc1.png")
    write_file(tmp_path / "02_complex_tables/forms/.hidden.png")
    write_file(tmp_path / "02_complex_tables/forms/._sidecar.png")
    write_file(tmp_path / "06_mixed_content/receipts/doc2.jpg")
    write_file(tmp_path / "ground_truth/06_mixed_content/doc2_gt.txt")

    total, manifest = build_manifest(
        tmp_path,
        ["02_complex_tables/forms", "06_mixed_content/receipts"],
    )

    assert total == 2
    assert manifest == {
        "02_complex_tables/forms": ["doc1.png"],
        "06_mixed_content/receipts": ["doc2.jpg"],
    }


def test_build_corpus_summary_reports_gt_and_no_gt_counts():
    docs = [
        Path("test-dataset/02_complex_tables/forms/doc1.png"),
        Path("test-dataset/02_complex_tables/forms/doc2.png"),
        Path("test-dataset/06_mixed_content/receipts/doc3.jpg"),
    ]
    gt_entries = {
        "doc1": {
            "path": Path("test-dataset/ground_truth/02_complex_tables/doc1.json"),
            "category": "02_complex_tables/forms",
            "tier": "human_verified",
        },
        "doc3": {
            "path": Path("test-dataset/ground_truth/06_mixed_content/doc3_gt.txt"),
            "category": "06_mixed_content/receipts",
            "tier": "consensus",
        },
    }
    model_run_coverage = {
        "tesseract": {
            "run_dir": "results/example",
            "coverage_basis": "results_json",
            "visible_doc_total": 3,
            "attempted_visible_docs": 3,
            "successful_visible_docs": 2,
            "attempt_rate_pct": 100.0,
            "success_rate_pct": 66.7,
            "results_not_in_current_corpus": 0,
            "category_attempts": {
                "02_complex_tables/forms": {"visible_total": 2, "attempted": 2, "successful": 1},
                "06_mixed_content/receipts": {"visible_total": 1, "attempted": 1, "successful": 1},
            },
        }
    }

    summary = build_corpus_summary(docs, gt_entries, model_run_coverage)

    assert summary["visible_document_count"] == 3
    assert summary["visible_documents_by_category"] == {
        "02_complex_tables/forms": 2,
        "06_mixed_content/receipts": 1,
    }
    assert summary["ground_truth"]["total_documents"] == 2
    assert summary["ground_truth"]["tier_totals"] == {
        "consensus": 1,
        "human_verified": 1,
    }
    assert summary["ground_truth"]["no_gt_count"] == 1
    assert summary["ground_truth"]["no_gt_by_category"] == {
        "02_complex_tables/forms": 1,
        "06_mixed_content/receipts": 0,
    }
