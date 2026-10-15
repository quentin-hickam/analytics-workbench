

## [2026-10-15T12:39:44Z] HUMAN (Codex) message (turn 1)

Use awb-init to initialize this analytics project. I lead research at Carbon Ledger Initiative. In ten days, I need about eight slides and a methodology note for semi-technical donors deciding which countries our next two-year program should focus on.

Use Our World in Data’s CO2 dataset:
- Data: https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv
- Codebook: https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-codebook.csv
- Documentation: https://github.com/owid/co2-data

I need five questions answered:
1. Which 10 countries had the largest absolute increases in annual territorial CO2 since 2000, and which 10 had the largest decreases?
2. How many countries reduced territorial CO2 while growing GDP since 2005, through the latest year with both measures? Which are largest by emissions?
3. For the US, China, India, and EU-27, how do consumption-based and territorial CO2 per person compare in the latest available year?
4. What shares of cumulative global CO2 since 1850 come from those four?
5. Among countries emitting at least 50 million tonnes in 2010, where has coal’s share of CO2 fallen fastest since then?

Use fossil CO2 including cement, excluding land-use change. Exclude regional and income aggregates from country rankings, and state the years used.

Keep original data at `SIMS/co2-B/storage/landed/` and released packages at `SIMS/co2-B/storage/releases/`.

STATUS: CONTINUE


## [2026-10-15T12:45:07Z] AGENT (Opus) reply

The workbench is set up and your first investigation, `program-country-focus`, is created and active. I haven't downloaded the data or run any analysis yet. I need a few decisions from you first, listed at the end.

**Project folder:** `.../sims/co2-B/project/`. It had nothing in it, so I created a new local Git repository there. Nothing is committed yet.

**What I created**
- **Project files:** `README.md`, `AGENTS.md` and `.gitignore`. The README records where original data goes (`storage/landed/`) and where released packages go (`storage/releases/`). I added a short section to `AGENTS.md` saying the analysis runs with `.venv/bin/python`, because the system `python3` doesn't have duckdb.
- **Helpers:** the workbench helpers are in `src/`, the guides in `workbench-guides/`, and `requirements.txt` lists duckdb and pandas. The installer reported every file as installed.
- **Python environment:** I created `.venv` (Python 3.12) and installed the packages into it myself. The install command the installer printed uses `pip`, which this kind of environment doesn't include, so I used `uv pip install --python .venv/bin/python -r requirements.txt` instead.
- **Source register:** `foundation/sources.md` lists the OWID CO2 dataset as a candidate. I checked it against the documentation, and it has what all five questions need. The codebook and README are saved under `foundation/references/owid-co2/` for citation (CC BY 4.0).
  - The `co2` column is annual CO2 excluding land-use change, and it includes cement, flaring and other industry. That matches your definition.
  - OWID's own cumulative column starts in the 1750s, so for question 4 I'll add up annual emissions from 1850 instead.
- **Glossary:** `foundation/glossary.md` defines territorial CO2, consumption-based CO2, and "country" (aggregates excluded).
- **Investigation:** `investigations/program-country-focus/` holds:
  - the brief, which records your five questions, the audience (semi-technical donors), the eight slides plus methodology note, and the 2026-10-25 due date;
  - the state, history and run script;
  - settings for each question's start year and the 50 Mt threshold;
  - a list of 15 open questions.

**Left for later:** the data folders, `foundation/views/`, the catalog, the quality record and dataset checks. Each will be created once it has real content.

**Optional: the `awb` server.** It isn't registered in this agent host. To register it, merge the `awb` entry that `install_helpers.py --mcp-config claude` prints into `agent-home/.claude.json`. The host needs a restart to pick it up, so I'll keep using the command-line helpers for now.

