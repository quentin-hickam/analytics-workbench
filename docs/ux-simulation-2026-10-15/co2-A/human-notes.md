# Friction log: Sam Whitfield (co2-A)

## Pre-session: reading the README
- README is long and dense for a non-coder. Install section is mostly about symlinks, MCP config, VS Code Copilot targets; as Sam I assume install is done.
- The "Use" section is the useful part: start with "Use awb-init to initialize this analytics project. The question is ...".
- Jargon I don't fully follow: "validated Parquet datasets", "DuckDB views", "canonical views", "saved queries", "question ledger", "disposition for each flagged finding", "M365 assembly file". Unclear whether I need Microsoft 365 for the deck (I just want slides).
- Good: README tells me the agent will ask where to keep landed data and releases. I have those folders ready.
- Unclear: how long setup takes, and whether I need to install Python/duckdb myself.

## Turn 1
- Asked: awb-init with my business question, gave data URLs, storage locations, audience, deadline.
- Expect: project initialized, then a scoping interview.
- Happened: project initialized quickly, investigation created ("emissions-accounting-shifts"). Asked for my five questions. No scoping interview yet; it deferred open questions (Q-003 eligibility, Q-004 selection criteria, Q-005 endpoint, Q-006 measures) to a ledger.
- Friction: "Git initialization was denied by filesystem restrictions" and "Connector writes were blocked by the approval configuration" -- as a non-coder I don't know what either means or whether I need to act. No guidance on whether it matters.
- Friction: README said awb-init hands off to awb-scope for an interview; instead it stopped and waited. Fine, but slightly different from what I expected.
- Opened brief.md (agent linked it). Readable and accurate. It derived the meeting date (2026-10-25) from the session date and flagged it as unconfirmed -- careful, good.
- Went well: concise, plain summary; recorded storage paths.

## Turn 2
- Sent: the five questions plus definitions (territorial co2 excl. land use, countries not aggregates, EU-27 only when named, latest-year per variable, Maddison GDP). Asked whether the git/connector issues need action.
- Expect: questions recorded in the ledger, open Q-003/Q-005/Q-006 resolved, then data landing.
- Happened: agent said git/connector issues need no action from me (good, plain answer). Landed full OWID snapshot pinned to a commit, codebook + docs, copied to my storage/landed folder (checked: files there, 14 MB CSV + provenance.json). 17 structural checks passed. Emissions to 2024, GDP to 2022.
- Went well: fast, clear, pinned version. Didn't need to answer a storage question again since I'd given paths up front.
- Mild friction: landed folder nests as landed/data/raw/owid-co2/<date-commit>/ -- deeper than I expected but fine.
- "17 structural checks passed" -- I don't know what they checked; no mention of the countries-vs-aggregates problem yet.

## Turn 3
- Asked: check/clean the data, specifically how it separates countries from aggregates, before answering. (README order: clean then explore.)
- Expect: awb-clean scan, a decision for me about aggregate rule, then explore.
- Happened: cleaning scan found my ISO assumption would drop Kosovo (and Antarctica has an ISO code). Agent added explicit entity classifications, kept all rows. Found consumption data ends 2023 for my four places and corrected its own earlier "2024" claim. Gave 3 decisions in a clear table with recommendations.
- Went well: this is exactly what I wanted -- verified, not assumed; plain-language decisions with a recommended option. Self-correction was candid.
- Friction: quality record link is an absolute file path; fine for me but I didn't open it (a busy user wouldn't). "Q-001..Q-013" quality IDs clash visually with the question ledger's Q-00x IDs from turn 1 (Q-003, Q-004 were questions). Confusing: two different "Q-" numbering systems.
- "54 of 218 lack GDP at the endpoints" -- big number, unclear whether any large emitters are among them. Asked.

