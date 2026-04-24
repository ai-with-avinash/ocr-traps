# Three Traps That Quietly Invalidate Your OCR Benchmark

*A practitioner's tour through the structural mistakes that make most OCR evaluations lie to you, with the numbers from a 6-model, 107-document benchmark to show what each trap looks like when you actually measure it.*

---

**TL;DR**

We benchmarked six OCR systems — Tesseract, Mistral OCR, Surya, Sarvam OCR, Docling, PaddleOCR — on 107 enterprise documents. The "winning" model changed three times depending on which evaluation protocol we used, and every change was caused by a *structural* flaw in the benchmark, not a modelling difference. We surface the three traps below, show the numbers, and publish a reproducible framework so you can avoid them in your own bake-off.

- **Trap 1:** consensus-seeded ground truth is circular. Mistral OCR hit F1 ≈ **1.00** on four categories because Mistral's own output seeded the reference text. Its genuine forms F1 was **0.4615**.
- **Trap 2:** confidence calibration inverts expectations. The open-source baseline (Tesseract) surfaced Pearson **r = 0.918** between per-document confidence and F1. The commercial API models did not expose comparable signal.
- **Trap 3:** the practitioner's edge cases dominate the final decision. API page caps, wrapper-API drift, and language-pack latency each flipped the "best model" for a workload before accuracy even entered the picture.

