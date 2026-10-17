# Friction log: Sam Whitfield, CO2 donor roundtable

## Turn 1 (first message)
- Read the README first. Asked: awb-init setup with the business question, five questions, audience, length, methods note, data URLs, landed and release folders, preview-and-wait headline mode.
- Expected: setup, then a scoping round of up to four questions.
- README notes: The "What to say first" example made writing the opening message easy. The README is long and the Install/MCP half isn't for me; it's clearly marked, which helped. Unclear before starting: do I have to ask separately for the download ("Setup and the scoping round bring no data in")? I put the URLs in now anyway. "Provisional", "question ledger", and "review rule" are jargon, but the glossary covers them. The two checkpoint modes (preview-and-wait vs draft-then-review) took two reads to understand.

## Turn 2 (scoping answers)
- Agent set up the project and asked 4 scoping questions, each with a recommendation and alternatives. That matched what the README promised. The questions were good; the land-use and percentage-point vs proportional ones are real choices I'd have had to make anyway.
- Friction: the reply repeated itself. The four questions appear twice, and the "foundation is ready" paragraph also appears twice, so it's noisy to read. It also linked me to awb-scope's SKILL.md as the reason it was asking, which is an agent instruction file I have no reason to read; I ignored it. Jargon: "awb-scope's instructions require asking open decisions 'Before writing the records'" means nothing to me.
- Q3 framing: I want each answer to say which year it used. A common year per question works for that.
- Accepted all four recommendations and stated there are no program restrictions.

## Turn 3 (data in)
- Asked for the download and import. It worked: the originals landed in my storage folder with a provenance file and README, checksums matched, and 16 checks passed. Giving coverage years up front (2024 for CO2, 2022 for GDP, 2023 for per-capita) was useful.
- Minor: the landed path nests as storage/landed/data/raw/owid-co2/<date>/. It mirrors the project layout, which is a bit deep but fine.
- "Cohort checks" and "shared dataset owid_co2" are jargon; I don't need the table name.
- Unclear: was the data cleaned or explored? The main issue I know of is aggregates mixed in with countries. I asked about it explicitly instead of assuming.
- Next: asked it to handle aggregates and then answer all five.

## Turn 4 (aggregates, cleaning, five answers)
- Very good turn. It caught that Kosovo has no ISO code and kept it, which I wouldn't have known (my ISO assumption was nearly right but not quite). It listed the excluded entity types in plain words. Cleaning pass: no fixes needed.
- All five answers came with tables, years, and exclusion counts. The numbers look plausible against what I know of the literature (US is the biggest decliner, China roughly 15% of cumulative, EU consumption about +30%).
- My concerns: in Q2, several "reducers" barely moved (Australia −0.3%, Mexico −2.1%, Poland −2.4%). Calling that decoupling in front of donors is weak, so I asked for a materiality threshold sensitivity. Q4: does the World denominator include international aviation/shipping? I asked.
- Still says "provisional"; per the README, approval comes at the headline checkpoint.
- One long message with mixed narration ("I'm using awb-clean...") followed by a duplicate summary. The repetition persists but is less bad this time.

## Turn 5 (Q2 threshold, Q4 denominator)
- Clean, quick answers. 38 of 45 at the ≥5% threshold, the seven dropped countries listed, and an OWID source cited for aviation/shipping. The proposed caveat wording is donor-friendly. This is exactly what I wanted.
- Accepted Q2 (38 as headline, with 45 mentioned in notes) and Q4. Now asking for awb-status as the README suggests, then headlines.

## Turn 6 (status + headline preview)
- Asked for status and package headlines in one message. Status came back as a short prose paragraph rather than the "one screen" with suggested requests the README described, but it covered the essentials: results current, caveats, storage reachable, no draft yet, uncommitted.
- The headline preview was good. I opened the preview file it linked; it's readable, with a chart plan and caveats per slide. Lines like "Primary result: territorial-change. Supporting records: entity-audit" are internal jargon, but tolerable. The file sits in a hidden `.preview` folder, which is odd for something I'm meant to review.
- The summary repeated itself again ("All five analytical answers are now accepted" appears twice).
- My edits: the Slide 6 headline is clunky ("Among these four..."), so I proposed one with a number. The Slide 5 headline should mention China/India going down. The Slide 4 chart shows 2022 levels, which doesn't show the cut, so I asked for a CO2 % change vs GDP % change chart. "Territorial" needs a plain-words definition the first time it's used.
- Odd: "ten slides including the appendix divider" when I asked for about 8. It's explained, and fine.

## Turn 7 (draft review)
- Full draft came back with links to findings.md, methodology-note.md, and START-HERE.md. All my headline edits went in, the definitions are there, and the methods note is 489 words. Quality is high, and the caveats sit where they belong.
- START-HERE is clear about what to send and what to attach. I don't have a Copilot license confirmed, so I may build by hand; that's fine.
- The agent's "next: build the PowerPoint" line is a bit confusing: is that my job or its job? Per the README, it's mine.
- My corrections: too much precision for donors (8,645.2 million tonnes → ~8.6 billion; whole numbers in chart 1; 23.57% → 23.6%). Two headlines end with stray periods. I asked for these as one-off edits, not review rules.
- The findings.md format (Chart spec blocks with Interval: none etc.) is builder-oriented but readable.

## Turn 8 (corrections applied)
- All the edits came back exactly as asked, and the changed slides were shown inline in chat, which was convenient. Checks passed.
- Minor: the links this time were relative paths (deliveries/...), where earlier ones were absolute, so they may not open from my terminal. It's inconsistent.
- I didn't reopen the files because the inline excerpt was enough. Marking delivered now.

## Turn 9 (release)
- Release 001 frozen and copied. I checked the releases folder and all the files are there (findings, methods note, 5 charts, START-HERE, rules, assembly, manifest). The full path and caveats were reported as the README promised. No release questions were needed.
- The agent never suggested a commit (the README says it suggests one at most once per session; status mentioned "uncommitted"). Fine.

## Overall
- 9 messages from an empty folder to release 001, consistent with the README's 6–11 range.
- Went well: scoping questions with recommendations; the Kosovo/ISO catch; threshold sensitivity on request; headline preview; caveats placed on slides; a short methods note at the right length; a clean release.
- Friction: repetitive/duplicated agent summaries (turns 2, 4, 6); a link to an agent SKILL.md shown to me; internal jargon (cohort checks, result IDs, "records") leaking into chat and the preview; the preview is in a hidden `.preview` folder; inconsistent absolute vs relative links; the status report was prose rather than the one-screen format with suggested next requests; the default precision was too high for a donor audience (I had to ask for rounding).