**Open questions**
- **For the data (7):** your five questions; which OWID entries are aggregates; and the latest year available for CO2, consumption CO2, GDP and coal.
- **For you (8):** the four below now, plus three method choices I'll bring next round:
  - the decoupling definition, and which year ranks "largest by emissions" (question 2);
  - whether "coal share fallen fastest" means the biggest percentage-point drop (question 5);
  - which global total to divide by for the since-1850 shares (question 4).

  There is also one lower-priority question: what else donors weigh when picking countries.

**The decisions I need now:**
1. **Recommendation or evidence?** Should the deck end by recommending a shortlist of focus countries, or lay out the evidence for donors to choose? I recommend the evidence, plus a short "countries that stand out on several measures" slide: it serves the donors' decision without baking in a scoring scheme they haven't agreed to.
2. **How to measure "since 2000/2005/2010":** compare single years (the start year against the latest year), or average a few years at each end? I recommend single years with the years stated, since that's what you asked for and it's easiest to explain. I'd note any country where one unusual year changes its rank.
3. **What counts as a country:** every OWID entry that isn't an aggregate (including Taiwan, Hong Kong, Kosovo and dependent territories), or UN members only? I recommend every non-aggregate entry. It matches OWID's own country lists, and the small territories barely affect rankings measured in absolute tonnes.
4. **Year for question 3:** compare the US, China, India and EU-27 in one shared year where consumption data exists for all four, or each in its own latest year? I recommend one shared year so the comparison is like-for-like. Consumption data likely ends a year earlier than territorial.

Once you answer, I'll download the OWID CSV into `storage/landed/` and build the dataset the analysis will use.

Questions: opened 15 (8 need you) · next: your answers on Q-001 to Q-004, then load the OWID data.


## [2026-10-15T12:45:27Z] HUMAN (Codex) message (turn 2)

Those four recommendations work: evidence plus countries that stand out, single-year comparisons, all non-aggregate countries and territories, and one shared year for question 3.

For the remaining method choices:
- Question 2: CO2 must fall and real GDP must rise between 2005 and the latest common year. Rank the qualifying countries by emissions in that ending year.
- Question 5: use the largest percentage-point decline in coal’s share, and show starting and ending shares.
- Question 4: divide by OWID’s World emissions summed from 1850 through the same ending year as the four contributors.

Donors will also consider policy opportunity and our ability to make a difference. These data can identify candidates, but cannot establish those factors alone.

Please proceed with the download, data checks and analysis. Keep updates focused on findings and decisions I need to make; the technical setup details can stay in the project records.

STATUS: CONTINUE


## [2026-10-15T12:56:00Z] AGENT (Opus) reply

All five questions now have answers from the OWID data, using your method choices. I downloaded the data and kept the original in `storage/landed/`. Every validation check on the results passes. The measure throughout is territorial CO2 (fossil fuels plus cement, excluding land-use change). "Countries" means every entity in the data that isn't a region or income group, Kosovo included.

**Years used:** CO2 and coal run to 2024, consumption-based CO2 to 2023, and GDP to 2022. So question 2 ends in 2022 and question 3 uses 2023.

**1. Biggest changes in annual CO2, 2000 → 2024**
- **Increases:** China +8,645 Mt, India +2,206, Indonesia +531, Iran +425, Saudi Arabia +382, Vietnam +317, Russia +300, Turkey +280, Malaysia +167, Iraq +150.
- **Decreases:** United States −1,119 Mt, Germany −327, Japan −298, UK −256, Italy −168, France −143, Ukraine −143, Spain −89, Netherlands −57, Czechia −52.
- **Caveats:** Russia's 2000 starting point was a post-Soviet low. Ukraine's 2024 figure reflects the war.

**2. CO2 down while GDP grew, 2005 → 2022**
- 45 of the 164 countries with both measures qualify.
- **Largest by 2022 emissions:** US (5,055 Mt), Japan, Germany, Canada, Mexico, Australia, Italy, Poland, UK, France.
- **Caveat:** several of these only just qualify. Australia's CO2 fell 0.3%, Mexico's 2.1%, Poland's 2.4% and Canada's 4.0%.