## Turn 4
- Decisions: exclude Antarctica; keep outliers with caveats (historical, mostly pre-2000); Libya unranked. Asked about GDP gaps in big emitters and how EU-27/historical territories are handled for cumulative since 1850. Asked to proceed to answering.
- Happened: all five questions answered in one reply with tables, explicit years (2024 / 2005-2022 / 2023 / 1850-2024 / 2010-2024), and caveats. GDP follow-up answered with a ready-made footnote. Historical-entity follow-up answered with sources, honest about what the docs don't specify.
- Numbers look plausible against what I know (US ~24%, EU-27 ~16%, China ~15% cumulative matches OWID's charts). Q3 consumption vs territorial direction matches expectation.
- Went well: very strong turn. Footnote text is donor-ready. Caveat on China's 1850-1906 gap handled correctly (not zero-filled).
- Note: no separate "explore" step happened -- it went straight from clean to answers. README describes awb-explore as a step; I didn't need to ask for it, and nothing seemed lost, but the README flow and actual flow differ.
- Q5 metric choice ("pp/year" over a fixed 14 years = just total pp decline) is a judgment call the agent made without asking; it did state it. Relative decline could rank differently (UK, Greece). Asked for a sensitivity check.
- Link to state.md is to an internal-looking file; didn't open.

## Turn 5
- Accepted Q1-Q4. Asked for Q5 sensitivity with relative decline. Asked awb-status (required checkpoint).
- Happened: sensitivity check showed rankings differ a lot (5 overlap); agent gave side-by-side table, a clear recommendation (pp main chart, relative as callouts), and pointed out the small-base problem (Algeria) and undefined cases. awb-status: concise, plain summary; told me the exact next request phrase.
- Went well: status report readable; suggested next request verbatim is helpful for a first-time user.
- Friction: "17 questions answered, one superseded" -- I asked 5 questions; the ledger count of 17 is confusing without explanation (presumably includes internal scoping/data questions). "10 supported findings" also unexplained vs my 5 questions.
- Friction: README says package is built by Microsoft 365 Copilot's PowerPoint agent. Unclear whether I need M365 Copilot. Asked.

## Turn 6
- Chose pp + relative callouts. Requested awb-package: 8 slides + methodology note, with a rough storyline. Asked whether I need M365 Copilot.
- Happened: explained 17/10 counts (bookkeeping incl. setup decisions) -- fine answer. Confirmed manual slide assembly is possible. Produced headline draft (findings.md) + methodology draft; asks headline approval and a "no separate datasets / full supporting tables" choice.
- FRICTION: the agent linked its own skill instruction file (agent-home/.agents/skills/awb-package/SKILL.md) and quoted it as the reason for the checkpoint. I did not open it -- not something a user should be pointed to. Quoting internal rules ("requires us to wait...") feels like process leaking into the conversation.
- Opened findings.md: just headlines, 6 findings + implications. Readable but several headlines name one country when the slide is a top-10 (China only; US only; Greece only; US 23.6% only). Implications headline is vague/jargony ("can weigh emissions growth, reductions, consumption and historical contributions").
- Opened methodology.md: thorough and accurate but very internal -- r-010/r-011 IDs, settings.toml, run.py, evidence JSON links, "Recorded question" lines repeated verbatim several times, parameter names (baseline_year=2000). Not something I can hand to donors. README called it an "internal methodology reference" -- I needed a donor-readable methodology note. Mismatch between what I asked for and what the package format provides.
- "no separate datasets / full supporting tables" choice: unclear what difference it makes to me; picked none.

## Turn 7
- Requested headline edits, chose no separate datasets, asked for a donor-readable 1-2 page methodology note in addition to (or as a version of) the internal one.
- Happened: full outline expanded with chart specs, footnotes, speaker notes, alt text; donor methodology note (PDF + md) produced; 6 chart CSVs; manual assembly guide. Agent checked my 55% arithmetic and the "most of top ten in Europe" claim (8/10) -- good. It pushed back on my slide-8 wording (data only cover 4 places for consumption) -- correct pushback, stated plainly.
- Links this turn were relative paths (deliveries/...), unlike earlier absolute paths -- had to work out where they were. Inconsistent.
- Donor methodology note: readable, right length, plain language. Exactly what I asked for. Minor: a stray top-level heading mid-document.
- Outline: good, but speaker notes are heavy with caveats and a bit repetitive ("do not establish policy causality" on nearly every slide). Acceptable.
- Problems I found reviewing:
  * Chart CSVs carry floating-point noise (0.42541799999999996, 1.1190380000000004). If I build charts by hand these show up ugly; need rounding.
  * Label inconsistency: CSVs say "European Union (27)", slides say "EU-27".
  * Slide 8 headline now just repeats slides 2-3 and drops the consumption half of my business question.
- The outline is a markdown file; I can't "see" the deck. To check the storyline I had to read a long file. Expected at least a slide-by-slide summary in chat.

## Turn 8
- Requested: round chart data, use EU-27 label consistently, new slide-8 headline that includes consumption shift (limited to the four places). Then asked to release once fixed.
- Happened: corrections applied and release 001 created; copied to my storage/releases folder. Verified: CSVs rounded, EU-27 label used, slide 8 headline covers growth + consumption (agent reworded mine slightly to "raises US and EU-27 footprints" -- more precise, acceptable, though it didn't tell me it changed my wording).
- Went well: release step needed no extra questions since I gave storage path at the start. One-shot "fix and release" worked.
- Friction: release folder nests deeply (releases/emissions-accounting-shifts/donor-roundtable/released/001/); "released" folder repeated under "releases". Link in chat was relative again.
- Friction: no actual deck file -- I still have to build slides by hand from a markdown outline (or have M365 Copilot). README hints at this but a first-time user expecting "a deck package" might expect a .pptx.
- Package includes internal files (methodology.md internal, deck-rules.md, manifest.json, m365.md) alongside donor files; I'd need to know which ones to send to donors. No README in the release saying "send these".

## Overall
- All 5 questions answered with specific numbers and years; status asked once; package drafted, reviewed, corrected, released as 001 and copied. End point reached.
- Biggest positives: verification of aggregate rule (Kosovo), candid self-correction (consumption 2024->2023), sensitivity check, ready-to-use footnotes, donor note quality.
- Biggest frictions: internal jargon/IDs leaking (Q-IDs for both questions and quality, r-IDs, "17 questions/10 findings"); agent linked its SKILL.md; internal-style methodology by default; inconsistent absolute/relative links; no deck file; git/connector errors reported without saying whether they mattered until I asked.

## Turn 9
- Confirmed release, asked which files to send to donors. DONE.
- Final reply: clear one-line split of donor vs internal files. Answered what I asked. Session complete.
