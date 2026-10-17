# Proposed issues from the 2026-10-17 re-run

This is the finding list for the maintainer to read before anything is filed. **Nothing is filed.** It groups the confirmed findings in the [comparison report](README.md) into PR-sized issues.

- **Included:** only findings that both skeptics confirmed as product defects (47). Where a skeptic narrowed a finding, the problem is stated in its narrower form, and a lower suggested severity is noted.
- **Listed separately, not proposed:** the 17 contested findings, at the end under [Contested findings](#contested-findings), with what each skeptic said.
- **Left out:** the 4 rejected findings and the 11 harness findings. They are summarized in the report.

**Paths.** Evidence paths are written `SIMS/<run>/...`, where `SIMS` is the simulation folder that holds `grade/report/`. Release paths such as `awb-package/references/review.md:43` are relative to the release root (`SIMS/release/analytics-workbench-skills/`, built from `main` at `1677d19`). `README.md:NN` refers to the release README. Line numbers marked "about" come from the skeptics' reading of the code and may be off by a few lines.

**IDs.** `C-NN` is a consolidated finding in this study (`consolidated` in `data.json`). These numbers collide with Oct 16 IDs of other meanings, so Oct 16 findings are written "Oct 16 C-NN". Per-run IDs such as `taxi-B-04` are the `member_ids` in `data.json`. Skeptics found that several of those do not match the per-run `findings.json` files, so each issue cites the files and logs directly.

## Summary

| # | Proposed issue | Severity | Closes | Runs |
|---|---|---|---|---|
| 1 | Review brief: check meaning, allow honest approximate wording, scope the coverage and style rules | major | C-03, C-06, C-12, C-50, C-51 | 6/6 |
| 2 | Review stop rules, rule workflow and receipt checks | major | C-04, C-24, C-72 | 5/6 |
| 3 | Conversation: untested explanations, coded values, plain words, complete first answers | major | C-05, C-09, C-13, C-22, C-33, C-34, C-48 | 6/6 |
| 4 | awb-package instructions, preview checkpoint and slide linkage | major | C-01, C-23, C-31, C-49, C-56, C-62 | 6/6 |
| 5 | Display precision, units and check-draft number reading | major | C-07, C-08, C-20, C-43, C-69 | 6/6 |
| 6 | Analysis validation: coverage wording, joins, reruns, reconcile wording, cut-line ties | major | C-10, C-36, C-58, C-61, C-65 | 4/6 |
| 7 | Data landing and cleaning | major | C-11, C-39, C-40, C-70, C-71 | 5/6 |
| 8 | MCP tool surface: output size, batching, profile settings | minor | C-18, C-35, C-66 | 6/6 |
| 9 | Records, templates and instruction gaps | minor | C-21, C-26, C-37, C-41, C-63 | 6/6 |
| 10 | awb-status reports | minor | C-30, C-67 | 3/6 |
| 11 | README | minor | C-14 | 6/6 |

All 47 confirmed findings are closed by exactly one proposed issue.

## Conventions for every issue

- **One PR per issue,** reviewed by a fresh Codex reviewer and a fresh Opus reviewer before merge. Issue 11 is docs-only, so decide its review approach when it is opened rather than defaulting to that pair.
- **MCP reach.** Every changed helper argument or new command stays reachable over MCP through the existing tools, with a case in `tests/test_awb_mcp.py`.
- **Design record.** A PR that changes accepted behavior updates the matching sentences of `docs/workbench-spec.md`, `docs/workbench-design.md` and `CONTEXT.md`, and adds a `CHANGELOG.md` fragment.
- **No migration.** No projects exist on any release yet.
- **Copilot.** Copilot was not used in this study. Where a fix rests on Copilot's behavior, cite its primary documentation and do not describe the behavior as tested.

---

## Issue 1: Review brief: check meaning, allow honest approximate wording, scope the coverage and style rules

**Severity.** Major. C-03 and C-12 are side effects of #101 (the fix for Oct 16 #85). Skeptics suggested moderate for C-06 and minor to moderate for C-12.

**Closes.** C-03, C-06, C-12, C-50, C-51.

**Problem.**
- **Form over substance, and repairs that delete true context (C-03).** The reviewer judges how evidence is cited, not only whether the claim is true.
  - A data-quality row that cites a saved query fails, although `awb-clean` itself creates such rows with no scan link.
  - A true match that is near-exact, or within a tolerance recorded only in a judgment's detail, has no allowed wording.
  - Plain words such as "flagged" are banned as record words, even when the user wrote them.
  - Agents cleared these by deleting or shrinking true statements. The same reviews also caught real errors, and retail-B's "= 0, exactly" really was false against a recorded -4.38e-06 gap. The defect is the missing allowed wording, not every flag.
- **Meaning errors pass (C-06).** The closed checklist never compares the narratives' definitions and exclusion rules with the brief's agreed definitions, never checks whether wording names what a metric measures, and accepts any cited check as support for a claim about how a source builds a series, including a check the agent wrote into its own judgment detail. One skeptic judged this last point weak: its one case was a check that reasonably supported a definition the user had set.
- **Internal checks forced onto slides (C-12).** A sanity check the user asks for in chat becomes a represented result whose question is the user's words, repeated verbatim in `methodology.md`. The brief-coverage rule then demands a visible answer, and the first-review rule makes the agent add one without asking.
- **A closed readability list (C-50).** Jargon that the glossary does not define passes, even when the brief's Audience records a non-technical audience. Nothing checks typos or punctuation.
- **The imperative rule's scope (C-51).** It covers the whole of `findings.md` outside Implications, including the Answer slide and builder-only chart fields.

**Evidence.**
- **taxi-B** (C-03, C-06):
  - First full review: 21 problems, about 14 of them citation or exactness form (`SIMS/taxi-B/review-reports/agent-005-record01.txt`). The repair deleted the cash-tip observation and cut code-0's missing fields to passenger count only (`SIMS/taxi-B/relay/agent-005.out.md`). That narrowing caused both problems in the scoped review (`agent-005-record02.txt`).
  - "flagged" was rejected although the user had written "retain and flag it" (`SIMS/taxi-B/relay/agent-003.in.md`).
  - The user caught three meaning errors in one read (`SIMS/taxi-B/relay/human-006.out.md`): a trip-time rule narrowed to "zero" against the brief's "zero or less" (brief line 16); base fare called the meter's time-and-distance fare beside a $70.00 JFK median, which the review had flagged only for a missing reference; a count-check sentence that read as adding overlapping rule counts.
  - The flat-fare wording then passed on the agent's own `metrics` judgment detail (`SIMS/taxi-B/relay/agent-006.jsonl`; `SIMS/taxi-B/review-reports/agent-006-record02.txt`).
- **co2-B** (C-03, C-06):
  - 5 of the full review's 9 problems and 4 of the scoped review's 7 were match or reconcile wording (`SIMS/co2-B/review-reports/agent-004-record01.txt`, `agent-004-record02.txt`). The within-1-Mt reconciliation lived only in a judgment detail. The repair replaced it with a citation of OWID's code (decision 3 in `SIMS/co2-B/relay/agent-004.out.md`).
  - "Energy mix" for coal's share of CO2 sat at `findings.md:116` and passed both drafting reviews (`SIMS/co2-B/relay/agent-004.jsonl`). The user caught it in U5 (`SIMS/co2-B/transcript.md`).
- **co2-A** (C-03): the full review flagged "consistent within source rounding" in the donor note (`SIMS/co2-A/review-reports/agent-006-record01.txt`). The tolerance was pre-recorded (`eu27_rounding_tolerance_mt = 0.02` in settings). The repair dropped the statement that EU totals agreed, and the unflagged population check with it. The same wording still ships in speaker notes (`SIMS/co2-A/storage/releases/emissions-and-country-focus/donor-roundtable/001/findings.md` lines 70 and 118). Cost: one 0.9-minute round.
- **retail-B** (C-03, C-06, C-51):
  - The full review flagged the "exactly" revenue match on four lines (`methodology.md:43`, `findings.md:140` and `:146`, `methodology-note.md:26`) and the Answer-slide recommendation at `findings.md:7` and `:12` as imperatives (`SIMS/retail-B/review-reports/agent-005-record01.txt`).
  - The user had asked for that recommendation in msg 4 and supplied the wording in msg 5. The gerund rewrite shipped: "Recommendation: protecting key accounts, testing retention alongside acquisition" (`SIMS/retail-B/storage/releases/marketing-budget-evidence/leadership-deck/001/findings.md` lines 7 and 12).
  - The cohort query (`SIMS/retail-B/project/investigations/marketing-budget-evidence/queries/repeat-within-90-days.sql`) requires a goods line, narrower than brief line 62. Internal `methodology.md:19` states it; the note does not. No review flagged it.
- **taxi-A** (C-12, C-50):
  - The first reviewer required the Q-016 no-mix-up check to appear on a slide (`SIMS/taxi-A/review-reports/agent-007-record01.txt`, third problem). The user removed the bullet in msg 8 (`SIMS/taxi-A/transcript.md` line 413). The agent wrote an override into `brief.md:25` and `methodology.md`.
  - The released `findings.md` has "6 p.m.." at lines 23 and 60 (`SIMS/taxi-A/storage/releases/trip-pattern-comparison/board-brief/001/findings.md`), from the agent's regex in `SIMS/taxi-A/project/.workbench-tmp/revise_board_delivery.py`. The scoped review read those lines and reported clean (`agent-008-record01.txt`).
- **retail-A** (C-50, C-51):
  - The full review passed "signed quantity", "grouping keys" and "permitted repeated line occurrences", with the brief's Audience saying to avoid technical detail. The user asked for plain English in msg 8 (`SIMS/retail-A/relay/agent-008.jsonl` shows the pre-edit text).
  - The same review flagged the chart Axis instruction "keep the saved ranking by GBP increase" at `findings.md:82` (`SIMS/retail-A/review-reports/agent-007-record01.txt`).

**Cause in the release.**
- `awb-package/references/review.md:26`: every checked, reconciles or matches sentence must cite a result ID, an evidence path, or a DQ ID with its scan path. A tolerance appears only in `methodology.md` or Notes, only if `brief.md` or settings recorded it before the result. "A tolerance ... only in a judgment's `detail` ... is a problem".
- `review.md:27`: every part of each question `methodology.md` repeats for a represented result must be answered "not only in a slide's Notes". A sentence about how a source builds a series may rest on "a recorded check", with no requirement that the check establishes it.
- `review.md:28`: readability, "only these": glossary terms, precision against a stated precision, record words ("ledger, flagged, or disposition"), imperatives outside Implications.
- `review.md:29`: "Report exactly this, and nothing else".
- `review.md:43`: in `awb-package`, repair every narrative problem from the first review.
- `awb-package/references/package-contract.md:49`: the same citation and tolerance rule.
- `awb-clean/SKILL.md`, section 6: a `new` quality row cites a saved query and "has no scan link".
- `awb-package/SKILL.md:71` and `awb-init/references/provenance.md:17`: a result's question is one line in the user's words, repeated verbatim.
- `awb-package/assets/package-format/findings-template.md:66` (plain-language method) and `:36-42` (the Answer slide has no recommendation element).

**Fix direction.**
1. Give approximate matches an allowed wording, such as "agree to within source rounding (check: <result>)". Let a tolerance written in a judgment detail count when that detail names it. Let a saved-query quality row be cited.
2. Add a step 3 item that compares the narratives' definitions and exclusion rules with `brief.md`'s Population and Local terms. Require that a cited check establishes a source-build claim, as line 26 already does for "checked" sentences.
3. Exempt verification-only results from the audience-coverage rule: a presentation role on the result, or coverage limited to the Business question.
4. Add a readability item for technical terms when the Audience is non-technical, plus a mechanical punctuation lint in check-draft.
5. Exempt the Answer slide's recommendation and chart-spec fields from the imperative rule, or name "We recommend ..." as the allowed form.
6. Tell the writer to add support before deleting a true statement when repairing.

---

## Issue 2: Review stop rules, rule workflow and receipt checks

**Severity.** Major. All three trace to #96 and #101 (fixes for Oct 16 #84 and #85); for C-72 that link is possible, not shown. Skeptics suggested minor to moderate for C-04: two of three users rated it minor, and the co2-B user rated the wider review process major.

**Closes.** C-04, C-24, C-72.

**Problem.**
- **Stop rules escalate small or self-made problems (C-04).**
  - A scoped reviewer marks a problem "(unchanged since the prior review)" whenever it sits on a line the diff left unchanged. The rule cannot tell a problem an earlier pass missed from one that a repair elsewhere created.
  - A marked problem goes to the user instead of being repaired, so the next review finds it again and the second-review stop fires too.
  - This hit all three Claude-agent runs and no Codex-agent run, because Claude reviewers raise far more first-round problems.
- **Rule workflow (C-24).**
  - The release says to ask whether a correction should become a rule, and to record it, before repairing. Corrections arrive with "go ahead", so agents in all four runs where the agent offered a rule repaired first and asked afterwards, and the rule arrived a turn late.
  - Adding a rule makes the passed review stale, because the receipt covers `foundation/review-rules.md`. When the user approved a rule in the release message, that forced one extra scoped review at release.
  - Rules cover one package or all packages, never one investigation.
- **The receipt does not check report shape (C-72).** `review-receipt record` checks only the last line and row counts, not the `problems` and `errors` lines Brief step 4 asks for. Reviewers on both hosts drop them when the lists are empty: 10 of 24 recorded reports. Nothing was lost in these runs. The latent gap is a report that drops a non-empty list and still counts "0 command problems".

**Evidence.**
- **taxi-B** (C-04): both problems in `SIMS/taxi-B/review-reports/agent-005-record02.txt` are marked unchanged. The reviewer itself says the repair to `methodology.md:159` caused them. Reply 5 asks the user to approve "lack a passenger count" (`SIMS/taxi-B/relay/agent-005.out.md`). The user called it one of the "small approval loops" (`SIMS/taxi-B/feedback/human.md`).
- **retail-B** (C-04, C-24):
  - `SIMS/retail-B/review-reports/agent-006-record01.txt` marks the wrong citation at `methodology.md:64` unchanged. Reply 6 asks the user for a yes. `agent-006-record02.txt` marks the same line unchanged although the prior report had listed it, a reviewer error.
  - In msg 7 the user says routine citation corrections need no separate decision (`SIMS/retail-B/relay/human-007.out.md`). Feedback calls it "the clearest unnecessary gate" (`SIMS/retail-B/feedback/human.md`).
  - Msg 6 asked for checks "for future packages in this investigation"; the agent recorded them for every package and said so.
- **co2-B** (C-04, C-24):
  - The scoped review (`SIMS/co2-B/review-reports/agent-004-record02.txt`) flagged `findings.md:12`, a problem the repair created, which then went into the user's decision list (`SIMS/co2-B/relay/agent-004.out.md`). The "cut" headlines were brought to the user by the agent's own choice after the first review, not by the stop rules.
  - In `agent-005-record01.txt`, `findings.md:42`, `:51` and `:52` are marked unchanged. The agent repaired them itself against `review.md:43` and disclosed it.
  - The rule question came as "Optional" after the repair (`SIMS/co2-B/relay/agent-005.out.md`). In reply 6 the rule add made the receipt stale and forced a 0.55-minute scoped review (`SIMS/co2-B/review-reports/agent-006-record01.txt`). The user disliked that a rule added just before delivery forced another review (`SIMS/co2-B/feedback/human.md` item 2).
- **retail-A** (C-24): reply 8 asked the rule question mid-reply and said "I'll complete the requested edits either way" (`SIMS/retail-A/relay/agent-008.out.md`). In reply 9 two new rules made the receipt stale, and a scoped review ran before release (`SIMS/retail-A/review-reports/agent-009-record01.txt`).
- **co2-A** (C-72): the full reviewer's final message has only a narrative line and the summary line, and `record` accepted it (`SIMS/co2-A/review-reports/agent-006-record01.txt`). The same omission appears in every taxi-B and co2-B report under `SIMS/taxi-B/review-reports/` and `SIMS/co2-B/review-reports/`.

**Cause in the release.**
- `awb-package/references/review.md:35`: the "(unchanged since the prior review)" marker for any problem on a line the diff leaves unchanged.
- `review.md:43`: take a marked problem to the user rather than repairing it. When a second review in one request still reports problems, stop repairing and start no third review.
- `review.md:45`: ask before repairing, and on a yes "record the rule before repairing". The only scope is `--package <investigation>/<package>`, otherwise every package.
- `awb-package/SKILL.md:24`: ask first whether later drafts should be checked.
- `review.md:39`: a review goes stale once `foundation/review-rules.md` changes.
- `awb-release/SKILL.md:20`: a stale receipt needs a scoped review before release.
- `review.md:32`: Brief step 4 asks for "the command's `problems` and `errors` verbatim".
- `awb-package/assets/awb_draft.py`, `review_summary` (about line 4617) and the `record_review` docstring (about line 4691): only the last line and row counts are checked.
- `README.md:70` and `:99` describe the same behavior to users.

**Fix direction.**
1. Let the scoped reviewer say whether an unchanged-line problem follows from a change elsewhere. Send only true misses to the user. Let the agent repair, and show the user, a citation-only or narrowing fix that keeps the evidence.
2. Keep the two-review stop, but list leftover citation and wording items as one plain note with the repairs already made, instead of decisions.
3. When the user's message both asks for the edit and could set a rule, repair now and offer the rule in the same reply. Let a rule add check only the new rule against the draft instead of staling the whole receipt.
4. Add an investigation scope to `review-rules add`.
5. Require `problems: []` and `errors: []` in the report, or have `record` compare the report with the `review-rules check` output.

---

## Issue 3: Conversation: untested explanations, coded values, plain words, complete first answers

**Severity.** Major (C-05, C-09). Skeptics suggested moderate for C-09, since one follow-up fixed it.

**Closes.** C-05, C-09, C-13, C-22, C-33, C-34, C-48.

**Problem.**
- **Untested explanations reach the user as fact (C-05).**
  - Chat replies and headline previews state causes and labels as fact, against the rule in `AGENTS.md` and at the headline checkpoint.
  - Nothing checks the preview. check-draft's causal regex covers only causal verbs on finding slides. The reviewer brief has no item for a user statement presented as a confirmation.
  - Most cases are about meaning rather than causal phrasing, so a phrase regex alone would not catch them.
- **Coded values left undefined (C-09).**
  - The scanner treats any column whose name ends in "ID" as a key and skips its placeholder check, so RatecodeID 99 (71,004 rows against values 1 to 6) never reached the cleaning sign-off.
  - Nothing tells the agent to name a coded value by its meaning in chat; that rule exists only for package drafts.
  - The taxi-B half of this finding was a harness effect: the simulation's URL rule kept the dictionary from the agent until turn 3.
- **Workbench vocabulary (C-13).**
  - Lines the release requires put internals in chat: the recorded interpreter path, the upstream-check notice, and finding counts by status.
  - The plain-words rule covers chat only, so files written for the user to read (headline previews, an ad hoc quality proposal) carry result and question IDs.
  - Claude agents' interim narration is partly a harness effect (C-77), and `provisional` is README vocabulary the release intends.
- **Status line (C-22).** The end-of-turn line counts only root questions, so it can say "0 open" while a must-answer decision is pending. It gives no wording for the init turn; all six runs improvised, accurately.
- **Incomplete first answers (C-33).** No rule says what the first results report must contain. Claude agents reported highlights; Codex agents on the same release gave full tables. The request for full tables rode along in a message the user sent anyway.
- **SKILL.md links (C-34).** Codex's own model instructions tell it to name, link and quote the SKILL.md behind a pause. The release's only counter, `AGENTS.md:32`, was in context in every Codex session and lost every time. The cause is the host, but every Codex user of the release will see it, and only release wording can counter it.
- **Release report and uncommitted code (C-48).** The release report has no item for uncommitted producing or packaging code, `provenance_gaps` excludes it, and the once-a-session commit cap blocks a reminder. A release can freeze code that exists only in the working tree, with nothing said. co2-B's repeated commit suggestion was an agent deviation, not a release defect.

**Evidence.**
- **C-05, taxi-B:** "timing errors, not fast drivers" and "mostly heading to Long Island or Westchester" (reply 2); "the dictionary defines code 0 as a Flex Fare trip" (reply 3); a "Flex Fare trips rose" headline right after calling the meaning unconfirmed, and "vendors differ in why, not how often", which hides vendor 6's 35% (reply 4). The user corrected these in msgs 2 to 5 (`SIMS/taxi-B/transcript.md`) and ranked it pain point 1 (`SIMS/taxi-B/feedback/human.md`).
- **C-05, retail-B:** "not product demand" in headline 3 (reply 3); "the Christmas closure" and early cohorts that "would push their repeat rates up" (reply 4); corrected in msgs 4 and 5 (`SIMS/retail-B/transcript.md`).
- **C-05, retail-A:** the released How we know slide says "as confirmed by the e-commerce lead" (`SIMS/retail-A/storage/releases/marketing-budget/leadership-budget/001/findings.md` line 95), where the user had said "plausible" (msg 4). The user's own suggested wording in msg 8 had already said "genuine repeat items", so this case is weaker.
- **C-09:** `SIMS/taxi-A/transcript.md` reply 4 leads the tipping answer with 0% Bronx and Brooklyn medians and "rate-code 99". The user asks what code 99 is in msg 5. The scan output `SIMS/taxi-A/project/foundation/scans/yellow-trips.json` has no RatecodeID placeholder issue.
- **C-13:**
  - taxi-A: ".venv/bin/python", "eligible-trip view", "All 35 validation checks passed" and "two provisional reference calculations" (`SIMS/taxi-A/transcript.md` replies 1, 4 and 8); the agent-written `quality-proposal.md` under `SIMS/taxi-A/project/` handed to the user in reply 3.
  - co2-A: "cohort checks" and "shared dataset `owid_co2`" (`SIMS/co2-A/transcript.md` reply 2); "Primary result: territorial-change" in the headline preview linked in reply 5.
  - retail-A: "Committed through `7f1ccf0`", "91 validation checks" and "no stale results" (reply 4), and the upstream notice (reply 3), in `SIMS/retail-A/transcript.md`.
  - Each user flagged jargon in `SIMS/<run>/feedback/human.md`.
- **C-22:** `SIMS/taxi-B/transcript.md` line 212 (reply 3) says "5 answered (provisional), 0 open" while Q-011, a must-answer decision under Q-003, was open (`questions.md` at commit `412d7d9` in `SIMS/taxi-B/project/`). The user found it confusing (`SIMS/taxi-B/feedback/human.md` section 3).
- **C-33:**
  - taxi-B reply 3 names 4 of the top-10 zones; msg 4 asks for full tables.
  - co2-B A2 gives values for 3 of 20 Q1 countries and leaves the coal count ambiguous between 59 and 60; U3 asks for tables.
  - retail-B reply 3 gives 3 of 24 monthly figures and 3 of 12 cohort rates; msg 4 says "Ranges alone don't fully answer those questions".
  - Sources: `SIMS/taxi-B/transcript.md`, `SIMS/co2-B/transcript.md`, `SIMS/retail-B/transcript.md`.
- **C-34:** taxi-A replies 1 and 8, co2-A reply 1, retail-A replies 1, 3, 6 and 8 (`SIMS/<run>/relay/agent-NNN.out.md`). The Codex base instruction to "name and link to the exact SKILL.md ... quote the relevant instruction" is in the session metadata of the rollouts under `SIMS/taxi-A/agent-home/.codex/sessions/`.
- **C-48:**
  - retail-A release 001's manifest lists the Q4 version-B producer and queries under `producing_uncommitted_changes` and six package-format files under `packaging_uncommitted_changes`. The release reply says nothing about it (`SIMS/retail-A/storage/releases/marketing-budget/leadership-budget/001/manifest.json`; `SIMS/retail-A/relay/agent-009.out.md`).
  - Reply 5 had said "This Q4 revision is uncommitted".

**Cause in the release.**
- `awb-init/assets/workbench/AGENTS.md`:
  - `:28`: records keep IDs; "chat uses plain words", with a word list of record terms only.
  - `:30`: "Offer an untested explanation as a question. Name every share's base and say when it changes."
  - `:32`: "never send them to a skill or instruction file".
  - `:34`: the closing line counts "the ledger's roots".
  - `:50`: suggest a commit at most once a session.
- `awb-package/SKILL.md`:
  - `:49`: the preview goes to `.preview/headlines.md`, "which no check reads".
  - `:52`: "never as a headline's claim", with no check.
  - `:96`: the package report.
- `awb-package/assets/awb_draft.py`, `_CAUSAL` (about line 1157) and `_UNCHECKED`: causal verbs only, finding slides only.
- `awb-init/assets/awb_provenance.py`, `_finding_warnings` (about line 1661): numbers and check wording only.
- `awb-clean/scripts/scan_dataset.py:65` (`KEY_NAME` matches any name ending in "Id", case-insensitive) and `:477` (sentinel check skipped for key-like names).
- `awb-init/SKILL.md:40` ("Report in one line the interpreter its `interpreter` entry records") and `awb-init/references/landing.md:11` (the upstream notice).
- `awb-status/SKILL.md:30`: `must_subquestions` are reported after roots, but the footer ignores them.
- `awb-release/SKILL.md:61`: the Report has no uncommitted-code item and caps the commit suggestion.
- `awb_draft.py` `provenance_gaps` (about line 5023) counts only `{"unknown": ...}` values.

**Fix direction.**
1. Give the explanation rule two or three examples (a label, a cause, a user's recollection). Have the reviewer flag a user statement shown as a confirmation. Run a check over the headline preview for causal words and "confirmed" attributions.
2. Name a coded value by its meaning the first time chat uses it. Narrow `KEY_NAME` so a code column such as RatecodeID still gets the placeholder check.
3. Extend plain words to files written for the user, and give the preview a fixed format with no IDs. Reword the interpreter and upstream lines in plain terms.
4. Count open must-answer decisions in the footer, and define the init-turn line.
5. Say that the first results report shows every item a question asks for (all N of a top-N, every period, every group with its base), or links the result file that does.
6. Strengthen `AGENTS.md:32`: "state a pause's reason in plain words; do not name, link or quote SKILL.md or AGENTS.md, even when your host asks you to". Wording alone may not beat a host instruction.
7. Name uncommitted producing or packaging code in the release report, whatever the commit cap says.

---

## Issue 4: awb-package instructions, preview checkpoint and slide linkage

**Severity.** Major for C-01 on Codex hosts. Skeptics found that reading costs little wall time on Claude, and suggested minor for C-23.

**Closes.** C-01, C-23, C-31, C-49, C-56, C-62.

**Problem.**
- **Instruction load, and rules placed where the writer reads them too late (C-01).**
  - About 13,500 words must be read before `helpers.md` adds 7,011 more. The four core files grew from 11,749 words on Oct 16 to 14,727.
  - On Codex, combined reads truncate under the agent's own output caps and are repeated after mid-turn compaction, costing about 1 to 5 minutes per packaging turn.
  - Rules on imperatives, record words and glossary first use live only in the reviewer brief, which the writer reads after drafting. Check citations and "exactly" sit in one long contract paragraph. First full reviews then raise avoidable problems.
  - The 35-69% packaging share is mostly drafting, exports and record updates, not reading.
- **Required slides take up the requested length (C-23).** The default storyline comes to 9 slides against "about 8". The README never says before the checkpoint that the title counts. Every user approved the trade-off.
- **Brittle linkage (C-31).**
  - check-draft runs its claims and storyline checks even when a methodology heading is missing, so one missing heading gives four rows, one of them a wrong "move it to finding position N".
  - The first citation sets a slide's primary result, so inserting a paragraph silently changes it.
  - The weakest cited claim sets a slide's claim strength.
- **The preview is never checked (C-49, C-56).** Nothing counts preview headline words, yet the skill has the agent tell the user a headline holds at most 15 words. Nothing carries chart forms agreed at the preview into the draft. Export cannot pivot a long-form result into a promised grid, and packaging may not reshape results, so the agent quietly picks a chart the result can feed.
- **Priority set silently decides placement (C-62).** `awb-scope` assigns priority without telling the user, the slide order sorts by it, and the default appendix proposal moves the user's lower-priority questions with a label the user never saw. The user still decides at the checkpoint.

**Evidence.**
- **C-01:**
  - `SIMS/co2-A/feedback/agent-notes.md` lines 28, 57, 71 and 89 record truncated combined reads. A read of `review.md` plus templates returned "truncated output (original token count: 18235)" in the co2-A main rollout.
  - `SIMS/taxi-A/relay/agent-007.jsonl` re-reads SKILL.md and `review.md` at 4.4 and 4.5 minutes, right after compaction at 4.3 minutes.
  - `SIMS/retail-B/review-reports/agent-005-record01.txt`: 4 of 15 problems came from rules found only in `review.md`, and 4 from the long contract paragraph. `SIMS/retail-B/feedback/agent.md` puts the cost in "rules discovered late".
- **C-23:** `SIMS/taxi-B/relay/agent-004.out.md` ("Eight main slides need the four required slides"; Q1 and Q5 to the appendix); `SIMS/co2-A/relay/agent-005.out.md` (Limitations to the appendix); `SIMS/retail-A/relay/agent-006.out.md` (Q2 and Q3 merged); `SIMS/retail-B/relay/agent-005.out.md` (9 main plus 2 appendix, with the user declining an 8-slide option). `SIMS/retail-B/feedback/human.md` section 3 asks for clearer counting up front.
- **C-31:**
  - `SIMS/retail-B/relay/agent-006.jsonl`: one check-draft returns headings, claims, storyline ("move it to finding position 6") and unlinked_findings rows for one stale heading.
  - `SIMS/taxi-A/relay/agent-007.jsonl`: check-draft call 3 shows the primary results of the airport and zone slides changing (q5-supported/Q-013 to board-rankings/Q-005) with `passed: true`. Call 1 shows a claims row lowering the tipping slide to descriptive.
- **C-49:** `SIMS/retail-B/transcript.md` reply 3 ("Each headline is at most 15 words") includes a 16-word headline that the user approved. check-draft raised it in `SIMS/retail-B/relay/agent-005.jsonl` and it became decision 1 in reply 5.
- **C-56:** reply 3 promised a Year 1 / Year 2 / 24-month reconciliation table, and the agent's preview file recorded "chart: table, components by year". The draft exported a 24-month bar chart (`SIMS/retail-B/relay/agent-005.jsonl`). The user asked again in msg 6, and the result was reshaped (commit `cea5151` in `SIMS/retail-B/project/`).
- **C-62:** `SIMS/taxi-B/relay/agent-002.jsonl` adds Q-001 and Q-005 with `--priority should`. Reply 4 proposes moving "your two 'should' questions" to the appendix (`SIMS/taxi-B/relay/agent-004.out.md`). The user objected to the label in `SIMS/taxi-B/human/notes.md` turn 5 and approved the move.

**Cause in the release.**
- `awb-package/SKILL.md:10`: "Read the package contract first". Step 5 sends the writer to `references/review.md` only after drafting.
- `awb-package/references/package-contract.md:49`: one paragraph of about 1,900 characters holds number tracing, check citations, tolerance and "exactly".
- `review.md:28`: the readability rules live only in the reviewer brief.
- `awb-package/references/helpers.md`: 7,011 words, with lines up to 3,843 characters.
- `package-contract.md:46`, `awb-package/SKILL.md:54`, `README.md:22`, `:53` and `:68-69`, and `findings-template.md:12`: the required slides, the appendix option and the length question, with no word on how the title counts.
- `package-contract.md:34` (the first citation is the primary result; siblings sort by priority), `:36` (the slug is kept), `:49` (identical headings) and `:50` (weakest claim). `methodology-template.md:35`. `awb_draft.py` check-draft (about lines 3089-3103) runs the claims and storyline checks when headings fail.
- `awb-package/SKILL.md:49` (no check reads the preview), `:54` (tell the user a headline holds at most 15 words), `:83`; `package-contract.md:19`; `awb_draft.py:1901` (`HEADLINE_WORDS` applies only at check-draft).
- `awb-package/SKILL.md:10` and `:69` (packaging serializes; select rows rather than record a new result); `helpers.md:52` (the closed `--chart` grammar has no pivot).
- `awb-scope/SKILL.md`, step 2: priority set by the agent, "Write the records without a separate confirmation round".

**Fix direction.**
1. Put a short writer's checklist in SKILL.md step 3 with every rule the reviewer enforces. Split `helpers.md` so an agent reads only the part it needs. Tell agents not to batch whole reference files into one read.
2. Say in the README and at the checkpoint that the title counts toward the length, and offer moving How we know and Limitations before moving findings.
3. Make a slide's primary result explicit rather than the first citation, and suppress dependent rows when a heading is missing.
4. Count preview headline words with a helper, such as `check-draft --preview`.
5. Record chart forms agreed at the preview. When a promised form needs a reshaped result, say so to the user instead of switching forms.
6. Show priorities in the scope report, or stop citing them as the reason for an appendix move.

---

## Issue 5: Display precision, units and check-draft number reading

**Severity.** Major as filed. Skeptics suggested moderate for C-07 and C-08.

**Closes.** C-07, C-08, C-20, C-43, C-69.

**Problem.**
- **No audience-based display defaults (C-07).** A precision is recorded and reviewed only when the user volunteers one. Nothing prompts for it or for clock format, and nothing covers noting that rounded start, end and change values may not subtract. Formatting is therefore left to the host model's taste. "Full saved precision" overstates it: export forces rounding beyond four decimals.
- **Rescaled, approximate or derived figures (C-08).**
  - `[scale]` is per column and rescales the chart file too, so a sentence cannot use billions of tonnes beside a chart kept in Mt.
  - Rounding traces by decimal places only, so "about 22,500" cannot trace to 22,523.
  - A sum of recorded values needs separately authorized analysis.
- **Number and name checks misread notation (C-20).**
  - In "a%/b%" the reader drops the first value's percent sign.
  - Slash-joined 24-hour time lists are read as joined numbers.
  - Export's own "divided by 1000000000" line, which SKILL.md says to paste into `methodology.md`, fails the numbers check.
  - A hyphenated result ID used as a prose word fails the name check.
  - `review-rules add` pulls digit runs out of words ("CO2").
  - A year after a word is read as a count, and the date inside an acquisition ID is read as a number. Both are documented fail-safe behavior, but still friction.
- **Chart rows and roles (C-43).** `@where` takes one column, with no conjunction or comparison. Bar, column and line charts have no annotation role, and check-draft refuses a column with no role.
- **An unsilenceable precision warning (C-69).** `precision_warnings` flags any percent fraction saved to exactly four decimals and shown to fewer than two, even when the value is exact. It says the query rounded it, and nothing confirms it.

**Evidence.**
- **C-07:**
  - co2-A's draft carried "8,645.2 million tonnes", "US 23.57%" and "14.32 tonnes", from `foundation/display.toml` `[round] change_mt = 1, world_share_percent = 2` (`SIMS/co2-A/project/foundation/display.toml`; `SIMS/co2-A/relay/agent-007.jsonl`).
  - The user's rounding request took a 6.7-minute turn, which also fixed headline punctuation and recorded a new result (`SIMS/co2-A/feedback/human.md` pain point 1).
  - taxi-A's draft for a non-technical board used "18:00", from its own HH:MM result labels. The user made 12-hour times a rule in msg 8 (`SIMS/taxi-A/transcript.md`).
  - co2-B's A3 table showed Ukraine 286 to 142 as -143, and the user asked for a note in U4 (`SIMS/co2-B/transcript.md`).
  - taxi-B's Claude agent used "6 pm" and "5 am" unprompted, so the clock-format symptom depends on the model.
- **C-08:**
  - `SIMS/co2-A/relay/agent-007.jsonl`: producer `territorial-change-tonnes.py`, a run with 7 standard checks, and a recorded finding, all for "about 8.6 / 2.2 billion tonnes" beside a whole-Mt chart. The agent chose this before running check-draft.
  - `SIMS/co2-A/relay/agent-006.jsonl`: "1,844.55 billion" flagged and deleted.
  - `SIMS/retail-A/feedback/agent.md` line 27: wrote 22,523 instead of the user's "about 22,500".
- **C-20:**
  - `SIMS/taxi-A/relay/agent-007.jsonl`, the first check-draft: 15 numbers rows, including `21:00/22:00/23:00`, `2024` twice and nine first members of percent pairs. The repair script is `SIMS/taxi-A/project/.workbench-tmp/repair_board_wording.py`.
  - `SIMS/co2-B/relay/agent-004.jsonl`: "1000000000" at `methodology.md:86-87`, then an `allowed_numbers` entry.
  - `SIMS/co2-A/relay/agent-006.jsonl`: a name row for "coal-share" at `findings.md:94`.
  - `SIMS/retail-A/relay/agent-007.jsonl`: `20261017` at `methodology.md:28`.
  - `SIMS/co2-B/relay/agent-006.jsonl`: "the rule names 2" against `findings.md:1`.
- **C-43:** `SIMS/taxi-A/relay/agent-007.jsonl` records board-rankings, a projection result built only to select one scenario's top ten in each month. `SIMS/retail-A/storage/releases/marketing-budget/leadership-budget/001/charts/chart-3.csv` and `chart-4.csv` put counts, bases and growth rates into category labels. The taxi-B example cited for this finding does not hold, per the skeptics.
- **C-69:** `precision_warnings` with example 0.1875 on every retail-B export that wrote files (`SIMS/retail-B/relay/agent-005.jsonl`, `agent-006.jsonl`). The value is 45/240, unrounded, at row 993 of `SIMS/retail-B/project/investigations/marketing-budget-evidence/results/product-cancellation-rate.csv`.

**Cause in the release.**
- `awb-init/assets/workbench/investigation/brief.md:19`: record a precision "when the user states them".
- `awb-package/SKILL.md:30`: precision is recorded only as the user states it.
- `awb-package/SKILL.md:70` and `helpers.md:51`: `[round]` takes "the places the slide's number format shows".
- `review.md:28`: decimals are checked only against a stated precision.
- `awb-package/SKILL.md`, step 6 repair rules 1 to 4 (lines 85-90).
- `helpers.md:42-44` (tracing by decimal window and k/M/bn scales) and `:50` (`[scale]` is per column; results tables take only columns, values and percent).
- `awb_draft.py`: `_untraced` (about line 1687), and the chart entry scale must equal display.toml's (about line 2456).
- `awb_draft.py`: `_NUMBER` (about line 1461; its lookahead drops % before "/digit"), `_NOT_QUANTITY` (about lines 1403-1408), `_identifier` (about line 1439), `_sources` (lines 3704-3720 write "divided by"), `_RULE_NUMBER` (line 4069, no letter lookbehind).
- `helpers.md:27`, `:44-49` and `:53`; `awb-package/SKILL.md:71` (paste `methodology_lines`).
- `awb_draft.py`: `parse_chart` (about line 3472), `_select` (about line 3573), `CHART_FORMS` (about line 1904), `check_charts` (about line 2375). `helpers.md:52`; `package-contract.md:53`.
- `awb_draft.py`: `_shape` (lines 3684-3691) and `_PRECISION` (line 3385); `[confirmed]` covers only label collisions. `helpers.md:54`.

**Fix direction.**
1. Ask for a display precision and clock format at the brief or headline checkpoint, or default them from the Audience. Add a note that changes are computed before rounding.
2. Allow a per-chart or per-sentence unit, so prose can use a scale the chart does not. Allow "about N" with a stated rounding to significant figures. Allow a declared sum.
3. Keep the % on each value of "a%/b%". Accept slash-joined time lists. Trace export's own divisor text. Ignore hyphenated IDs used as prose words. Skip digits inside words in rule warnings.
4. Let `@where` take two conditions, and add an annotation role for bar, column and line charts.
5. Let `[confirmed]` silence a precision warning, and reword its diagnosis.

---

## Issue 6: Analysis validation: coverage wording, joins, reruns, reconcile wording, cut-line ties

**Severity.** Major as filed for C-10. Skeptics suggested moderate: no figure was wrong, and the user caught both wordings before packaging.

**Closes.** C-10, C-36, C-58, C-61, C-65.

**Problem.**
- **Coverage gaps worded badly (C-10).** The per-entity coverage rule makes the agent count and caveat short series, but sets no wording. co2-B again described unreported early years as "count as zero", then called a fill-forward scenario a "ceiling". This is the third co2 run in a row with a gap-wording error. The agent did count and disclose the gaps at the first answer, which Oct 16 did not.
- **Joins with no not-applicable form (C-36).** Leaving joins out of the spec is recorded as "not assessed". Promotion then needs an explanatory caveat, so each row reads "not assessed: joins; joins not ..." and `awb-status` repeats it for every finding. The length-against-left-rows check cannot validate a join made before aggregation. The Codex agents bypassed it with trivial specs whose pass says nothing.
- **Near-ties at a cut line (C-58).** Ties are treated only as a determinism problem. Nothing reports the margin between rank N and N+1, so a top-N chart can drop an entry that is tied at the deck's display precision. No stated claim depended on it here.
- **Recording a check demotes an approved finding (C-61).** The only documented way to record a check is to edit a judgment's detail and rerun, and any rerun with changed checks demotes a supported finding to provisional, even when the table is identical. The state template says a rerun demotes only when it "changes a supported finding's result".
- **Overlapping exclusion rules (C-65).** `reconcile()` requires an exclusive per-rule split, while every description calls it "rows excluded by each rule". Nothing covers rules that overlap. The guide's own phrase reached the deck next to independently counted rule figures and read as if they add up.

**Evidence.**
- **C-10:**
  - Reply 2 (`SIMS/co2-B/transcript.md` line 115) says "Earlier years count as zero in the cumulative totals". The same wording went into DQ-004 in `foundation/quality.md` (`SIMS/co2-B/relay/agent-002.jsonl`).
  - U3 challenged it. Reply 3 (line 254) said "I also calculated a ceiling ... at most 15.51%", and U4 corrected it.
  - Ranked pain point 1 in `SIMS/co2-B/feedback/human.md`.
  - A third error went unnoticed and into release 001: India's 11-year mid-series gap (1867-1877) is never disclosed, and the "illustrative scenario" fills only 1850-1857 for India.
- **C-36:** 11 of 11 taxi-B results, 6 of 6 co2-B and 7 of 8 retail-B carry the caveat (`SIMS/<run>/project/investigations/*/state.md`). co2-B told the user "Only the join check is unassessed" (`SIMS/co2-B/relay/agent-002.out.md` line 25). The Codex runs filled joins on all 36 results with specs at the output grain.
- **C-58:** `SIMS/taxi-A/project/investigations/trip-pattern-comparison/results/q5-supported.csv` rows 11-12: Briarwood/Jamaica Hills 93.4972501 at rank 10, LaGuardia 93.4969666 at rank 11. Both round to 93.50; the released top-ten chart shows only Briarwood/Jamaica Hills at 93.50 (`SIMS/taxi-A/storage/releases/trip-pattern-comparison/board-brief/001/charts/chart-4.csv`).
- **C-61:** `SIMS/taxi-B/relay/agent-006.jsonl`: the rerun returned status "provisional" with an identical table checksum, and the agent promoted it again. Project commits `01b0aa8` and `188dfc2` show the history entries "rerun: supported to provisional" and "promoted to supported" (`SIMS/taxi-B/project/`).
- **C-65:** `SIMS/taxi-B/feedback/agent-notes.md` turn 3 ("first rule wins"). The reconcile detail credits 2,182 to the speed rule, while the deck shows 2,433. The draft sentence "records kept plus the records excluded by each rule equal the records going in, exactly" (`SIMS/taxi-B/review-reports/agent-005-record01.txt`) was corrected by the user in msg 6.

**Cause in the release.**
- `awb-init/assets/workbench/workbench-guides/analysis.md:15`: count the periods each entity has data for; a short count "is a caveat on the finding", with no wording.
- `awb-explore/SKILL.md:52`: record short entities, with no wording.
- `awb-init/assets/awb_validate.py`:
  - `:229`: an omitted key becomes not-applicable, "not assessed".
  - `:163-180`: `_joins` requires keys and left_rows and has no outcome/detail form.
  - `:208-213`: `_judgment` covers only scope, metrics and values.
- `investigation/settings.toml:41-44`: the spec shapes.
- `awb_provenance.py:1006-1013` (the reserved caveat segment) and `:1781-1787` (promotion refused until a caveat explains it).
- `awb-status/scripts/collect_status.py:268-270` and `awb-status/SKILL.md:29`: every caveat listed.
- `analysis.md:17`: "a stable total ORDER BY, with tie-breakers". `awb-package/SKILL.md:69`: `@first=10`, with no boundary check.
- `awb_provenance.py:1485-1487` (`_baseline` includes check detail) and `:1568-1581` (`record_finding` demotes on any baseline change).
- `analysis.md:19`: record a check by editing the detail and rerunning.
- `investigation/state.md:10`: the narrower template text.
- `awb_validate.py:96-132` (`_row_counts`) and `:148-162` (`reconcile` docstring); `references/validation.md:14`; `investigation/run.py:76-87`.

**Fix direction.**
1. Give the coverage caveat a wording, such as "unreported before YEAR; sums cover reported years only". Say that a scenario filling gaps is illustrative, never a bound.
2. Add a not-applicable form for joins with a reason, and stop repeating the reserved segment when a caveat already explains it.
3. Report the margin at a top-N cut and flag entries tied at display precision.
4. Keep a supported finding when only check detail changed and the table is identical, or add a command that records a check without a rerun. Align the state template's text with the code.
5. Document overlapping rules and give narrative wording that separates exclusive counts from independent rule counts.

---

## Issue 7: Data landing and cleaning

**Severity.** Major for C-11 as filed. The removed rows were true copies and the user approved afterwards, so the harm is process, not numbers.

**Closes.** C-11, C-39, C-40, C-70, C-71.

**Problem.**
- **Cross-sheet copies removed on the agent's inference (C-11).**
  - `awb-clean` states the right condition: cross-part copies are the agent's to remove only when the user or the source's documentation says they are re-extracts.
  - The example "such as overlapping periods" and the phrase "parts known to be re-extracts" let an agent count its own observation, or its prior knowledge of a public dataset, as meeting it. That contradicts `README.md:67`.
  - The scan reports cross-part copies and within-part repeats as one `duplicate-rows` issue, so the record carries a partial correction under one status.
  - This happened in one of two retail runs; retail-A's agent asked first.
- **Scoping against the data guide (C-39).** In a new project, `awb-scope` tells the agent to test definitions against source data during the scoping round, while the README says scoping brings no data in and `data.md` allows record inspection only from landed copies. taxi-B queried unlanded inbox files.
- **Landing instructions (C-40).** `landing.md` buries the `land()` signature in one long paragraph of URL refusal rules and also carries the unrelated source-reference grammar. Neither `landing.md` nor `data.md` covers a fetched archive.
- **EDA flood (C-70).** On a wide, skewed country-year panel, the per-column rules fire about twice per column. Including aggregate rows inflates the extremes. The "not read by the scan" line lists `run.py`'s `[parameters]` keys.
- **Helper output quirks (C-71).**
  - On a rescan, the compact `issues` field lists only new unrecorded issues, though the help says "unrecorded issues", so `issues: []` appears beside 12 baseline issues still unrecorded.
  - `profile` prints pandas dtypes under "type", so DECIMAL(18,6) shows as float64.

**Evidence.**
- **C-11:**
  - `SIMS/retail-B/relay/agent-002.jsonl`: the overlap count (22,523), the view rewrite in `foundation/views/01_online_retail.sql`, and the S1 correction "so they are re-extracts".
  - `SIMS/retail-B/transcript.md` reply 2 reports it afterwards. Msg 3 says "I'd expect to be asked before removing transaction rows where their meaning is uncertain".
  - `SIMS/retail-B/feedback/agent-notes.md` turns 1 and 3; `SIMS/retail-B/feedback/human.md` item 2; `SIMS/retail-B/project/foundation/quality.md` DQ-001.
  - Counterexample: `SIMS/retail-A/transcript.md` lines 98-161.
- **C-39:** `SIMS/taxi-B/relay/agent-001.jsonl` runs DuckDB over `inbox/yellow_tripdata_2024-*.parquet` during the scope round. `SIMS/taxi-B/feedback/agent-notes.md` turn 1 cites `awb-scope`'s "source systems" line. The user noticed (`SIMS/taxi-B/feedback/human.md`).
- **C-40:** `SIMS/co2-B/feedback/agent-notes.md` line 35 ("findable but the doc mixes many concerns"). `SIMS/retail-B/feedback/agent-notes.md` lines 29 and 38: the fetch callable for a zip had to be inferred. It worked the first time.
- **C-70:** `SIMS/co2-B/project/investigations/co2-emissions-change/exploration/eda/owid_co2.json` lists 142 anomalies over 80 columns: 74 extreme-values, 57 high-nulls, 7 null-shift and 4 rare-negatives. The printout shows 15 (`SIMS/co2-B/relay/agent-002.jsonl`).
- **C-71:** `SIMS/retail-A/relay/agent-003.jsonl`: the rescan result shows `"issues":[]` with 13 delta entries, and `profile` shows `price | float64`.

**Cause in the release.**
- `awb-clean/SKILL.md:33` ("that the user or the source's documentation says are re-extracts of the same rows, such as overlapping periods or a repeated export") and `:35` ("parts known to be re-extracts ... are yours to remove").
- `awb-init/references/landing.md:39`: overlapping periods can hold the same rows twice.
- `README.md:67`: the user decides unless the source says they are re-extracts.
- `awb-clean/scripts/scan_dataset.py`, about lines 536-554: one `duplicate-rows` issue.
- `awb-scope/SKILL.md:33` (tested "against source data") and `:38` ("Look facts up yourself in the repository, catalog, and source systems"). `README.md:54` and `:64`.
- `awb-init/assets/workbench/workbench-guides/data.md:9`: "inspect records only from landed copies".
- `landing.md:9` (the `land()` paragraph), `:21-29` (archives via the CLI only) and `:53-61` (source-reference grammar). `data.md:19` and `:21`.
- `awb-explore/scripts/eda_scan.py:578-579` (high-nulls at 20%), `:592-595` (any value beyond 3 IQR) and `:106-131` (unread `[parameters]` keys).
- `scan_dataset.py:819-821`: the compact issues list is filtered to new issues on a rescan.
- `awb-init/assets/awb_validate.py`, `cli_profile` (about lines 300 and 321): `relation.df()` dtypes.

**Fix direction.**
1. Drop "such as overlapping periods". Say that an observed overlap or prior knowledge is not the source saying so. Split cross-part copies from within-part repeats into separate scan issues.
2. Point `awb-scope` at `data.md`: documentation lookups are fine before landing, record lookups are not.
3. Put the `land()` signature first, move the source-reference grammar to the `awb-status` references, and add the fetched-archive case.
4. Group EDA anomalies per column family or by entity type, and stop listing `run.py` parameters as unread.
5. Document or fix the rescan issues list, and print SQL types in `profile`.

---

## Issue 8: MCP tool surface: output size, batching, profile settings

**Severity.** Minor.

**Closes.** C-18, C-35, C-66.

**Problem.**
- **Output size (C-18).** The release's MCP server cuts every result at 16,000 characters. At normal investigation sizes, `read state` and `read status` exceed that, so the cut removes findings and issues and leaves invalid JSON. Neither command has a section or compact option. The saved overflow file ends with "exit status 0", so `json.loads` fails on it. Status repeats every finding's text and reason under caveats. Export reprints about 6,000 characters of `methodology_lines` on every revision.
- **One command per call (C-35).** The MCP tools take one command per call, with no batch input. Claude agents therefore route runs of records writes, multi-query `sql` and `--help` through Bash, against the MCP-first rule. On Claude Code only, the reviewer brief names the CLI form, contradicting its own Launch section. On a default Claude Code host each such Bash call needs approval. On Copilot each terminal call needs approval too; that is inferred from Copilot's documented model, not tested.
- **Profile settings (C-66).** Neither `awb.py profile` nor the MCP read `profile` can load an investigation's views or settings, while `sql --settings` can. The read tool's shared schema lists `settings` beside `profile`, which invites the failing call.

**Evidence.**
- **C-18:**
  - `SIMS/taxi-B/relay/agent-004.jsonl`: status cut by 5,233 characters of 21,111. The overflow went to a temp folder the simulation barred, so on a real host the agent could have read it.
  - `SIMS/taxi-A/relay/agent-005.jsonl` to `agent-009.jsonl`: state and status reads cut.
  - `SIMS/retail-A/agent-home/.cache/tmp/awb-mcp-*/`: the overflow file fails `json.loads` with "Extra data" (`SIMS/retail-A/feedback/agent-notes.md` turn 5).
  - `SIMS/retail-B/relay/agent-005.jsonl`: exports of about 9,000 to 10,000 characters each.
- **C-35:** main-thread Bash helper calls against MCP calls were 6:94 (taxi-B), 13:57 (co2-B) and 43:40 (retail-B) (`SIMS/<run>/relay/agent-00N.jsonl`). In `SIMS/retail-B/relay/agent-002.jsonl` the agent read MCP `read help` for `questions add`, then batched in Bash. `SIMS/co2-B/feedback/agent.md` and `SIMS/retail-B/feedback/agent.md` give batching as the reason. Reviewer subagents ran `review-rules check` through Bash in all three Claude-agent runs.
- **C-66:** `SIMS/co2-A/relay/agent-003.jsonl` item_31: `read profile` with `settings` returned "unknown arguments: settings". The agent copied the view's filter into a plain SELECT.

**Cause in the release.**
- `awb-init/assets/awb_mcp.py`:
  - `:72`: `MAX_CHARS` defaults to 16000.
  - `:464-472`: `_clip` saves the full text.
  - `:497-501`: "exit status N" is appended before clipping.
  - `:504`: `_text` returns no structured content.
  - `:373-381`: `_check_keys` allows `settings` only for `sql`, while `:142-150` holds one schema for all commands.
- `awb-status/scripts/collect_status.py:262` and `:269-270`: caveats duplicate findings.
- `awb-package/SKILL.md` step 4 (export on every revision) and `helpers.md:53`.
- The `awb_mcp.py` write tools take one `command` plus one `args` array per call.
- `awb-init/assets/workbench/AGENTS.md:20-24`: MCP first, but the commands are named in CLI form.
- `awb-package/references/review.md`: the Brief (line 18) names `python3 src/awb.py review-rules check`, while Launch (line 10) says Claude Code reviewers use MCP.
- `awb_validate.py` `cli_profile`: no `--settings`; it opens a session without the investigation. `awb_landing.py` `cli_sql` passes the investigation (about line 1712).

**Fix direction.**
1. Add compact and section modes to `state` and `status`. Drop the duplicate caveat list. Write overflow files without the exit trailer. Return structured content for JSON outputs.
2. Print `methodology_lines` from export only when asked or when changed.
3. Accept a list in `questions add` and `answer` and in `state finding --text`, so MCP-first does not cost batching. Name the MCP calls in the reviewer brief for every host that has them.
4. Let `profile` take an investigation, and give each read command its own argument set.

---

## Issue 9: Records, templates and instruction gaps

**Severity.** Minor.

**Closes.** C-21, C-26, C-37, C-41, C-63.

**Problem.**
- **Small conflicts and gaps agents resolved alone (C-21), all without harm:**
  - `AGENTS.md` sends the agent to `data.md` before publishing data or editing views, while `awb-clean` says a cleaning pass reads neither guide.
  - The answerer list has no value for a fact looked up in documentation.
  - A result's question must be in "the user's own words, never paraphrased", with no rule for derived checks the user never phrased.
  - `awb-package` step 1 always asks for the dataset selection, and asks about the methods note exactly when the request already mentions one.
  - The review-rule offer covers only corrections to an existing draft.
  - Export "creates the draft folder", while step 3 writes the preview and narratives into it first.
  - The run.py reading, the co2-B packaging doubt and the retail-B "Project conventions" section are weaker cases.
- **No place for a settled first brief, and no create helper (C-26).** `awb-init` runs `awb-scope`'s first round before any investigation exists, and `awb-scope` writes records only after that round. The settled parts of a rich first message have nowhere durable to go. Two of three Codex agents invented a README section. There is no command that creates an investigation, so templates are copied by hand.
- **One item per records call (C-37).** `questions add` and `answer` take one question per call, and `state finding --text`, `--claim` and `--caveat` take one result. A scoping round of 10 or 11 questions costs as many calls. Issues, next steps, status changes and promotions already batch.
- **A candidate source cannot meet the basis rule (C-41).** The source register requires Relevance and fitness to start with "from documentation" or "from landed records", and `awb-status` flags anything else. A candidate registered at setup has neither, so agents hedge with "not yet assessed", which status flags. The legend paragraphs in state and sources templates were handled inconsistently.
- **Finished next steps outlive the release (C-63).** No step in `awb-package` or `awb-release` retires a finished next step. Status reports next steps verbatim, and its staleness check ignores `deliveries/`.

**Evidence.**
- **C-21:**
  - `SIMS/taxi-A/feedback/agent-notes.md` line 27 (data guide versus cleaning).
  - `SIMS/taxi-B/project/investigations/airport-trips-and-tipping/questions.md` Q-008 (answerer "stakeholder", answered by the "NYC TLC data dictionary").
  - `SIMS/taxi-B/project/investigations/airport-trips-and-tipping/settings.toml` line 119 (a fragment used as a question); `SIMS/taxi-B/feedback/agent.md` section 2.
  - `SIMS/retail-A/feedback/agent.md` lines 25 and 31; `SIMS/retail-B/project/AGENTS.md` "Project conventions".
- **C-26:** the README "Scoping handoff" block in `SIMS/taxi-A/relay/agent-001.jsonl` and `agent-002.jsonl`; `SIMS/co2-A/feedback/agent-notes.md` lines 9 and 24; `SIMS/retail-A/feedback/agent-notes.md` turn 1; `SIMS/taxi-B/feedback/agent.md` (templates copied by hand).
- **C-37:** `SIMS/taxi-B/relay/agent-002.jsonl` (10 `questions add` calls); `SIMS/retail-A/relay/agent-002.jsonl` (11 adds and 3 answers) and `agent-005.jsonl` (15 `state finding --text` calls); `SIMS/co2-B/feedback/agent-notes.md` line 34.
- **C-41:** `SIMS/retail-A/relay/agent-001.jsonl` ("Not yet assessed; candidate supplied by user"); `SIMS/co2-B/relay/agent-001.jsonl` ("not yet assessed"); `SIMS/retail-A/feedback/agent-notes.md` turn 1.
- **C-63:** `SIMS/taxi-B/project/investigations/airport-trips-and-tipping/state.md` line 37 still reads "Preview the slide headlines with Dana before drafting the package". It was added in commit `412d7d9` and kept through headline approval (`8439222`) and release.

**Cause in the release.**
- `awb-clean/SKILL.md:10` against `awb-init/assets/workbench/AGENTS.md` Procedures; `awb-clean/references/correction-views.md:43`.
- `awb-init/assets/awb_provenance.py:1900` (`_ANSWERERS = ("user", "stakeholder", "data")`) and `:2220-2223`.
- `workbench-guides/analysis.md:11` and `investigation/settings.toml:14-15`.
- `awb-package/SKILL.md:24`, `:28`, `:30`, and `:17` against `:49`.
- `awb-init/SKILL.md:26` ("Do not interview here") and `:48` (scope's first round before the investigation exists). `awb-scope/SKILL.md:44` and `:57` (adapt the templates by hand). `README.md:46` and `:48` (put everything in the first message).
- `awb_provenance.py:2414-2432` (`questions add` and `answer` take one item), `:1727-1729` (one result for `--text`), `:1551-1554` (placeholder text on every new row). `awb_mcp.py:166-172`. `awb-scope/SKILL.md:47-52`.
- `awb-init/assets/workbench/foundation/sources.md` line 16 and `awb_landing.py:726` (the basis prefix). `collect_status.py:305-310`. `awb-init/SKILL.md:41` (register a candidate source at setup).
- `awb-release/SKILL.md` (no state step); `awb-package/SKILL.md` (no Next steps rule); `AGENTS.md:48`; `collect_status.py:267` and about line 948.

**Fix direction.**
1. Resolve each listed conflict in text: an `awb-clean` publish branch that names the data guide, a documentation answerer, a rule for derived-check questions, conditional step 1 questions, a review-rule offer for pre-draft corrections, and accurate wording about which step creates the draft folder.
2. Add a create-investigation command, and give a settled first brief a defined holding place before scope finishes.
3. Accept lists in `questions add`, `questions answer` and `state finding --text`.
4. Add a candidate-stage basis wording that status accepts.
5. Retire finished next steps at headline approval, draft and release, and have status compare next steps with the latest release.

---

## Issue 10: awb-status reports

**Severity.** Minor.

**Closes.** C-30, C-67.

**Problem.**
- **Counts users cannot map, and a skipped per-question screen (C-30).**
  - The Findings item opens with `active.counts`, which counts every recorded calculation: intake, reconciliation, sensitivity and reference results included.
  - A finding stays provisional until the user approves its headline, so supporting checks stay provisional for good.
  - A result can never be unlinked from a question, and superseding one sends the question to "awaiting recheck".
  - `by_question` folds sub-question checks into the user's question, so even a compliant report confuses.
  - When status shared a message with other work, which the README says is supported, agents of both models left out the per-question list and the suggested requests.
- **A hand-written history entry dates the state (C-67).** The freshness check exempts only `state.md` and the question ledger. A hand-written history entry, which `AGENTS.md` asks for after a caveat or method change, made a second or more after the last state write reads as "out of date", although the state already reflects it. The one-second gap is incidental.

**Evidence.**
- **C-30:**
  - `SIMS/taxi-A/transcript.md` line 426: "nine supported findings and two provisional reference calculations". The user could not map 11 results to 5 questions (`SIMS/taxi-A/feedback/human.md`).
  - `SIMS/retail-A/transcript.md` reply 5: "seven supported and seven provisional findings". Msg 6 asks "What are the 14?".
  - The collector's `by_question` in `SIMS/retail-A/relay/agent-005.jsonl` totals 7 and 7, with Q-001 at 2 supported and 4 provisional.
  - taxi-A's superseded reference results sent Q3 and Q5 to awaiting recheck (`SIMS/taxi-A/feedback/agent-notes.md`, verify-Q3 entry).
  - co2-A gave status as prose (`SIMS/co2-A/transcript.md` reply 5).
- **C-67:** `SIMS/co2-A/relay/agent-004.jsonl` runs two `state finding` calls (07:32:49), then a hand append to `history.md` (07:32:50). In `agent-005.jsonl` status reports `state_status` "out of date" while `stale` checked 9 of 9 results current. The agent did not pass the warning to the user.

**Cause in the release.**
- `awb-status/SKILL.md:29` (`active.counts` first), `:26` (one screen), `:38-40` (the "You can ask for" list) and `:10` (other requests after the report).
- `awb-status/scripts/collect_status.py`: the active block counts every findings row; `results_under` folds child questions.
- `README.md:84-85` (the one-screen promise) and `:97` (provisional until headline approval); `investigation/state.md:10`.
- `awb_provenance.py`, the answer function (about lines 2200-2245): results can only be added to a question.
- `collect_status.py`, the exempt list (about line 951), `order()` (lines 1000-1006) and `:1011-1014`.
- `AGENTS.md:48`: write history by hand for scope, method, caveat or data changes.
- `awb-status/SKILL.md:51`: "out of date" becomes the risk request "Update the investigation state".

**Fix direction.**
1. Lead with each question and the findings that answer it. Give supporting and reference results a role that keeps them out of provisional counts. Let a superseded reference result be unlinked.
2. Keep the per-question screen when status shares a message with other requests.
3. Exempt hand-written history entries from the freshness check, or add a command that writes a history entry and restamps the state together.

---

## Issue 11: README

**Severity.** Minor. Docs only.

**Closes.** C-14.

**Problem.**
- **Length.** The README is 4,718 words. About 1,500 words of install, MCP and How it works material share the file with a roughly 3,000-word analyst section, with no short analyst path. Four of six users called it long; five of six wanted the install material moved out.
- **Mechanism over effect.** Items 6 and 7 (checkpoint modes, review problems) explain mechanisms rather than effects. Nothing gives an example of how small a problem can trigger the second-review stop, or says that adding a review rule forces another review.
- **Gaps.** The glossary never defines an investigation. Nothing warns that `findings.md` is a long builder outline.
- **The no-data promise.** Line 54's "Setup and the scoping round bring no data in" is not backed by `awb-init`. taxi-A's agent landed files at setup, against `awb-init/SKILL.md:10` and `AGENTS.md:38`. One skeptic judged this an agent miss rather than a release gap, since no other run landed at setup.

**Evidence.** Section 3 of `SIMS/<run>/feedback/human.md` in all six runs; turn-1 notes in each run's `human/notes.md` (for example `SIMS/taxi-A/human/notes.md` turns 1, 2 and 8). `SIMS/taxi-A/relay/agent-001.jsonl` lands both sources in reply 1, and the user asks in msg 3 whether the data is "in".

**Cause in the release.**
- `README.md`: 4,718 words, with install and administer at lines 122-188.
- `README.md:54` (no data at setup), `:69-70` (items 6 and 7), `:94-100` (the glossary has no "investigation"), `:13` (findings.md as the outline), `:99` (R-periods-001), `:105` (commits).
- `awb-package/references/review.md:39`: a rules change makes the review stale, which the README does not say.

**Fix direction.** Move install and administer to their own file, linked from the top. Open with a short analyst path. Define an investigation. Rewrite items 6 and 7 by effect, with one example of a stop and a note that a new rule forces one more review. Describe `findings.md` as the builder's outline. Either back the no-data promise in `awb-init` or soften it.

---

## Recommended order

1. **Issues 1 and 2 together or back to back.** Both edit `awb-package/references/review.md`, and the review gate is the maintainer's main question.
2. **Issue 4.** It moves the reviewer's style rules into the writer's checklist, which depends on what Issue 1 keeps.
3. **Issues 3, 5 and 6.** Independent of each other.
4. **Issues 7, 8, 9 and 10.** Independent and minor.
5. **Issue 11 last,** so the README describes the behavior the other PRs settle.

---

## Contested findings

The two skeptics split on these, so none is proposed. "Harness lens" asked whether the simulation caused it; "release lens" asked whether the release text causes it. Each entry gives what each found.

- **C-02: Thresholds and exclusions set or proposed after seeing which rows lead** (taxi-A, taxi-B, co2-A, co2-B, retail-B; major).
  - *Harness lens (product):* only taxi-A clearly shows it. The Codex agent noted a plan to propose a zone-trip floor before viewing leaders, skipped it, and showed a top 10 with 1-to-13-trip zones. co2-A never raised a materiality threshold. The B runs proposed thresholds before computing answers or disclosed later proposals, which `analysis.md:13` allows.
  - *Release lens (unsupported):* the rule is clear in `analysis.md:13`, `awb-explore/SKILL.md:51` and `README.md:67`. The two misses are agent non-compliance. Optional hardening: have `awb-scope` ask for a support floor on top-N questions.
- **C-25: Scoping proposals incomplete, mis-scoped or mis-paced** (taxi-B, co2-A, co2-B, retail-B).
  - *Harness lens (product):* the four-decision cap pushes simple, independent choices into an announced second round without recommendations (co2-B, retail-B). taxi-B's first invalid-record rules had no speed rule and counted missing geography as invalid.
  - *Release lens (unsupported):* the cap is deliberate (`README.md:64`, `CHANGELOG.md:157`) and the users answered the deferred items in their next message. The rest is agent judgment or a breach of rules the release already has.
- **C-27: check-draft's pass and fail signals do not match the draft's stage** (taxi-A, retail-B, co2-A, co2-B).
  - *Harness lens (product):* the MCP read tool offers check-draft only as `--verify-only`, which fails before the first writing run and after any edit, and every failure is marked as a tool error.
  - *Release lens (unsupported):* documented behavior. The `passed` key leaves out the review by design, the skill orders the read form for release only, and no agent was misled.
- **C-32: Chat figures, counts and bases misstated** (taxi-A, co2-A, retail-B).
  - *Harness lens (product):* only retail-B holds. Reply 3's headline left out the identified-customer base, and a 90% share of revenue level backed a growth claim. Nothing checks share bases before the draft.
  - *Release lens (unsupported):* agent slips against `AGENTS.md:30`, caught by the headline checkpoint and the review. co2-A's "same ten countries" was accurate. taxi-A's 91.85% was the agent's own double rounding.
- **C-38: Results run before a commit need a commit, a rerun and a re-export** (taxi-B, retail-A, retail-B).
  - *Harness lens (product):* the guides never say to commit before running, and export accepts uncommitted code without saying so, while `analysis.md` and `awb-status` present a rerun as the fix. The first publish happens before any commit and records "uncommitted".
  - *Release lens (unsupported):* nothing requires the cycle. Agents chose it, and the reruns were cheap (about 25 seconds in retail-A).
- **C-42: Release reports restate every caveat, repeat a headline, and can contradict START-HERE** (taxi-A, taxi-B, retail-A).
  - *Harness lens (product):* taxi-B's release chat labelled the outline and chart files "For the board", against START-HERE. `awb-release`'s Report never points to START-HERE.
  - *Release lens (unsupported):* the caveat list is intended and both users valued it. The repeated headline exists only in the raw JSON. The mislabel was the agent's own.
- **C-52: The deliverable is a builder kit, not a rendered deck** (taxi-A, co2-A).
  - *Harness lens (product):* a disclosed scope limit that every user meets. co2-A's "next: build the PowerPoint" did not say who builds it.
  - *Release lens (unsupported):* the README says "It is not a .pptx", and every user accepted it. A feature request.
- **C-53: File links switch to relative paths, including for the release copy** (retail-A, co2-A).
  - *Harness lens (product):* after Codex auto-compaction, retail-A gave the release copy as a relative link, against `awb-release` section 5, which the agent had just re-read. Host drift on a real host.
  - *Release lens (unsupported):* a one-off miss of a clear instruction. Five runs reported the full path. Only the unspecified link form for drafts is a cosmetic gap.
- **C-57: Weekday comparisons are not checked for calendar events** (taxi-A).
  - *Harness lens (product):* nothing prompts a holiday check. The Codex agent missed July 4 and January's holiday Mondays, while taxi-B's Claude agent raised them unprompted.
  - *Release lens (unsupported):* a guidance gap, not a cause. The same agent named holidays as uncontrolled in its own brief. Optional line for `analysis.md`.
- **C-59: Export with `--no-datasets` and no `--chart` deletes every chart** (taxi-A).
  - *Harness lens (product):* there is no pre-write guard, and a flag named for datasets also replaces the chart set.
  - *Release lens (unsupported):* documented in `awb-package/SKILL.md:72` and the export help, which the agent read in the same turn. One full re-export recovered everything.
- **C-60: Answered child questions stay open until linked by hand** (taxi-A).
  - *Harness lens (product):* data questions answered by caveats ("what evidence is missing") have no route to closure, and only the Open questions rule surfaces them.
  - *Release lens (unsupported):* explicit linking is the design, and it is documented in five places. Nothing reached the user.
- **C-64: Status does not check references on rows assessed from landed records** (taxi-B).
  - *Harness lens (product):* status trusts the basis label, and a mixed label such as "from landed records and documentation" skips the reference check.
  - *Release lens (unsupported):* the agent's own replace silently did nothing, and the package reviewer caught it as designed.
- **C-68: The methods-note length line must stand alone in its exact form** (retail-A).
  - *Harness lens (product, low confidence):* the strict parser trips an agent that appends prose. The row is informational.
  - *Release lens (unsupported):* the template and step 1 both give the standalone form. One edit fixed it, and the user never saw it.
- **C-73: Hard-coded row counts instead of `reconcile()`** (co2-B).
  - *Harness lens (product):* `validate()` never compares list-form row counts with the result, so a re-landing would pass with stale counts.
  - *Release lens (unsupported):* an agent shortcut against `analysis.md`, which the agent followed for its other results.
- **C-74: A question only IT could answer, asked without a fallback** (retail-A).
  - *Harness lens (product):* nothing requires a default treatment when only a third party knows what a code means.
  - *Release lens (unsupported):* `AGENTS.md:32` and `awb-clean` step 2 already require a recommendation and an alternative. Agent non-compliance.
- **C-75: A retained public dataset page embeds a third party's email address** (retail-A, and retail-B independently).
  - *Harness lens (unsupported):* the address is already public on the source site. At most a quality issue: agents commit raw HTML with embedded page data.
  - *Release lens (product):* the data guide requires keeping documentation but gives no guidance on capturing a web page or checking it for personal data. Minor.
- **C-76: "Changed on disk" notifications re-show whole files** (retail-B).
  - *Harness lens (harness):* 91% of the reminder text came from the relay restarting the session each turn and from the study's own notes file. Only about 3,800 characters came from helper rewrites.
  - *Release lens (product):* helpers rewrite `state.md` whole after the agent has written it by hand, so each rewrite re-shows the file. Minor.
