# OCR-Traps Project Roadmap

> Minimal roadmap stub. BRIEF skipped (work was done ad-hoc before planning skill adoption — this scaffolding captures forward-looking phases only). Add BRIEF retroactively if a milestone summary is needed later.

## Project identity

**ocr-traps** — Practitioner OCR benchmark + companion paper.
- Repo: https://github.com/ai-with-avinash/ocr-traps
- Concept DOI: https://doi.org/10.5281/zenodo.19741773
- Paper: "A Practitioner's OCR Benchmark: Three Traps Real Evaluations Hit"

## Shipped milestones (informal)

- v1.0.0 — Initial Zenodo release
- v1.0.1 — DOI wiring fix
- v1.0.2 — Concept DOI swap
- v1.0.3 — Finding 1 reframe (GT-construction leakage, post-Kornai feedback)

## Phase scope (forward-looking)

| Phase | Name | Status | Blocks |
|-------|------|--------|--------|
| 01 | Phase 1 benchmark + paper | shipped (pre-planning-skill) | — |
| 02 | arXiv submission completion | in flight | endorsement |
| **03** | **Distribution amplification** | **active** | LinkedIn engagement window |
| 04 | Paper v2 (post-review) | queued | arXiv live |
| 05 | Phase 2 model benchmarking (DeepSeek, Qwen-VL, OlmOCR, GOT-OCR) | queued | GPU access |
| 06 | Framework hardening (CI, ruff/pylint pass, type hints, tests) | queued | none (parallel-safe) |

## Phase 03 scope (active)

Goal: maximize practitioner reach for the published paper + Medium piece via Reddit, HN, and engagement infrastructure. No new technical content — purely distribution + reply protocol.

Plans:
- `03-01-PLAN.md` — Reddit submission cluster (r/MachineLearning + r/datascience drafts + posting protocol)
- `03-02-PLAN.md` — Hacker News submission (title + first comment + timing)
- `03-03-PLAN.md` — Engagement metrics + reply protocol library

Total: 7 atomic tasks across 3 independently committable plans.

## Conventions

- Plan numbering: `{phase}-{plan}-PLAN.md` (e.g., `03-01-PLAN.md`)
- SUMMARY.md sibling marks plan complete
- Phase directory: `.planning/phases/{XX}-{name}/`
- Deviation rules: auto-fix bugs/blockers/security gaps, log enhancements to `ISSUES.md`, ask only on architectural changes
