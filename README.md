# ocr-traps

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![uv](https://img.shields.io/badge/built%20with-uv-000000.svg)](https://docs.astral.sh/uv/)
[![arXiv](https://img.shields.io/badge/arXiv-pending-b31b1b.svg)](#citation)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19741773.svg)](https://doi.org/10.5281/zenodo.19741773)

Reproducible benchmark of six OCR systems on 107 enterprise documents, with a focus on the structural traps that invalidate most practitioner OCR bake-offs.

> **Companion paper:** *A Practitioner's OCR Benchmark: Three Traps Real Evaluations Hit* — arXiv preprint (link added at release).

## Why this exists

Most internal OCR evaluations produce confident rankings that invert the moment the evaluation protocol changes. After running ten integrated models over 107 documents, we surface three reproducible traps that every enterprise team hits:

### Finding 1 — Consensus-seeded ground truth leaks at practitioner-relevant magnitude

The underlying principle (do not score a model against ground truth its own output helped construct) is the deployment-side cousin of the well-known train-on-test antipattern. The contribution here is not the principle but the **empirical magnitude on a deployed practitioner corpus** and a concrete protocol rule.

The mechanism is GT-construction leakage, not training contamination: a seed model's output is shown to human verifiers, who accept or edit rather than transcribe blind, and the resulting "human-verified" reference inherits the seed model's idiosyncrasies. Practitioner teams routinely conflate "human-edited" with "human-verified" and report the result as unbiased ground truth.

In our corpus, Mistral OCR scores **F1 ≈ 1.00 on the four consensus-seeded categories** (financial, multi-column, equations, receipts) and **F1 = 0.4615 on 20 forms transcribed independently of any model output**. The gap is larger than any genuine between-model difference in the benchmark and reflects evaluation protocol, not model quality.

**Protocol rule we now enforce:** any model whose output contributed to a tier's reference text is excluded from cross-model ranking on that tier. The independently transcribed forms subset is the only tier used for headline accuracy claims.

### Finding 2 — Confidence calibration flips the expected winner

The open-source baseline (Tesseract) exposes per-word confidence that is strongly predictive of per-document F1: **Pearson r = 0.918, Spearman ρ = 0.925** (n=45, p<10⁻¹⁹). A Tesseract confidence below ~0.6 is a reliable rejection signal — you can send that document to human review instead of trusting the output.

The commercial API models in this benchmark (Mistral OCR, Sarvam OCR) do **not** expose comparable per-document confidence. "Best accuracy" and "best production signal" are therefore different questions, and the answers diverge.

### Finding 3 — Practitioner's edge cases dominate the final decision

Three examples we hit during this benchmark that don't show up in academic OCR leaderboards:

- **API page caps:** Sarvam OCR rejects any PDF > 10 pages. Four long federal-form PDFs (`fw2`=11pp, `f1040es`=16pp, `SF-85-questionnaire`=18pp, `sf2809`=18pp) failed before we even looked at accuracy.
- **Wrapper API drift:** Surya required migrating to a new predictor architecture mid-benchmark; PaddleOCR required version-aware API handling; Sarvam OCR required an async job workflow rather than a single request/response. Benchmark reproducibility is a moving target.
- **Language-pack cost:** Tesseract with `eng+hin+tel+tam+ben` is **2.24× the latency** of `eng` only on English forms, with **no measurable accuracy loss** (ΔCER = −0.0151, ΔF1 = −0.0015). The default multi-language configuration we shipped was paying for coverage it never used.

## Phase 1 headline numbers (non-circular)

| Tier | Rank | Models | F1 |
|---|---|---|---|
| **Forms** (n=20, human-verified) | Co-lead | Docling, Tesseract | 0.8220, 0.8122 |
| **Consensus aggregate** (n=40, Mistral excluded) | Lead | Surya | 0.7717 |
| **Operational reliability** (107-doc visible corpus) | Lead | Mistral OCR | 92/107 success |

Full per-category tables, Wilcoxon pairwise tests, and error decomposition are in `docs/whitepaper/tables.md` and the paper.

## Quick start

### Reproducible setup (uv, recommended)
```bash
git clone https://github.com/ai-with-avinash/ocr-traps.git
cd ocr-traps

curl -LsSf https://astral.sh/uv/install.sh | sh     # if uv not installed
uv venv --python 3.12
source .venv/bin/activate
uv sync                        # runtime deps
uv sync --group dev            # + pytest, ruff, pylint

cp .env.example .env           # add Mistral + Sarvam API keys
```

### Reproduce the paper numbers

```bash
# Run each Phase 1 model on the full locked corpus
python cli/run_model.py --model tesseract
python cli/run_model.py --model docling
python cli/run_model.py --model surya
python cli/run_model.py --model mistral_ocr
python cli/run_model.py --model paddleocr
python tools/sarvam_rerun_throttled.py         # rate-limit friendly

# Recompute all metrics against the expanded human-verified GT
python tools/recompute_metrics.py

# Generate HTML report + CSV export
python cli/evaluate.py --results-dir results/latest --export-csv
```

Authoritative numeric sources cited in the paper:
- `results/expanded_gt_metrics/corpus_summary.json`
- `results/expanded_gt_metrics/model_summaries.json`
- `results/expanded_gt_metrics/per_doc_metrics.csv`
- `results/expanded_gt_metrics/statistical_tests.json`
- `test-dataset/manifest.json`

## Adding a new OCR model

1. Create `models/<your_model>.py`
2. Inherit `BaseOCRModel`, implement `_ocr_impl(image_path) -> OCRResult`
3. Decorate class with `@register_model` — no manual wiring needed
4. Add non-secret config to `configs/config.yaml`
5. Add API key reference (if any) to `.env.example`

## Models integrated (10 wrappers; 6 benchmarked in Phase 1)

| # | Model | Type | GPU needed | Phase 1 benchmarked? |
|---|-------|------|-------------|---|
| 1 | Tesseract | Open source | No (CPU) | ✅ |
| 2 | PaddleOCR | Open source | Optional | Partial (financial only) |
| 3 | Docling / SmolDocling | Open source | Optional | ✅ |
| 4 | Surya OCR | Open source | Optional | ✅ |
| 5 | Mistral OCR | API | No | ✅ (forms-only ranking) |
| 6 | Sarvam Vision OCR | API | No | ✅ (GT-backed subset) |
| 7 | DeepSeek OCR | Open source | Yes (16GB+) | Phase 2 |
| 8 | olmOCR | Open source | Yes (16GB+) | Phase 2 |
| 9 | Qwen2.5-VL | Open source | Yes (16GB+) | Phase 2 |
| 10 | GOT-OCR 2.0 | Open source | Yes (8–16GB) | Phase 2 |

## Test dataset

107 documents committed under `test-dataset/`. No download required.

| Category | Docs | Ground truth |
|---|---:|---|
| Forms | 20 | Human-verified |
| Financial tables | 15 | 9 consensus |
| Multi-column | 17 | 11 consensus |
| Equations | 14 | 10 consensus |
| Receipts | 10 | 10 consensus (seeded from Mistral — see Finding 1) |
| Handwritten Devanagari | 30 | None (32×32 char crops, not page-scale) |
| Hindi document | 1 | None |
| **Total** | **107** | **60 GT-evaluable** (20 human + 40 consensus) |

## Platform notes

**Apple Silicon:** MPS works for the optional-GPU models. 32 GB+ unified memory handles the 7B–9B VLMs. Set `device: mps` in `configs/config.yaml`. 30B+ models need cloud GPU.

**Linux:** `sudo apt install tesseract-ocr tesseract-ocr-hin tesseract-ocr-tel tesseract-ocr-tam tesseract-ocr-ben`. CUDA users install PyTorch with CUDA.

**Windows:** Tesseract needs separate install via [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki). PowerShell activation is `venv\Scripts\Activate.ps1`.

## Known issues

- **Tesseract not found**: system binary, not a pip package. macOS `brew install tesseract tesseract-lang`; Linux apt; Windows UB-Mannheim.
- **Mistral SDK import path**: SDK v2 uses `from mistralai.client import Mistral` not `from mistralai import Mistral`.
- **Tesseract multi-lang latency**: see Finding 3 above. Default is `eng` only in `configs/config.yaml`.
- **Sarvam 10-page cap**: 4 federal-form PDFs exceed the limit and are logged as failures. Split the PDFs upstream if coverage matters.
- **PaddleOCR on Apple Silicon**: set `use_gpu: false` in `configs/config.yaml` if GPU errors.

## Project layout

```
ocr-traps/
├── cli/                    # run_single, run_model, run_batch, evaluate
├── models/                 # 10 OCR wrappers (self-registering)
├── utils/                  # runner, metrics, report, helpers
├── tools/                  # sarvam_rerun_throttled, recompute_metrics, generate_charts, ...
├── configs/config.yaml     # non-secret settings only
├── .env                    # API keys (gitignored)
├── test-dataset/           # 107 documents + ground truth
├── results/                # timestamped run dirs (gitignored)
└── docs/whitepaper/        # paper source (LaTeX + tables.md + figures)
```

## Citation

```bibtex
@software{seethalam_ocrtraps_2026,
  author  = {Seethalam, Avinash},
  title   = {ocr-traps: A Practitioner's OCR Benchmark},
  year    = {2026},
  url     = {https://github.com/ai-with-avinash/ocr-traps},
  doi     = {10.5281/zenodo.19741773},
  orcid   = {0009-0007-1068-6156}
}
```

Zenodo DOI: [10.5281/zenodo.19741773](https://doi.org/10.5281/zenodo.19741773). arXiv preprint link added once published. See `CITATION.cff` for structured metadata.

## License

Code is released under the [MIT License](./LICENSE). The companion paper and this README are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Contact

Avinash Seethalam · GenAI Practice · [sreethalam.avinash@gmail.com](mailto:sreethalam.avinash@gmail.com) · [ORCID](https://orcid.org/0009-0007-1068-6156)
