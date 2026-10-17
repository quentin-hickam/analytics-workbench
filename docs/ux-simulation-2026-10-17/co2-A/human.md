# Feedback from Sam Whitfield (research lead, Carbon Ledger Initiative)

## 1. Did I get what I needed?

Yes. All five questions have specific, sourced answers that I'd put in front of donors. A reviewed, 8-slide deck package and a 489-word methods note were released as 001, and I confirmed the copy in my releases folder. It took 9 messages from an empty folder to release.

**Satisfaction: 8/10.** Yes, I'd use it again, especially for the donor-facing "how we know" discipline and the caveats.

## 2. Top pain points, ranked

1. **Default precision was too high for the stated audience** (turn 7, draft review). **Severity: major.** I had said "semi-technical donors, no jargon" in the first message, yet the draft carried figures like "8,645.2 million tonnes" and "23.57%" on slides and in charts. I had to spend a full correction round on rounding. *What would have helped:* rounding to audience-appropriate precision by default, or asking about display precision at the headline checkpoint.
2. **Repetitive, duplicated agent messages** (turns 2, 4, 6). **Severity: minor-to-major.** The four scoping questions appeared twice in one reply, and "foundation is ready" and "all five answers accepted" were each stated twice. The messages felt like the narration stream and the final summary were concatenated. *What would have helped:* one final summary per turn, without progress narration repeated in it.
3. **Agent-internal material shown to me** (turn 2). **Severity: minor.** The agent linked to awb-scope's SKILL.md to justify why it was asking questions. As a user I have no reason to read that. *What would have helped:* just ask the questions; no justification by citing its instructions.
4. **Internal jargon in chat and in the headline preview** (turns 3, 6). **Severity: minor.** "Cohort checks", "shared dataset `owid_co2`", "Primary result: territorial-change. Supporting records: entity-audit", "recording results". *What would have helped:* keep result IDs out of user-facing previews, or put them in a clearly marked footer.
5. **Status report wasn't the "one screen" the README promised** (turn 6). **Severity: minor.** It came back as a prose paragraph with no list of my questions and no "up to five requests you can type next". It was useful, but I couldn't scan it. *What would have helped:* the structured format the README describes.
6. **Headline preview lived in a hidden `.preview` folder** (turn 6). **Severity: minor.** I could open it from the link, but I'd never have found it browsing the folder.
7. **Inconsistent links** (turn 8). **Severity: minor.** Some links were absolute paths and some relative (`deliveries/...`), and the relative ones may not open from my terminal.
8. **The "next: build the PowerPoint" line** (turn 7) was momentarily ambiguous about who does it. The README makes clear it's me, but the agent could have said so.

## 3. The README

- **Good:** the "What to say first" example made my first message easy and complete. Thanks to it, the scoping round was short. The glossary (finding, provisional, ledger, review rule) was useful.
- **Unclear:** the two headline checkpoint modes (preview-and-wait vs draft-then-review) took two reads to understand. A two-line example would help.
- **Unclear:** "Setup and the scoping round bring no data in". I wasn't sure whether giving URLs up front was useful or whether I'd have to repeat them. (It was fine; I just asked "download the data" later.)
- **Missing:** nothing about display precision or number formatting for the audience, or how to set it once (would that be a review rule?).
- **Missing:** whether cleaning happens automatically. The README says "ask 'Was the data cleaned?'", and I did, but it'd be better if the import report just said so.
- **Length:** the README is long, and half of it is install/MCP admin material. It's clearly separated, but a short analyst-only version would be friendlier.
- The "Status" description (one screen, up to five suggested requests) didn't match what I got.

## 4. The agent's communication

- **Scoping interview: excellent.** It asked four questions, each with a recommendation, the alternative, and a concrete example (the 60%→30% coal example made the percentage-point vs proportional choice obvious). It raised the land-use-change question before I did. "Reply 'use these recommendations'" was a nice shortcut.
- **Message length:** answers were long but mostly earned (tables for all five questions). The duplication is what made them feel long.
- **Jargon:** mostly plain in the analysis answers. Workbench-internal vocabulary leaked in at setup and in the preview.
- **Follow-ups:** it responded precisely to my Q2 threshold request (it listed the seven removed countries) and my Q4 denominator question (it cited OWID and drafted caveat wording). That's exactly what a good analyst does.

## 5. Which answers I trusted

- **Trusted:** Q1 (the magnitudes match what I know: the US is the biggest absolute decliner, China dominates growth), Q3 (EU consumption about +33% is consistent with the literature), Q4 (US ~24%, China ~15% of cumulative since 1850 is plausible, and the missing early China/India years are negligible in volume and were disclosed honestly rather than zero-filled), and Q5 (Greece and the UK leading on coal share is credible).
- **Initially did not trust:** Q2 with "any decline". Australia at −0.3% and Mexico at −2.1% are not "cuts" I'd present to donors. Once the ≥5% threshold went in (38 of 164), I trusted it. The agent should have offered a materiality threshold itself. The README says thresholds the brief leaves open are proposed up front, but this one wasn't.
- **Builds trust:** the Kosovo catch (ISO-code filter would wrongly drop it), the EU-27 member-sum check, the explicit exclusion counts, and the statement of which year each answer used.

## 6. Deck package review and release

- The headline preview was the right checkpoint: I fixed two headlines and a chart choice (levels → CO2% vs GDP%) before any full slides were written. All my edits landed exactly.
- The draft was high quality: caveats on the slides they qualify, plain-words definitions of "territorial" and "consumption", a sensible appendix. START-HERE clearly separates what to send from what to attach and what to keep internal.
- The methods note was right-sized (489 words, one page) and in donor terms.
- The correction round showed the changed slides inline, which was convenient. I asked for one-off edits, not standing rules, and it respected that.
- Release was smooth: no unnecessary questions, the full path reported, caveats listed, and the files verified in my folder.
- Still a gap for me: no .pptx. I have to build it by hand or with Copilot. The README is upfront about this, but it's extra work in a 10-day window.

## 7. Wasted turns or time

- One full turn on rounding (avoidable with audience-appropriate defaults).
- One turn on the Q2 threshold (arguably avoidable if the agent had proposed a materiality threshold during scoping), though it was a good conversation to have.
- Reading time lost to duplicated text in roughly three replies.
- Otherwise efficient: 9 exchanges is at the low end of what the README predicts.

## 8. What worked well

- The first-message template, plus a four-question scoping round with recommendations.
- Data landing: checksums, provenance, my landed folder populated, and coverage years reported up front.
- Entity handling (Kosovo, the 35 excluded aggregates explained in plain words).
- Every answer stated its year, cohort size, and exclusions.
- Honest caveats (missing early records not zero-filled; aviation/shipping in the World denominator).
- Preview-and-wait headline checkpoint.
- A clean, verified release to my storage folder.
