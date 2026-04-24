# OCR Whitepaper Submission Tables

This file mirrors the main-paper package in
`docs/whitepaper/latex/main.tex`.

Authoritative numeric sources:

- `results/expanded_gt_metrics/corpus_summary.json`
- `results/expanded_gt_metrics/model_summaries.json`
- `results/expanded_gt_metrics/per_doc_metrics.csv`
- `results/expanded_gt_metrics/statistical_tests.json`
- `test-dataset/manifest.json`

Metrics regenerated against the expanded $n=20$ human-verified forms tier; pairwise forms-only Wilcoxon rows are now populated.

## Table 1: Dataset and GT Coverage

| Category | Visible docs | Human GT | Consensus GT | No GT |
|:---|---:|---:|---:|---:|
| Financial tables | 15 | 0 | 9 | 6 |
| Forms | 20 | 20 | 0 | 0 |
| Multi-column | 17 | 0 | 11 | 6 |
| Handwritten Devanagari | 30 | 0 | 0 | 30 |
| Hindi document | 1 | 0 | 0 | 1 |
| Equations | 14 | 0 | 10 | 4 |
| Receipts | 10 | 0 | 10 | 0 |
| **Total** | **107** | **20** | **40** | **47** |

Caption rule:

- Visible counts refer to visible OCR inputs only.
- Forms are the only human-verified category (20 documents).
- Handwritten and Hindi have no GT and therefore do not support comparative accuracy claims.

## Table 2: Model Set and Run Coverage

| Model | Deployment | Success on visible corpus | Mean latency (ms) | GT coverage | Interpretation in paper |
|:---|:---|---:|---:|---:|:---|
| Mistral OCR | Cloud API | 92/107 (86.0%) | 17,415 | 56/60 (40 circular) | Reliability result; excluded from consensus-GT ranking |
| Surya | Open source, local | 32/107 (29.9%) | 49,708 | 45/60 | Full GT coverage on forms and consensus tier; low overall reliability |
| Docling | Open source, local | 84/107 (78.5%) | 7,460 | 57/60 | Structure-preserving, deletion-dominant profile |
| Sarvam OCR | Cloud API | 51/55 GT-backed (92.7%)\* | 7,910 | 51/60 | Competitive accuracy on GT-backed subset; 10-page API cap blocks 4 long PDFs |
| Tesseract | Open source, local CPU | 76/107 (71.0%) | 9,852 | 60/60 | Baseline reference |
| PaddleOCR | Open source, local | 4/107 (3.7%) | — | 3/60 | Partial financial-only run; not ranked overall |

Caption rule:

- Success denominator is the full visible corpus (`n=107`).
- Mean latency is computed over successful visible-corpus runs.
- PaddleOCR is shown for coverage transparency, not as a full-run peer.
- `*` Sarvam was executed on the 55 GT-backed documents only (20 human-verified forms + 35 consensus-GT docs — receipts/equations/financial/multi-column). Four failures were all PDFs exceeding the Sarvam 10-page API cap (`fw2`=11pp, `f1040es`=16pp, `SF-85-questionnaire`=18pp, `sf2809`=18pp).

## Table 3: Human-Verified Forms Results

