# Contributing to ocr-traps

Thanks for your interest. The repository is the reference implementation behind the companion paper, so contributions should preserve the evidence chain between source code, result artifacts, and paper claims.

## Ground rules

- **Never break reproducibility.** Changes that alter benchmark numbers must regenerate `results/expanded_gt_metrics/*.json` and `test-dataset/manifest.json` in the same commit.
- **Never commit secrets.** API keys live in `.env` (gitignored). If you accidentally commit one, rotate it immediately and file an issue.
- **Never commit the virtualenv.** Use `uv sync` to rebuild it locally; `.venv/` and `venv/` are gitignored.
- **Preserve the locked corpus contract.** Changes to `test-dataset/` must update `test-dataset/manifest.json` atomically.

## Developer setup

```bash
git clone https://github.com/ai-with-avinash/ocr-traps.git
cd ocr-traps
uv venv --python 3.12
source .venv/bin/activate
uv sync --group dev
cp .env.example .env        # add your API keys
```

## Before opening a PR

1. `ruff check .`
2. `pylint models utils cli tools`
3. `pytest`
4. If touching the metrics pipeline, rerun `python tools/recompute_metrics.py` and commit the regenerated artifacts under `results/expanded_gt_metrics/`.
5. If touching the paper, rebuild `docs/whitepaper/latex/main.pdf` and verify no `Warning`/`Error` lines in `main.log`.

## Adding a new OCR model

1. Create `models/<your_model>.py` inheriting `BaseOCRModel`.
2. Implement `_ocr_impl(image_path: str) -> OCRResult`.
3. Decorate with `@register_model` — the registry is self-wiring.
4. Add non-secret config to `configs/config.yaml`.
5. Add any API-key reference to `.env.example` (empty value).
6. Run `python cli/run_single.py --model <your_model> --input test-dataset/02_complex_tables/forms/0012199830.png` to smoke-test.
7. Run `python cli/run_model.py --model <your_model>` to evaluate on the full corpus.

## Reporting evaluation bugs

Include:

- Exact command used
- Model(s) affected
- Relevant excerpt from `results/<run>/...`
- Python version and `uv.lock` hash if possible

## Protocol rules (non-negotiable)

- Claims in the paper must trace back to `results/expanded_gt_metrics/*.json`.
- A model whose output seeded consensus GT is excluded from cross-model ranking on that tier.
- Accuracy metrics are only reported on GT-evaluable documents.
- Success rate uses the full 107-document visible corpus as the denominator.
