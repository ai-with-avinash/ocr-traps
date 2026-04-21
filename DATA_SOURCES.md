# Data sources (added for expanded human-GT set)

This file records provenance for **additional visible OCR inputs** added to `test-dataset/` to expand the *human-verified* ground-truth tier for the ICDAR submission.

## 2026-04-21 additions (15 visible inputs)

### U.S. Government PDFs (13 files)

- **License/terms**: U.S. Government works are generally public domain under **17 U.S.C. §105**. These files were downloaded from official U.S. government websites and mirrors.
- **Storage location**: `test-dataset/02_complex_tables/forms/`
- **Filename convention**: `usgov__<original_filename>.pdf`

| Local file | Source URL | Notes |
|---|---|---|
| `usgov__SF-85-questionnaire.pdf` | `https://www.opm.gov/forms/pdf_fill/sf85.pdf` | OPM Standard Form 85 |
| `usgov__SF-181-ethnicity.pdf` | `https://www.opm.gov/forms/pdf_fill/sf181.pdf` | OPM Standard Form 181 |
| `usgov__IRS-W-9.pdf` | `https://www.irs.gov/pub/irs-pdf/fw9.pdf` | IRS Form W-9 |
| `usgov__IRS-W-4.pdf` | `https://www.irs.gov/pub/irs-pdf/fw4.pdf` | IRS Form W-4 |
| `usgov__IRS-1040.pdf` | `https://www.irs.gov/pub/irs-pdf/f1040.pdf` | IRS Form 1040 |
| `usgov__fss4.pdf` | `https://www.irs.gov/pub/irs-pdf/fss4.pdf` | IRS Form SS-4 |
| `usgov__f941.pdf` | `https://www.irs.gov/pub/irs-pdf/f941.pdf` | IRS Form 941 |
| `usgov__fw2.pdf` | `https://www.irs.gov/pub/irs-pdf/fw2.pdf` | IRS Form W-2 |
| `usgov__f4506t.pdf` | `https://www.irs.gov/pub/irs-pdf/f4506t.pdf` | IRS Form 4506-T |
| `usgov__f1040es.pdf` | `https://www.irs.gov/pub/irs-pdf/f1040es.pdf` | IRS Form 1040-ES |
| `usgov__f9465.pdf` | `https://www.irs.gov/pub/irs-pdf/f9465.pdf` | IRS Form 9465 |
| `usgov__sf144.pdf` | `https://www.opm.gov/forms/pdf_fill/sf144.pdf` | OPM Standard Form 144 |
| `usgov__sf1152.pdf` | `https://www.opm.gov/forms/pdf_fill/sf1152.pdf` | OPM Standard Form 1152 |
| `usgov__sf2809.pdf` | `https://www.opm.gov/forms/pdf_fill/sf2809.pdf` | OPM Standard Form 2809 |
| `usgov__sf3104.pdf` | `https://www.opm.gov/forms/pdf_fill/sf3104.pdf` | OPM Standard Form 3104 |

### TuluDocuments scanned pages (2 files)

- **Dataset**: TuluDocuments (scanned pages of Tulu books + ground truth)
- **License**: Apache-2.0 (license text: `https://raw.githubusercontent.com/MILE-IISc/TuluDocuments/master/LICENSE`)
- **Repo**: `https://github.com/MILE-IISc/TuluDocuments`
- **Storage location**: `test-dataset/02_complex_tables/multi_column/`
- **Selection rule**: first 2 images in lexicographic order from `images/`
- **Filename convention**: `tulu__<original_filename>`

| Local file | Upstream file | Notes |
|---|---|---|
| `tulu__B01_P12.tif` | `images/B01_P12.tif` | Selected by lexicographic rule |
| `tulu__B01_P13.tif` | `images/B01_P13.tif` | Selected by lexicographic rule |