Unbiased cross-model comparison (`n=20` human-verified forms; `n` reflects each model's successful forms subset).

| Model | n | CER | WER | F1 | Precision |
|:---|---:|---:|---:|---:|---:|
| Docling | 20 | 0.4125 | 0.4980 | 0.8220 | 0.9147 |
| Tesseract | 20 | 0.3607 | 0.4845 | 0.8122 | 0.8353 |
| Surya | 5 | 0.3028 | 0.4483 | 0.7710 | 0.7943 |
| Sarvam OCR | 11 | 0.5018 | 0.9091 | 0.7313 | 0.6959 |
| Mistral OCR | 16 | 0.6791 | 0.7310 | 0.4615 | 0.8918 |

Caption rule:

- Wilcoxon tests at `α=0.05`: Tesseract significantly better than Mistral on forms (`p=0.0092`, `d=0.729`); Docling significantly better than Mistral (`p=0.0076`, `d=0.848`); Tesseract vs Docling not significant at `n=20` (`p=0.498`, `d=0.059`).
- Surya-inclusive forms pairs remain underpowered at `n=5`.

## Table 4: Consensus-GT Aggregate Results

Non-form categories only (`n=40` total consensus-GT docs).
Mistral excluded because of circularity. PaddleOCR excluded because its checked-in run is partial and financial-only.

| Model | n | CER | WER | F1 | Precision | Recall |
|:---|---:|---:|---:|---:|---:|---:|
| Surya | 40 | 0.5673 | 0.7707 | 0.7717 | 0.7275 | 0.8650 |
| Docling | 37 | 0.4417 | 0.5308 | 0.7294 | 0.8090 | 0.7098 |
| Sarvam OCR | 40 | 0.6192 | 0.8080 | 0.7230 | 0.6469 | 0.8849 |
| Tesseract | 40 | 0.5110 | 0.7585 | 0.6221 | 0.5904 | 0.7087 |

Caption rule:

- State explicitly that this is **consensus GT**.
- State explicitly that **Mistral is excluded from ranking**.

## Table 5: Per-Category Results

Token-level F1 by category.

| Model | Forms (`n=20`, human) | Financial (`n=9`, consensus) | Multi-column (`n=11`, consensus) | Equations (`n=10`, consensus) | Receipts (`n=10`, consensus) |
|:---|---:|---:|---:|---:|---:|
| Docling | 0.8220 | 0.7003 | 0.7827 (`n=9`) | 0.7587 | 0.6729 (`n=9`) |
| Tesseract | 0.8122 | 0.6086 | 0.7352 | 0.5957 | 0.5362 |
| Surya | 0.7710 (`n=5`) | 0.8081 | 0.8425 | 0.7624 | 0.6704 |
| Sarvam OCR | 0.7313 (`n=11`) | 0.7619 (`n=9`) | 0.7410 (`n=11`) | 0.7227 (`n=10`) | 0.6684 (`n=10`) |
| Mistral OCR | 0.4615 (`n=16`) | — | — | — | — |
| PaddleOCR | — | 0.6846 (`n=7`) | — | — | — |

Caption rule:

- `—` means not attempted, unsupported, or excluded from ranking.
- Reduced-coverage cells must show the available `n`.

## Table 6: Supported Pairwise Statistical Tests

Wilcoxon signed-rank tests on per-document F1 for the main non-circular Phase 1 comparisons.

| Comparison | n | p-value | Winner | Effect size |
|:---|---:|---:|:---|:---|
| **Forms-only (human GT)** | | | | |
| Tesseract vs Mistral OCR | 16 | 0.0092 | Tesseract | medium (`d=0.729`) |
| Docling vs Mistral OCR | 16 | 0.0076 | Docling | large (`d=0.848`) |
| Tesseract vs Docling | 20 | 0.4980 | Tesseract | negligible (`d=0.059`) |
| **Consensus-GT aggregate** (Mistral excluded) | | | | |
| Tesseract vs Surya | 45 | <0.001 | Surya | large (`d=0.850`) |
| Tesseract vs Docling | 42 | <0.001 | Docling | medium (`d=0.576`) |
| Tesseract vs Sarvam OCR | 27 | 0.1482 | Sarvam OCR | small (`d=0.366`) |
| Surya vs Docling | 42 | 0.0241 | Surya | small (`d=0.314`) |
| Surya vs Sarvam OCR | 27 | 0.0906 | Surya | small (`d=0.448`) |
| Sarvam OCR vs Docling | 25 | 0.5424 | Sarvam OCR | negligible (`d=0.098`) |

Caption rule:

- Mistral excluded from consensus-inclusive rows because of consensus-GT circularity.
- Forms-only rows use the `n=20` human-verified subset; Tesseract and Docling each significantly outperform Mistral, while Tesseract vs Docling is not significant.
- Surya-inclusive forms pairs are not shown because Surya forms coverage is only `n=5`.

## Main Figures

Exactly four figures belong in the conference manuscript:

1. `docs/whitepaper/figures/fig1_f1_comparison.png`
   - Overall token-level F1 comparison
   - Mistral forms-only
   - No Phase 2 diagnostic models
2. `docs/whitepaper/figures/fig3_category_heatmap.png`
   - Category-wise performance split
   - No Mistral consensus-tier ranking
   - No Phase 2 diagnostic models
3. `docs/whitepaper/figures/fig4_error_decomposition.png`
   - Substitution / insertion / deletion stacked bars
   - Phase 1 models only
4. `docs/whitepaper/figures/fig6_success_rates.png`
   - Success-rate comparison on the full visible corpus
   - PaddleOCR omitted because partial run is not comparable