The paper is on arXiv: [link pending]. Code + dataset inventory + all result artifacts: [github.com/ai-with-avinash/ocr-traps](https://github.com/ai-with-avinash/ocr-traps).

---

## Why I ran this benchmark

Selecting an OCR stack for an enterprise document pipeline is one of the more thankless technical decisions. Every vendor posts a leaderboard. Every open-source README claims state-of-the-art on *something*. And once you start running models on your own documents, the confident rankings you trusted yesterday quietly stop agreeing with what your eyes are telling you.

I work on the GenAI Practice side, not academic OCR research. My question wasn't *which model is best on the IAM handwriting benchmark?* — it was *if someone on my team ran a quick bake-off of five OCR systems next week, how wrong could their conclusions be?* The answer turned out to be: **very wrong, and in ways that are invisible unless you know to look for them.**

I picked 107 documents across the kinds of inputs a real pipeline sees: federal tax forms with human-verified ground truth, financial tables, multi-column academic layouts, equations, receipts, Devanagari character crops, and one Hindi document. I integrated six OCR systems behind a single `BaseOCRModel` interface, enforced a reproducibility contract (`uv.lock`, a locked corpus manifest, deterministic metric regeneration), and ran the benchmark.

The results were not interesting. The *meta-results* were interesting. Each of the three traps below changed the ranking by a larger margin than any between-model difference in the whole study.

---

## Trap 1 — Consensus-seeded ground truth is circular

### What it looks like

Most internal OCR benchmarks run into the same annotation problem: you want to score against ground truth, but you cannot afford to hand-label every document. A common shortcut is to run the "strongest" model, manually clean its output on a subset, and treat that cleaned text as the reference for scoring every model — including the one that generated it.

This is called **consensus-seeded ground truth**, and it is a trap.

In our corpus, 40 non-form documents (financial tables, multi-column layouts, equations, receipts) received consensus ground truth that was bootstrapped from Mistral OCR's raw output. Here is what Mistral's mean F1 looked like on each category:

| Category | Mistral F1 |
|---|---|
| Financial (consensus GT) | 0.9990 |
| Multi-column (consensus GT) | 1.0000 |
| Equations (consensus GT) | 0.9989 |
| Receipts (consensus GT) | 0.9981 |
| **Forms (independent human GT)** | **0.4615** |

The first four numbers are not real accuracy. They are approximately the identity function — Mistral is being scored against its own output. The fifth number is what Mistral actually does on independently annotated documents.

If you published a whitepaper that simply averaged these rows, you would recommend Mistral as the clear leader at F1 ≈ 0.89. That recommendation would be wrong by **46 percentage points of F1** for anything that looks like a form.

### Why it happens

Consensus GT is not inherently dishonest. It is how every cash-strapped OCR project starts. The trap is forgetting what the reference text actually represents once you start ranking models against it.

Formally, if your reference $R = f(M_{seed}, \text{human edits})$ for some seed model $M_{seed}$, and you score any model $M_i$'s output $O_i$ against $R$, then the error $d(O_i, R)$ has two components:

1. The genuine distance between $O_i$ and the true document content.
2. The distance between $R$ and the true document content — which is systematically smaller for $M_{seed}$ than for any other model.

The moment you use mean F1 on this subset as a ranking, $M_{seed}$ wins by construction.

### How to avoid it

The protocol we now enforce in the framework:

1. Mark every ground-truth file with its provenance: `human_verified`, `consensus_from_<model>`, or `none`.
2. When ranking models, exclude any model whose output seeded the consensus from that tier's ranking. Score it descriptively but never comparatively.
3. Keep a strictly unbiased subset (in our corpus, 20 human-verified federal tax forms) for all headline accuracy claims.

Under this protocol, the forms-only ranking in our corpus is:

| Model | n | F1 | Wilcoxon vs. Mistral |
|---|---|---|---|
| Docling | 20 | 0.8220 | p = 0.0076, d = 0.848 (large) |
| Tesseract | 20 | 0.8122 | p = 0.0092, d = 0.729 (medium) |
| Surya | 5 | 0.7710 | underpowered |
| Sarvam OCR | 11 | 0.7313 | — |
| Mistral OCR | 16 | 0.4615 | — |

Tesseract and Docling statistically tie on forms (p = 0.498, negligible effect size), and both are significantly better than Mistral. That is the *real* forms ranking. The consensus-tier ranking is a separate, non-circular question best answered by excluding Mistral, which puts Surya at the top with F1 = 0.7717 over 40 documents.

**Takeaway for your benchmark:** if you did not hand-label the ground truth, write "CIRCULAR — do not use for ranking" in big letters across the page before anyone reads a table.

---

## Trap 2 — Confidence calibration is not where you think it is

### What it looks like

Accuracy is only half the production decision. The other half is: **when the model is wrong, can you tell?** A model that confidently emits garbage is more dangerous than a model that surfaces "I am unsure about this page" with 80 % reliability. Everyone agrees with this in principle. Almost no benchmark measures it.

Tesseract exposes a per-word confidence score as a byproduct of its segmentation pipeline. We computed the average per-word confidence for each document Tesseract processed and correlated it against the per-document token F1 on the 45 documents where Tesseract produced output *and* we had ground truth to score against.

**Result: Pearson r = 0.918, Spearman ρ = 0.925, both p < 10⁻¹⁹ at n = 45.**

For a production system, this is a massive and highly actionable result. A Tesseract confidence score below roughly 0.6 is a near-perfect rejection signal: those documents are overwhelmingly wrong, and they should be routed to human review instead of trusting the extracted text downstream.

The two commercial API systems in the benchmark — Mistral OCR and Sarvam OCR — do not expose a per-document confidence channel at all. You get a string back. There is no analogous calibration number to measure, so the same reliability test cannot even be performed on them.

### Why this inverts the expected winner

The naive narrative around commercial vs. open-source OCR is "pay for accuracy." Our numbers actually support that narrative on forms (Mistral and Sarvam reach competitive F1 on human-verified forms), but they *invert* it on the question of *which system is safe to deploy without a human reviewer in the loop*.

On calibration, the ranking is:

1. **Tesseract** — exposes strong confidence signal, usable for automated rejection.
2. **Docling, Surya** — may have internal confidence but it is not surfaced consistently enough to be production-safe.
3. **Mistral OCR, Sarvam OCR** — no per-document confidence channel; you are flying blind.

If your pipeline needs to flag low-confidence documents for human review before downstream processing, the "weakest on accuracy" model in the benchmark is the *only* model that solves that problem cleanly.

### How to measure it in your own benchmark

Add two columns to your result table:

- **Confidence exposed?** (yes/no)
- **Confidence-quality correlation** (Pearson r, Spearman ρ, with n and p-value)

If a commercial vendor does not expose a confidence signal, note that as a deployment risk — not as an accuracy-neutral footnote. A 3-point F1 lead does not compensate for losing automated rejection.

**Takeaway:** calibration is orthogonal to accuracy, and "best F1" is a misleading single-number summary.

---

## Trap 3 — The practitioner's edge cases reorder everything

### What it looks like

Academic OCR leaderboards normalize away the operational surface that actually determines which system you can run. Three examples from our benchmark that changed the ranking for real workloads:

#### 3a — API page caps

Sarvam OCR's Document Intelligence API refuses any PDF with more than 10 pages. In our corpus, four federal-form PDFs exceed this limit:

- `fw2` (11 pages)
- `f1040es` (16 pages)
- `SF-85-questionnaire` (18 pages)
- `sf2809` (18 pages)

These four documents are *exactly* the kind of long, structured government forms that make or break a tax/compliance pipeline. The failure mode is not a low F1 score — it is a hard `BadRequestError status_code=400 body={"error": {"message": "PDF has 11 pages, maximum allowed is 10."}}` before Sarvam sees a pixel.

On forms ≤ 10 pages, Sarvam is a viable choice. On a federal-forms pipeline, it is disqualified before the accuracy column matters.

#### 3b — Wrapper API drift

Three of the six models broke their Python interface during the period I was running this benchmark.

- **Surya** migrated from a monolithic `RecognitionPredictor` class to a decomposed set of specialized predictors, forcing a wrapper rewrite.
- **PaddleOCR** required version-aware API handling because the same `ocr()` call returns different structures across point releases.
- **Sarvam OCR** could not be called via the simple request/response pattern used by every other API wrapper in the framework — the SDK requires a `create_job` → `upload_file` → `start` → `wait_until_complete` → `download_output` asynchronous flow.

For a benchmark whose credibility depends on running tomorrow with the same numbers it produced today, wrapper drift is a first-class reproducibility hazard. It is not an "engineering ergonomics" footnote.

#### 3c — Language-pack latency

The default Tesseract configuration in the framework loaded five language packs (`eng+hin+tel+tam+ben`) because the corpus spans English forms, Devanagari character crops, and other Indic scripts. When we ran a paired one-knob ablation on 15 English-only USGov forms:

| Variant | CER | F1 | Latency |
|---|---|---|---|
| `eng` only | 0.3410 | 0.9185 | 21,119 ms |
| `eng+hin+tel+tam+ben` | 0.3259 | 0.9170 | 47,248 ms |
| Δ (multi − eng) | −0.0151 | −0.0015 | **+26,129 ms** |

The multi-language pack costs **2.24×** the latency with essentially no accuracy difference on English inputs. Worse, my earlier project notes claimed the multi-language pack "garbled Indic characters" — a plausible-sounding qualitative observation that turned out to be unsupported once we ran the paired measurement.

The default configuration was paying for coverage it never used, and the project had baked a wrong qualitative claim into its README for months.

### The general shape of Trap 3

Every production-relevant OCR decision has a spine of:

- hard API limits (pages, file sizes, rate limits, credit caps)
- wrapper / SDK churn (not a one-time cost — it recurs)
- configuration choices with silent latency costs that never show up on a leaderboard
- failure modes that are qualitatively different between models even at similar F1 (Docling's conservative omissions vs. Sarvam's insertion-heavy outputs are not interchangeable in a human-review pipeline)

None of this is captured by the standard "CER / WER / F1 / latency" table. All of it reorders real deployment decisions.

**Takeaway:** before you score a single document, list the operational constraints of your workload and mark each candidate model as feasible / infeasible / conditional. The accuracy column is meaningless on infeasible rows.

---

## What "winner" actually means in our benchmark

After avoiding the three traps, there is no single winner. There are five clean recommendation positions:

- **Tesseract and Docling** co-lead on unbiased forms accuracy (F1 0.8122 and 0.8220 at n = 20; statistically indistinguishable from each other; both significantly better than Mistral). Tesseract additionally wins on calibration. Docling additionally wins on conservative, deletion-dominant error profile — which is what you want when wrong extraction is more expensive than missing extraction.
- **Surya** wins the consensus-tier aggregate F1 (0.7717 at n = 40) when Mistral is properly excluded. Surya has low overall visible-corpus reliability (32 / 107), so it is a "deploy behind Mistral for fallback" answer, not a "deploy as default" answer.
- **Mistral OCR** is the most reliable operational default at 92 / 107 success. It is excluded from consensus-tier ranking, and its real forms F1 is 0.4615. Use it when throughput and coverage matter more than best-case accuracy.
- **Sarvam OCR** is competitive across every category it successfully processes (forms 0.7313, financial 0.7619, multi-column 0.7410, equations 0.7227, receipts 0.6684) with the highest recall among non-circular models (0.8849). The 10-page cap disqualifies it for long federal-form workloads.
- **PaddleOCR** remains partial (financial-only) in our benchmark and is not ranked overall.

The single most surprising deployment conclusion: **the best model to deploy with no human review in the loop is the weakest one on accuracy**, because it is the only one whose confidence score is actually informative.

---

## Reproduce the whole thing in one afternoon

Everything in this post is reproducible from the public repo. The environment is reproducible via `uv.lock`, the corpus is committed, and all result artifacts are regenerated deterministically from `results/expanded_gt_metrics/*.json`.

```bash
git clone https://github.com/ai-with-avinash/ocr-traps.git
cd ocr-traps
uv venv --python 3.12
source .venv/bin/activate
uv sync
cp .env.example .env          # add Mistral + Sarvam API keys

python cli/run_model.py --model tesseract
python cli/run_model.py --model docling
python cli/run_model.py --model surya
python cli/run_model.py --model mistral_ocr
python tools/sarvam_rerun_throttled.py
python tools/recompute_metrics.py
python cli/evaluate.py --results-dir results/latest --export-csv
```

All numbers in this post trace back to `results/expanded_gt_metrics/per_doc_metrics.csv` and `results/expanded_gt_metrics/statistical_tests.json`.

---

## Closing

Internal OCR benchmarks are a quiet source of downstream bad decisions. The three traps above are not novel, but they are persistently underweighted in practitioner write-ups, and each of them inverted a conclusion in my own benchmark that I would have published confidently otherwise.

If you are about to run a bake-off, the low-cost protocol is:

1. Hand-label a subset. Never rank against consensus GT that your own candidate models produced.
2. Measure calibration, not just accuracy. No confidence channel = deployment risk column.
3. List operational constraints first. Infeasible models are infeasible regardless of F1.

Everything else — model choice, dataset expansion, metric selection — is a second-order concern next to these three. The framework, dataset inventory, and paper are on GitHub; the arXiv preprint link will be added when it goes live.

If you find a fourth trap, open an issue.

---

**Paper:** *A Practitioner's OCR Benchmark: Three Traps Real Evaluations Hit* — arXiv preprint (link pending).
**Code + data:** [github.com/ai-with-avinash/ocr-traps](https://github.com/ai-with-avinash/ocr-traps)
**Contact:** Avinash Seethalam · GenAI Practice · [ORCID 0009-0007-1068-6156](https://orcid.org/0009-0007-1068-6156) · sreethalam.avinash@gmail.com