**3. Tonnes of CO2 per person, 2023 (consumption-based vs territorial)**

| | Consumption-based | Territorial | Difference |
|---|---|---|---|
| United States | 15.8 | 14.3 | +10% |
| EU-27 | 7.3 | 5.5 | +33% |
| China | 7.6 | 8.6 | −11% |
| India | 1.8 | 2.1 | −17% |

The US and EU consume more CO2 through imports than they emit at home. China and India are the reverse.

**4. Share of world CO2, 1850–2024**
- US 23.6%, EU-27 16.3%, China 15.5%, India 3.6%.
- Together that is 58.9%.

**5. Fastest fall in coal's share of CO2, 2010 → 2024 (countries over 50 Mt in 2010)**
- **Biggest falls:** Greece (42% → 9%, −33 points), Romania −23, Israel −22, Poland −19.5, United States −19.4, Finland −19, Czechia −18, UK −18, Hungary −13.5, Germany −13.
- **Biggest rises:** Vietnam (34% → 62%, +28 points), Indonesia, the Philippines, Bangladesh and Pakistan.
- **Gap:** Libya passes the 50 Mt bar but has no coal figures in the data, so it isn't ranked.

**Countries that stand out (my tentative list, not yet a recorded result)**
- **Large reducers:** the US, Germany and the UK each appear in three rankings. Japan, Italy, France, Poland and Czechia each appear in two.
- **Fast-growing, increasingly coal-heavy emitters:** Indonesia and Vietnam each appear in two rankings.

For a two-year program, the second group, plus India, may be where donors see the most room for policy work. As you said, the data can only identify candidates; it can't show policy opportunity or your ability to make a difference.

**Decision needed:** should the stand-out slide name countries that appear in two or more rankings, split into "large reducers" and "fast-growing coal-heavy emitters"? Once you confirm or adjust the rule, I'll make it a recorded result.

Nothing is committed yet, so the results aren't tied to a fixed version of the code. I'd suggest a commit before drafting the deck. Say the word and I'll commit, then draft the eight slides and the methodology note.

Questions: answered 15 · opened 1 (needs you) · next: confirm the stand-out rule, then commit and draft the package.


## [2026-10-15T12:56:20Z] HUMAN (Codex) message (turn 3)

Use awb-status — where are we?

The five answers look suitable for the draft. For the final slide, use “Countries for further assessment,” with separate groups for experience in reducing emissions and growing emissions with rising coal dependence. Explain exactly which rankings support each country; counting appearances alone feels arbitrary. Include India because of its absolute emissions growth, with that rationale stated separately. Avoid implying these data establish where our program would have most impact.

For consumption emissions, describe the difference as net emissions embodied in trade. The current wording could sound as though imported emissions exceed all domestic emissions.

Please commit the analysis and use awb-package to draft the eight-slide package, methodology note and supporting chart data. Include the full ranked answers and country coverage rules in the supporting material, including how aggregates were identified. Point me to the files I should review.

STATUS: CONTINUE


## [2026-10-15T13:04:16Z] AGENT (Opus) reply

**Where we are:** the analysis is done and committed (latest commit 8b22b14 plus two follow-ups). Your five questions and the final-slide selection are recorded as findings that pass validation. Nothing in the ledger is open, the original data is kept in `storage/landed/`, and no package exists yet.

