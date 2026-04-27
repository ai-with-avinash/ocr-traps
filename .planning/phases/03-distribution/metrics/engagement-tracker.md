# Engagement Metrics Tracker

Daily snapshot of distribution-channel metrics. Update at end of day (or start of next morning) by reading each source listed below and filling in the row for that date.

## Data sources

| Channel | Where to read | Notes |
|---------|---------------|-------|
| Medium views/reads/claps | medium.com → Stories → 3 OCR Traps → Stats tab | "Reads" = full-article reads; "views" includes drive-by impressions. Use reads as the conversion-quality metric. |
| GitHub stars/forks | https://github.com/ai-with-avinash/ocr-traps (top-right counters) | Stars are the most-cited proxy for practitioner-credible interest. |
| Zenodo views/downloads | https://zenodo.org/records/19741773 → Statistics tab | Concept-DOI page aggregates across versions; that is the canonical citation count. |
| LinkedIn impressions/reactions | LinkedIn post analytics modal (View analytics on the post) | Cannot be read programmatically. User must open and copy. |
| Reddit r/ML score | Reddit post URL after 03-01 ships | Score = upvotes − downvotes shown on post page. |
| Reddit r/datascience score | Reddit post URL after 03-01 ships | Same as above. |
| Hacker News points | Submission page on news.ycombinator.com after 03-02 ships | Points + comment count. Front-page status (yes/no) noted in `notes`. |
| Endorser replies | sreethalam.avinash@gmail.com | Count any reply, even decline (Kornai counted as 1). |

## Escalation triggers

These are conditions that flip a state — when triggered, take the named action without re-deliberating.

| Trigger | Action |
|---------|--------|
| Day 4 from 2026-04-26 (i.e. 2026-04-30) and `endorser_replies` < 2 | Send 1-line nudge to first-wave 5 (Peroni, Shotton, Van Durme, Khashabi, Massari). Post Reddit + HN drafts (execute Plan 03-01 + 03-02). |
| Day 7 from 2026-04-26 (i.e. 2026-05-03) and `endorser_replies` < 1 actual endorsement | Twitter/X public cs.DL endorsement ask. Email moderation@arxiv.org with PDF + Kornai reply attached as "senior researcher engaged" proof. |
| Day 10 from 2026-04-26 (i.e. 2026-05-06) and still no endorsement | Drop arXiv-path. Treat Medium + GitHub + Zenodo as canonical citation surface. Begin Phase 04 (Paper v2 prep) without arXiv preprint. |
| `github_stars` < 30 by 2026-05-03 | Write a Trap-2-only standalone Medium follow-up (calibration deep-dive with the Pearson-r=0.918 figure as the hook). Long-tail extension. |
| `github_stars` > 200 in any rolling 48h window | Pin a "for endorsement / collaboration" GitHub issue and amplify on LinkedIn. Inbound momentum signal. |
| Hostile comment thread on Reddit/HN with vote ratio < 40% | Open a `docs/known-critiques.md` file, log the critique with the verbatim quote + a 2-sentence rebuttal. Do not edit the post. |

## Daily snapshot

Add one row per day. Leave a column blank if not yet read or not yet applicable.

| Date | medium_views | medium_reads | medium_claps | github_stars | github_forks | zenodo_views | zenodo_downloads | linkedin_impressions | linkedin_reactions | reddit_ml_score | reddit_ds_score | hn_points | endorser_replies | notes |
|------|-------------:|-------------:|-------------:|-------------:|-------------:|-------------:|-----------------:|---------------------:|-------------------:|----------------:|----------------:|----------:|-----------------:|-------|
| 2026-04-26 | manual | manual | manual | manual | manual | manual | manual | manual | manual | n/a | n/a | n/a | 0 | LinkedIn post live; Medium published; Zenodo v1.0.3 archived; first-wave 5 endorsement emails sent |
| 2026-04-27 | | | | | | | | | | n/a | n/a | n/a | 1 | Kornai replied (declined endorsement, gave Trap 1 framing critique → patched in 8833b78); second-wave 9 endorsement emails sent; LinkedIn first-comment CTA added |
| 2026-04-28 | | | | | | | | | | n/a | n/a | n/a | | |
| 2026-04-29 | | | | | | | | | | | | | | |
| 2026-04-30 | | | | | | | | | | | | | | DAY-4 TRIGGER CHECK — see Escalation triggers |
| 2026-05-01 | | | | | | | | | | | | | | |
| 2026-05-02 | | | | | | | | | | | | | | |
| 2026-05-03 | | | | | | | | | | | | | | DAY-7 TRIGGER CHECK |
| 2026-05-06 | | | | | | | | | | | | | | DAY-10 TRIGGER CHECK |

## Pitfalls to avoid

- Do not track LinkedIn impressions as a primary success metric. Impressions are vanity; conversions to GitHub stars / Medium reads are the real signal.
- Do not refresh stats more than once per day. The platform counters update on a delay and excessive checking creates anxiety without information gain.
- Do not edit historical rows. If you misread a number, add a `notes` correction in the same row. Trustworthy data is more useful than tidy data.
