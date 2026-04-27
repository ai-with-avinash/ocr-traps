# Reply Template Library

Four labeled templates for the most common inbound conversation classes. Use these as starting points, then trim further before sending. Replace bracketed placeholders before send.

---

## Class 1 — Hostile / dismissive critique

**Trigger:** A reader (Reddit / HN / LinkedIn / email) frames the work as already-known, trivial, methodologically broken, or self-promotional. Common forms include: "this is just train/test contamination," "five language packs is obviously slower, why is this a finding," "you didn't run [X] OCR system so this means nothing," "this reads like marketing."

**Template:**

> You are right that [the underlying principle / the obvious-in-hindsight result] is well-established. The contribution this work makes is not the principle but [the specific empirical magnitude on a deployed practitioner corpus / the protocol rule that prevents the trap from recurring / the mechanism by which the antipattern reappears in pipelines that do no model training]. Concretely: [one number, one source artifact, one regenerable command]. Full discussion in [link to the relevant Medium section or paper section]. If you spot a fourth trap or a stronger reframing of any of these three, I would genuinely like to hear it — [GitHub issues link].

**Pitfalls:**
- Concede the principle in the first sentence. Never argue back. The reader has already decided their framing is right; the only path forward is to narrow your claim, not defend a broader one.
- Do not link three sources when one will do. Hostile commenters do not click multiple links.
- The Kornai reply (commit `8833b78`) is the canonical worked example for this class.

---

## Class 2 — Technical clarification

**Trigger:** A reader asks a specific technical question: which Wilcoxon variant, what was the test power at n=20, why was Mistral excluded from category X but not Y, what were the per-document confidence bins, how was CER normalized.

**Template:**

> Short answer: [the number or fact]. Source artifact: [`results/expanded_gt_metrics/<file>.json`] in the repo. To regenerate from scratch: `python tools/recompute_metrics.py` against the locked corpus inventory. If you reproduce a different number please open an issue with the command you ran — that is exactly the kind of audit this benchmark exists to support.

**Pitfalls:**
- Never bluff a number. If you do not know it offhand, say "let me check the artifact and reply within 24 hours" and actually do.
- Always link the regenerable command. The work's credibility comes from reproducibility, not authority.
- Resist the urge to re-explain the framing. If the asker is on a technical question they already accepted the framing.

---

## Class 3 — Endorsement offer / lead

**Trigger:** A reader either offers an arXiv endorsement directly, or names a colleague who might be willing. Also covers conference / journal program-committee invitations once the arXiv preprint is live.

**Template:**

> Thank you — that would unblock the preprint. Endorsement code: **RDOS9I** at https://arxiv.org/auth/endorse?x=RDOS9I. Submission category is cs.DL (primary) with cs.CV and cs.IR as cross-lists, license CC BY 4.0. Manuscript PDF attached for your reference (also at the GitHub repo and at Zenodo doi:10.5281/zenodo.19741773). Happy to answer any questions before you decide.

**Pitfalls:**
- Reply within 4 hours. Endorsement enthusiasm decays fast — same-day replies convert at roughly 3x the rate of next-day.
- Always attach the PDF (`~/Desktop/ocr-traps-seethalam-2026.pdf`). Asking the endorser to download is friction.
- If the reader names a colleague rather than offering directly, ask for an introduction email rather than a name. A warm intro converts at much higher rate than a cold ask referencing the third party.

---

## Class 4 — Journalist / community-organizer outreach

**Trigger:** A newsletter writer, podcast host, conference organizer, university seminar organizer, or industry publication invites the work to be featured. Also covers vendor representatives (Mistral, Sarvam, etc.) reaching out about the benchmark.

**Template:**

> Thank you — I would be glad to talk. Quick context: this is a single-author practitioner benchmark, not academic-conference work, so the natural fit is [practitioner-facing newsletter / vendor-decision podcast / industry meetup]. The arXiv preprint is currently awaiting endorsement (status update once live). If a written piece would be useful, the Medium write-up at https://medium.com/@buildwithavinashai/3-ocr-traps-4cfd1ef0ea6b is licensed CC BY 4.0 and can be republished with attribution. For talks, comfortable date window is [your dates]. Press materials: GitHub repo + Zenodo concept DOI (no formal press kit yet — TODO).

**Pitfalls:**
- Do not commit to academic-conference talks before the arXiv preprint is live. The credibility math changes once the preprint exists.
- For vendor-rep outreach (Mistral, Sarvam): be polite but never agree to remove or soften critiques. The benchmark's value is its honesty.
- TODO: build a one-page press kit (~/Desktop/ocr-traps-press-kit.pdf) once the arXiv preprint lands. Not blocking yet.

---

## Cross-cutting tone rules

- No AI-sounding phrasing. Never start with "I appreciate your thoughtful engagement" or similar. Start with the substance.
- No unnecessary apologies. "Sorry for the delay" is a tax on your credibility — only apologize for actual errors.
- Reply length should approximately match the question length. A one-line question gets a one-line answer.
- Sign with first name only on informal channels (Reddit, HN, LinkedIn DMs). Use full name + ORCID + GitHub on email.