**Changes since last time**
- **Final slide, "Countries for further assessment":** each country is listed with the exact rankings that place it there.
  - **Experience reducing emissions:** top 10 in at least two of three rankings: biggest decreases since 2000 (Q1), CO2 down while GDP grew (Q2, ranked by 2022 emissions), and biggest coal-share declines (Q5).
    - United States: Q1 decrease #1, Q2 #1, Q5 #5.
    - Germany: Q1 #2, Q2 #3, Q5 #10.
    - United Kingdom: Q1 #4, Q2 #9, Q5 #8.
    - Japan (Q1 #3, Q2 #2), Italy (Q1 #5, Q2 #7) and France (Q1 #6, Q2 #10).
    - Czechia (Q1 #10, Q5 #7) and Poland (Q2 #8, Q5 #4).
  - **Growing emissions with rising coal dependence:** top 10 in absolute increase since 2000, and coal's share of CO2 up at least 5 points since 2010.
    - Indonesia: increase #3, coal share +19.4 points.
    - Vietnam: increase #6, +27.8 points.
    - Malaysia: increase #9, +5.9 points.
    - India: increase #2, +5.5 points.
  - **India:** it meets the coal rule anyway, but only narrowly. The slide also states its separate reason: the second-largest absolute increase.
  - **Threshold check:** the "two of three rankings" and "at least 5 points" cutoffs are my choices, so please confirm them. Turkey, Saudi Arabia and Iraq are among the top-10 increases, but their coal share barely moved (under 0.1 point), so the 5-point cutoff leaves them out.
- **Consumption wording:** now framed as net emissions embodied in trade. In 2023 the US was a net importer (+1.5 t per person) and the EU-27 too (+1.8 t). China (−0.9 t) and India (−0.4 t) were net exporters.
- **Full rankings for the supporting data:** I added the complete Q1 ranking, all 216 countries. I also added a top-10 table for the Q5 chart, because a chart has to plot a whole table and the full ranking has 59 rows.

**Draft package, paused at headline approval.** The package tool requires headline approval before it writes the full slides. So there are no draft files to review yet. Proposed headlines in order:

1. *Title:* Where CO2 is rising, falling and shifting — evidence for our next program's country focus
2. *Answer:* Most emissions growth since 2000 is in Asia; 45 countries cut CO2 while growing.
3. China's annual CO2 rose 8,645 Mt since 2000; the US fell most, by 1,119 Mt.
4. 45 of 164 countries cut CO2 while GDP grew from 2005 to 2022.
5. Net trade adds 1.8 t per person to EU-27 consumption emissions, but lowers China's.
6. The US, EU-27, China and India emitted 58.9% of all CO2 since 1850.
7. Greece cut coal's share of CO2 by 33.3 points since 2010; Vietnam's rose 27.8.
8. Countries for further assessment: eight with reduction experience, four with rising coal dependence.
9. *Implications:* Emissions data narrow the field; policy opportunity and our reach must decide.
10. *How we know:* Every figure is recomputed from one dated OWID download, with aggregates removed and totals reconciled to World.
11. *Limitations:* The main limits are single-year endpoints and GDP data that ends in 2022.
12. *Supporting datasets:* Eight tables let donors check every ranking and coverage rule.

**Supporting datasets (proposed):**
- the full Q1 ranking;
- all 45 Q2 countries;
- the Q3 and Q4 tables;
- the full Q5 ranking;
- the further-assessment table with its supporting rankings;
- the entity classification (which 35 entries were treated as aggregates or non-countries, and why);
- the latest-year coverage table.

**Charts (proposed):**
- Q1: bars for the 10 biggest increases and 10 biggest decreases.
- Q3: territorial vs consumption-based per person.
- Q4: shares table.
- Q5: coal share in 2010 vs 2024 for the top 10.
- Q2: no chart; the top 10 go in bullets, since 45 bars won't read.

**Decisions needed:**
1. Approve or reorder the headlines above.
2. The package format requires the Implications, How we know, Limitations and Supporting datasets slides, which brings the deck to 12. Which do you prefer?
   - **Keep slides 1–8 as the eight-slide core and treat 9–12 as an appendix** (my recommendation).
   - Merge slides 5 and 6 into one "four largest economies" slide.
3. Confirm the two cutoffs on the further-assessment slide.

**Files to review now:**
- Findings with their caveats: `investigations/program-country-focus/state.md`.
- The underlying tables: `investigations/program-country-focus/results/*.csv`.
- Country coverage: `results/entity-classification.csv`, plus the rule in `foundation/views/02_owid_co2_entities.sql`.

Questions: answered 1 · findings: added 3, reworded 1 · next: your approval of the headlines and slide count, then I write the slides, methodology note and chart files.


## [2026-10-15T13:04:41Z] HUMAN (Codex) message (turn 4)

Approved: eight core slides, with slides 9–12 as an appendix. The proposed order works, with these adjustments:

- Slide 2: replace “Most emissions growth … is in Asia” with the directly supported finding that China and India had the largest absolute increases. State the 2005–2022 period for the 45-country result.
- Slide 6: specify “global fossil CO2, including cement, 1850–2024.”
- Slide 8: label the selection as illustrative. I accept your two cutoffs for organizing further assessment; explain them in the methodology, without presenting them as a priority score.
- Put Q2’s top ten in a compact table with emissions and percentage changes in CO2 and GDP.

Please explain country classification in plain language in the methodology note; I won’t review SQL.

Go ahead and write the full draft now, including the appendix and supporting files. I need to review the actual package before release.

STATUS: CONTINUE


## [2026-10-15T13:29:23Z] AGENT (Opus) reply

The full draft package is written and ready for your review. It passes the automated checks, and a separate read-only reviewer now reports it clean. Getting it clean took four review rounds. The fixes changed wording only; no numbers changed:
- **Your corrections as standing rules:** I recorded them so every future draft is checked against them. They cover years named beside every figure, no regional generalizations, the "net emissions embodied in trade" wording, never implying where the program would have most impact, and stating the measure.
- **Descriptive wording:** "countries cut CO2" became "CO2 fell in…", since the data describe what happened, not who acted.
- **Claims removed:** two the results don't support. One was that domestic emissions are the larger part of each consumption-based total; the data only give the net trade balance. The other was a "Western Europe" generalization.

All files are under `deliveries/program-country-focus/donor-country-focus/draft/`. Please review these:

1. **`findings.md`** is the deck outline: every slide's headline, bullets, chart specification and speaker notes. I've also sent it to you as an attachment.
   - **Core (slides 1–8):**
     - title;
     - answer: China and India led CO2 increases from 2000 to 2024, and CO2 fell as GDP grew in 45 countries from 2005 to 2022;
     - one slide per question, 1 to 5;
     - "Countries for further assessment, illustrative", which gives each country its supporting rankings, lists India's separate rationale, and says the cutoffs don't rank countries.
   - **Appendix (slides 9–12):** Implications, How we know, Limitations, Supporting datasets.
   - **Q2 table:** the top ten are in a compact table with 2022 emissions and the percentage changes in CO2 and GDP.
2. **`methodology.md`** is the methodology note, also attached. It includes the plain-language explanation of how countries were identified: an entry counts as a country if it has an international three-letter code, plus Kosovo. The 35 entries without a code are regional, income-group or world totals, or non-country entries such as international aviation and shipping. It also explains the two cutoffs as rules for organizing further assessment, not a priority score.
3. **`charts/chart-1.csv` to `chart-5.csv`**: Q1 increases and decreases, the Q2 table, Q3 per-person comparison, Q4 shares, Q5 coal share 2010 vs 2024.
4. **`datasets/`**, eight tables:
   - full Q1 ranking (216 countries);
   - all 45 Q2 countries;
   - the Q3 and Q4 tables;
   - full Q5 ranking (59 countries);
   - further-assessment table with supporting rankings;
   - country classification (the 35 excluded entries);
   - latest year available for each measure.

**Things to check while reviewing:**
- **Appendix marking:** the outline format has no appendix divider, so the appendix is marked only in the speaker notes of slides 9–12. Whoever builds the deck will need to put those four slides after an appendix break.
- **Q2 table size:** it has 30 numbers, more than the deck rules suggest for a table. I kept it because you asked for it.
- **Package name:** I named it `donor-country-focus`.
- **Unlinked final slide:** the further-assessment slide isn't tied to any of the five data questions in the ledger, so the check lists it as unlinked. That's expected, and it's why it sits last.

**Building the deck:** in a Microsoft 365 Copilot chat, add the PowerPoint agent. Attach `findings.md`, every file in `charts/`, `methodology.md`, `deck-rules.md` and `assembly/m365.md`, and ask it to build the deck under those instructions. The datasets go alongside the deck and are not attached.

This is a working draft that the next revision overwrites. When you're satisfied, ask me to mark it delivered and I'll freeze it as release 001 in `storage/releases/`. Corrections go through a package revision first.

The analysis is committed. The draft itself is excluded from Git by design and is preserved when it's released.

Records: 5 review rules added, 1 result added (the Q2 table), display names set · next: you review the draft, then revise or release.


## [2026-10-15T13:29:48Z] HUMAN (Codex) message (turn 5)

I’ve read findings.md and methodology.md. The storyline works, and the five quantitative answers are covered. Please make these corrections before release:

- Mark slides 9–12 visibly as “Appendix” in their headings, so the deck builder doesn’t have to infer it from notes.
- For cumulative emissions, distinguish missing records from measured zero. Show the historical coverage for each contributor and remove “matters little because early emissions were small” unless you can substantiate it.
- Clarify the World reconciliation: which non-country entries are added, and which duplicate entries are excluded? The current wording sounds as though the Kuwaiti oil fires are counted twice.
- Add a brief rounding note: differences use unrounded values, so displayed endpoints may not subtract exactly.

Please also put a short plain-language methods summary before the technical audit detail. Keep the Q2 table as requested.

Send me the revised wording for the historical coverage and reconciliation points when the package is ready.

STATUS: CONTINUE


## [2026-10-15T13:39:19Z] AGENT (Opus) reply

The revised package is ready for review. It passes the automated checks and a fresh read-only review came back clean. I've attached both narratives again.

**Your reconciliation question turned up an error, now fixed.** The first draft said country totals plus all non-country entries add up to the world total. I had only checked that in six sample years. Checking every year showed that adding the Kuwaiti oil fires entry overshoots the world total by 478 Mt in 1991, because Kuwait's own 1991 figure already includes those emissions. No ranking or share changes: rankings use countries only, and the shares divide by the world total directly. The methodology note now records this under Methodological corrections, and the project records are updated to match.

**Revised wording on historical coverage (Q4 slide):**
- "Coverage, 1850 to 2024: the United States and EU-27 have records for every year; China's records start in 1907 (57 years missing) and India's in 1858 (19 years missing, including later gaps)."
- "A missing year adds nothing to a total and is not a recorded zero; even if China had emitted all the world's CO2 in its missing years, its 1850 to 2024 share would rise by at most 2.9 points, and India's by at most 0.5."
- I removed "matters little because early emissions were small". The speaker notes now explain that the bound gives every tonne the world emitted in those years to the contributor, so the true effect can only be smaller. None of the four has a year recorded as zero.
- Chart 4 now also shows each economy's first year with data and its missing years.

**Revised wording on the reconciliation (How we know slide):**
- "Check: in every year from 1850 to 2024, country totals plus international aviation and shipping and the historical Ryukyu Islands entry equal the world total within 0.011 Mt; a separate Kuwaiti oil fires entry is left out because Kuwait's 1991 figure already includes it."
- The speaker notes say the same in plainer terms. Aviation, shipping and Ryukyu are added when checking against the world total; the oil fires entry is not, because adding it would count those emissions twice.

**Other changes**
- **Appendix:** slides 9–12 now start their headlines with "Appendix:".
- **Rounding note** (How we know slide and methodology): "differences and shares use unrounded values, so displayed figures may not subtract or add exactly."
- **Plain-language summary:** the methodology note now opens with "Methods in brief" before the technical audit detail.
- **Q2 table:** kept as you asked.
- **Standing rules:** your corrections on the appendix marking, missing versus zero, and the rounding note are now checked on every future draft.

**Files to review** are in `deliveries/program-country-focus/donor-country-focus/draft/`:
- `findings.md`
- `methodology.md`
- `charts/chart-4.csv`, which now has the coverage columns
- `datasets/q4-cumulative-shares.csv`, which now includes coverage and the bound

**Decision needed:** should the year-by-year reconciliation table (175 rows) go in as a ninth supporting dataset? It's recorded but not exported, because the dataset list is your call.

When you're satisfied, say "mark this package delivered" and I'll freeze it as release 001 and copy it to `storage/releases/`.

Records: 1 result added (world reconciliation), 2 findings reworded, 3 review rules added, 1 correction recorded · next: your review, then release.


## [2026-10-15T13:39:44Z] HUMAN (Codex) message (turn 6)

I’ve reviewed the revised wording and coverage tables. The historical gaps and reconciliation are now clear. I accept all five answers with the documented caveats.

Include the year-by-year reconciliation as a ninth supporting dataset and update the supporting-datasets count accordingly.

Use awb-release — mark this package delivered as release 001 and copy it to the recorded releases folder. Please confirm the final location and that the copy succeeded.

STATUS: CONTINUE


## [2026-10-15T13:48:11Z] AGENT (Opus) reply

Release 001 is delivered and the copy in your releases folder succeeded: all 19 files were compared against the local release and match.

**Final location:**
`SIMS/co2-B/storage/releases/program-country-focus/donor-country-focus/released/001/`

A matching frozen copy is in the project at `deliveries/program-country-focus/donor-country-focus/released/001/`, released 2026-10-15 at 09:43.

**What's in it:**
- `findings.md` (deck outline) and `methodology.md` (methodology note).
- `deck-rules.md` and `assembly/m365.md`, the deck-builder instructions.
- `charts/chart-1.csv` to `chart-5.csv`.
- `manifest.json`, which records the files, their checksums and what produced them.
- Nine supporting datasets:
  - the full Q1 ranking;
  - all 45 Q2 countries;
  - the Q3 and Q4 tables (Q4 with historical coverage);
  - the full Q5 ranking;
  - countries for further assessment;
  - country classification;
  - data coverage years;
  - the new year-by-year world reconciliation, 1850–2024. It shows the entries added, the Kuwaiti oil fires entry that is left out, and the difference each year.

**Ninth dataset:** the Supporting datasets slide now says "nine tables" and describes the reconciliation table. To label that table correctly I had to rename one column in the underlying result, because its world total had been picking up the cumulative 1850–2024 label from the Q4 table. Nothing else changed.

**Checks:**
- **Review:** a fresh review before release came back clean against all eight standing rules.
- **Automated checks:** passed on the final files.
- **Caveats:** no finding carries a pending caveat.
- **Provenance:** every result traces to a single commit with no uncommitted changes.
- **Original data:** it is also held in `storage/landed/`, not just in this project folder.

**Building the deck:** in a Microsoft 365 Copilot chat, add the PowerPoint agent. Attach `findings.md`, every file in `charts/`, `methodology.md`, `deck-rules.md` and `assembly/m365.md` from `released/001`, and ask it to build the deck under those instructions. The datasets travel alongside the deck and are not attached.

Release 001 is frozen. Any later change goes through a new package draft and becomes release 002.

Records: 1 release made, 1 dataset added, 1 result column renamed · next: build the deck from release 001.


## [2026-10-15T13:48:26Z] HUMAN (Codex) message (turn 7)

Release 001 is accepted. The five questions are answered, the reviewed package is delivered, and the storage copy is confirmed. I’ll use the released files for PowerPoint assembly.

STATUS: DONE


## [2026-10-15T13:49:44Z] HUMAN (Codex) message (turn 8)

DONE
