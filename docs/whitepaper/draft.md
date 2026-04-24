# OCR Whitepaper Executive Summary

Derived from the conference manuscript in `docs/whitepaper/latex/main.tex`.
All numbers in this summary are sourced from the regenerated artifacts in
`results/expanded_gt_metrics/` and the visible-input dataset manifest in
`test-dataset/manifest.json`.

## Status

- Submission narrative is now keyed to the locked current corpus, not the older conflicting corpus-count drafts.
- The authoritative corpus contains **107 visible OCR inputs**.
- Accuracy evaluation is limited to **60 GT-evaluable documents**:
  - **20 human-verified forms** (`02_complex_tables/forms`)
  - **40 consensus-GT non-form documents** across financial, multi-column, equations, and receipts
- The conference package is constrained to **6 tables** and **4 figures** in the main manuscript.

## Evidence Lock

The repository previously contained conflicting corpus counts because different paths were counting hidden AppleDouble files, support artifacts, and visible OCR inputs differently. The current pipeline now uses one shared inventory rule for:

- runtime document enumeration
- dataset manifest generation
- corpus summary generation
- figure generation

Under that rule, the current reproducible corpus is:

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

## Main Findings

- **Tesseract and Docling** co-lead on the unbiased forms tier (`n=20`):
  - Docling forms F1 `0.8220` (CER `0.4125`); Tesseract forms F1 `0.8122` (CER `0.3607`)
  - both significantly better than Mistral on forms (Tesseract `p=0.0092`, `d=0.729`; Docling `p=0.0076`, `d=0.848`)
  - Tesseract vs Docling is not significant at `n=20` (`p=0.498`, `d=0.059`)
- **Surya** posts the lowest forms CER (`0.3028`) but only on `n=5` successful forms, and leads the consensus tier:
  - consensus aggregate F1 `0.7717`, recall `0.8650`
  - visible-corpus success in the current re-execution batch is only `32/107` (29.9%)
- **Mistral OCR** is the most reliable operational model:
  - `92/107` (86.0%) successful visible-corpus runs
  - forms F1 drops sharply at expanded `n=16` to `0.4615`; Mistral is **not** supported as an unbiased "best overall" choice
  - excluded from consensus-GT ranking due to reference-creation circularity
- **Docling** additionally serves as the structure-preserving option:
  - consensus-GT aggregate F1 `0.7294`
  - deletion-dominant profile indicates conservative omission rather than hallucination
- **Sarvam OCR** is the low-latency option for structured workloads:
  - mean latency `4,688 ms`
  - current re-execution produced `0/107` successful visible-corpus outputs; historical structured-doc results still inform recommendations
  - fails on receipts and most equations, so it is not a safe default
- **Tesseract** is a baseline reference that now leads alongside Docling on forms:
  - `76/107` (71.0%) visible-corpus success
  - full failure on handwritten Devanagari crops
- **PaddleOCR** remains partial:
  - only `3` GT-scored financial documents in the current batch
  - not used for overall ranking

## Recommendation Positions

The paper now resolves to five evidence-backed positions instead of a single-winner narrative:

1. **Tesseract and Docling** co-lead unbiased forms accuracy (`n=20`); both significantly better than Mistral.
2. **Surya** for strongest consensus-tier aggregate F1 among non-circular models, and the lowest forms CER on its `n=5` coverage.
3. **Mistral OCR** for cross-category operational reliability, not for unbiased "best overall" accuracy.
4. **Docling** additionally for structure-preserving extraction with conservative errors.
5. **Sarvam OCR** for latency-sensitive structured-document flows, with clear category caveats.

## Claim Rules Used in the Paper

- Forms (`n=20`) are the **only unbiased cross-model accuracy comparison**.
- Consensus-GT categories are always labeled **consensus GT**.
- **Mistral is excluded** anywhere consensus-GT cross-model ranking would be circular.
- Forms-only Wilcoxon significance is now established: Tesseract and Docling each significantly better than Mistral at `α=0.05`.
- Phase 2 and diagnostic models are not used in headline recommendations.

## Main Manuscript Package

The conference manuscript includes exactly:

- **6 tables**
  - dataset and GT coverage
  - model set and run coverage
  - human-verified forms results
  - consensus-GT aggregate results
  - per-category results
  - supported pairwise statistical tests
- **4 figures**
  - overall model comparison using F1
  - category-wise performance split
  - error decomposition
  - full-corpus success rates

## Current Risks / Limits

- Human-verified GT is limited to `n=20` forms; all other categories rely on consensus GT or have no GT.
- The handwritten and Hindi categories still contribute to reliability analysis, not comparative accuracy analysis.
- Consensus GT is useful for directional comparison among non-Mistral models, but it is not a substitute for broader human-verified annotation.
- PaddleOCR and the Phase 2 wrappers still need follow-up work before they belong in a broader comparative submission.
