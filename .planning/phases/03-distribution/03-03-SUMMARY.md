# Phase 03 Plan 03: Engagement Metrics + Reply Library Summary

**Engagement tracker initialized with day-zero baseline + day-4/7/10 escalation triggers; reply-template library covers four inbound conversation classes with tone pitfalls.**

## Accomplishments

- Daily-snapshot metrics tracker created at `.planning/phases/03-distribution/metrics/engagement-tracker.md`
  - 8 channels documented with read-source instructions
  - Pre-filled rows for 2026-04-26 (LinkedIn post day, baseline) and 2026-04-27 (Kornai reply, second-wave endorsement send)
  - 5 escalation triggers wired to specific dates and counter thresholds
- Reply-template library created at `.planning/phases/03-distribution/templates/reply-library.md`
  - Class 1: Hostile / dismissive critique (canonical worked example: Kornai reply, commit 8833b78)
  - Class 2: Technical clarification (always-link-the-regenerable-command pattern)
  - Class 3: Endorsement offer / lead (4-hour reply window, PDF-attach default)
  - Class 4: Journalist / community-organizer outreach (no academic-conference commits pre-arXiv)
- Cross-cutting tone rules block at file end (no AI phrasing, no unnecessary apologies, length match)

## Files Created/Modified

- `.planning/phases/03-distribution/metrics/engagement-tracker.md` — daily metrics + escalation triggers
- `.planning/phases/03-distribution/templates/reply-library.md` — four inbound-class reply templates

## Decisions Made

- **Tracker columns chose conversion metrics over impression metrics.** Medium reads, GitHub stars, Zenodo downloads, endorser replies are real signal. LinkedIn impressions are kept for completeness but flagged as vanity in the pitfalls section.
- **Escalation triggers anchored to specific dates** (2026-04-30 / 2026-05-03 / 2026-05-06) rather than "day N" relative dates, so the trigger fires unambiguously without recomputing day count from a moving anchor.
- **Reply-library templates keep the train-on-test reframing language** worked out in the Kornai exchange as the canonical Class 1 pattern. Future hostile critiques on the same axis can reuse it nearly verbatim.

## Issues Encountered

None.

## Next Step

Phase 03 status:
- ✅ 03-03 (this plan) — engagement infra complete
- ⏳ 03-01 — Reddit submission cluster (auto tasks ready to execute, manual posting blocked on weekday-AM window)
- ⏳ 03-02 — HN submission (auto tasks ready, manual posting blocked on Tue/Wed AM PT window)

Both 03-01 and 03-02 auto tasks (drafting) can run any time. Manual posting tasks should fire at the day-4 escalation trigger (2026-04-30) if endorsement replies remain at 0-1.
