# User feedback: Priya Natarajan, head of e-commerce (retail-A)

## 1. Did I get what I needed?

Yes. The agent answered all five questions with specific figures I would put in front of leadership. I asked for status once and got a clear answer. I reviewed a draft package, asked for corrections, and release 001 now sits in my releases folder. The session took 10 turns from setup to release, which is quick for this much analysis.

**Satisfaction: 8/10.** The analysis was strong and careful. I took points off because the deliverable is not a deck: it is a slide outline plus chart data that I still have to send through Microsoft 365 Copilot. The methodology note was also unusable for my audience until I asked for a summary.

**Would I use it again?** Yes, for the next quarterly or board analysis, provided I have Copilot to build the slides. Without Copilot I would hesitate, because I would end up building eight slides by hand from a markdown file.

## 2. Top pain points, ranked

1. **No actual PowerPoint (major).**
   - **When:** turn 8, when the "full draft" arrived. The agent said: "This is a working content package. To build PowerPoint, use the Microsoft 365 Copilot PowerPoint agent."
   - **The problem:** I had asked for "about 8 slides". The README mentions this in one dense sentence, but I didn't take it in. If I didn't have M365 Copilot, this would block me.
   - **What would have helped:** a plain statement near the top of the README that the workbench produces a slide outline and chart data, not a .pptx, and that you need the Copilot PowerPoint agent or a manual build. The agent should also say this during scoping, when I first mention slides, not at the end. The list of seven files and the copy-paste Copilot instruction should come with the draft automatically; I only got them because I asked.
2. **Methodology note written for auditors, not for my readers (major).**
   - **When:** turn 8.
   - **The problem:** about 4,300 words of "immutable publication", "exact overlap multisets", question IDs like Q-008, backticked check names and JSON file paths. I could not send that to Finance or leadership.
   - **What would have helped:** a one-page plain-English summary at the top by default. The agent wrote a good one in a single turn once I asked.
3. **Agent linked to its own instruction files (minor, repeated).**
   - **When:** turns 3 and 7. It linked the awb-clean and awb-package SKILL.md files to explain why it was asking me something.
   - **The problem:** I don't want to read the tool's rulebook, and it made me feel I was supposed to.
   - **What would have helped:** simply saying "I need your call on X before I continue."
4. **"3 need your context" without saying which three (minor).**
   - **When:** turn 1.
   - **The problem:** I had to guess the questions from a bullet list of "open decisions". I answered what I could and had to ask what else it needed.
   - **What would have helped:** listing the questions for me as numbered questions in the reply.
5. **Unrounded numbers in the Excel exports (minor).**
   - **When:** turn 7. Cells read like 366.89000039169395 and 100.00000000000001.
   - **The problem:** the files looked sloppy.
   - **What would have helped:** rounding by default (pennies, one decimal place for percentages). The agent fixed it once I asked.
6. **Headlines in analyst language (minor).**
   - **When:** turn 7. Examples: "screened cancellation-value rates", "first observed", and a slide 8 headline of "use two tables to check the evidence".
   - **What would have helped:** writing for a non-technical audience from the first pass. I had already said the audience was leadership.
7. **First ranking for question 4 was not usable (minor).**
   - **When:** turn 4. The list was dominated by one-off orders that were placed and reversed.
   - **The problem:** the agent did flag the storage-jar outlier itself, which I appreciated, but still presented the raw list as the answer.
   - **What would have helped:** proposing a more robust "meaningful sales" screen up front, especially once it saw that one order made up 95% of a product's sales.
8. **No real scoping interview (minor).**
   - **When:** turn 1.
   - **The problem:** the README says awb-scope "interviews you". Instead the agent initialized, scoped and recorded open decisions in one go, without asking me anything directly. It worked out because I had front-loaded a lot of detail. A user who opened with a one-line question would probably have had a vaguer investigation.

## 3. The README

- **Install section.** It is impenetrable for a non-programmer: MCP config JSON, symlinks, AGENTS.md precedence, Copilot custom-agent setup. I couldn't tell which steps were mine and which were the agent's or IT's. It needs a short "If you're not technical, ask your IT team or agent to do this" lead-in, or a separate admin guide.
- **The deliverable.** This is the biggest gap. It is described only in one long sentence about "M365 receives the audience-facing findings…". It needs a plain "What you get at the end" section: a slide outline in text, a CSV per chart, a methodology note, a .pptx only via the Copilot PowerPoint agent, and the instruction to give that agent.
- **Jargon with no explanation.** "Canonical views", "validated Parquet datasets", "DuckDB views", "question ledger", "receipt", "assembly file". A two-line glossary, or simply leaving these out of the user-facing Use section, would help.
- **The Use section and phrasings are good.** I used "Use awb-init…", "Use awb-status — where are we?", "Use awb-package…" and "Use awb-release — mark the package delivered" verbatim, and they worked.
- **Storage locations.** It was useful to know the agent would ask where landed data and releases go. Because of that I gave both paths up front and saved a turn.
- **What I did not know I needed to know:**
  - The package stops at a headline checkpoint before writing the slides.
  - The methodology note is a technical reference by default.
  - Exports would not be formatted for Excel use.
  - The release lands four folders deep (`marketing-budget-priorities/leadership-budget/released/001/`).

## 4. The agent's communication

- **Jargon.** Heavy in turn 1: "MCP writes were unavailable, so setup used the local CLI; filesystem policy prevented Git initialization." That left me unsure whether something was broken. It explained clearly when I asked, but it should not have raised it unprompted, or should have added "no action needed". After that, the chat replies were mostly plain, apart from the ledger counters ("Questions: answered 8 · opened 2") and "19 supported findings", which meant little to me.
- **Length.** Replies were long, especially turns 4 and 5, but well structured with tables and bold lead lines. I could skim them. The detailed slide notes are dense but work as speaker notes.
- **Quality of its questions.** When it asked, the questions were good and came with a recommendation, for example the cross-sheet duplicates ("I recommend yes") and the revenue treatment. It asked for few decisions and made sensible defaults. The weak spot was turn 1, where it didn't tell me what it needed from me.
- **Scoping interview.** Effectively absent (see pain point 8). It captured my decision context accurately, but only because I had written it all out.

## 5. Trust in the answers

- **Trusted:**
  - **Q1 (monthly revenue, seasonality):** the monthly figures sum exactly to the annual totals, and the Sep–Nov shares check out.
  - **Q2 (concentration, no-ID revenue):** 54.0% and 14.5% both check against the £18.94m total, and the reconciliation table ties net revenue to the full export.
  - **Q3 (repeat rates):** cohort sizes and the definition were stated clearly, and the agent volunteered that "first observed" does not mean newly acquired.
  - **Q5 (country growth):** it included buyer counts and largest-customer share, so I could see Australia's growth is mostly one customer and the Netherlands is 98% one customer. That is exactly what stops a bad budget call.
- **Trusted after a follow-up:**
  - **The April 2011 dip:** the bridge (two fewer trading days, lower daily sales, more credits) adds up, and April plus May combined being only 2% down is a defensible line. It was honest that it cannot prove the cause.
  - **The December 2010 cohort of 76:** the explanation (short month, mostly returning buyers, more guest orders) is plausible and properly caveated.
- **Did not initially trust:** **Q4 (product cancellation rates).** The first list was distorted by one-off orders that were placed and reversed. The revised screen (at least 20 customers, no single credit over 25% of cancellations) is defensible. The top ten is mostly one range (Cherry Lights), and six of the ten products didn't sell in 2011, so its value for next year's decisions is limited. The agent said so itself.
- **Small credibility knock:** it cited a district council committee PDF as the source for 2011 bank holidays. A gov.uk source would look better in a leadership note.

## 6. Deck package review and release

- **Headline checkpoint.** Seeing the eight headlines before the full write-up was useful; it let me fix the tone cheaply. But the outline file at that stage was just headings under "Answer / Findings / Supporting datasets" labels, and the table in chat was easier to read than the file.
- **Corrections.** All of them (headline rewording, Ireland on slide 6, the 14.5% shown prominently, rounding, the new chart, the methodology summary) were made in one turn each. The agent also narrowed two claims to match the evidence (Australia, Cherry Lights) and told me why, which I appreciated.
- **Coverage.** Two charts across eight slides was thin. I had to ask for the country chart.
- **Release.** Painless: one request, no decisions needed, verified copy in my releases folder. The release includes a build-powerpoint.md, which is good. "Git-history gap remains documented" was noise to me.
- **Files I couldn't place.** The draft folder contains files nobody explained to me (assembly/, deck-rules.md, manifest.json, evidence-selection.md). A one-line "what's in this folder" note would help.

## 7. Wasted turns or time

- **Turn 2:** spent partly on working out what the agent needed from me and asking what the MCP and Git messages meant. That turn could have been avoided.
- **Turn 4:** spent on question 4, which needed a redo that a more robust default would have avoided. The April and December follow-ups in the same turn were legitimate questions from me, not waste.
- **Turns 7 and 8:** partly spent on fixes that should have been defaults for a leadership audience: plain headlines, rounded exports, a summary-first methodology note, and a chart for every evidence slide.
- **Overall:** about 2–3 turns of the 10 were avoidable.

## 8. What worked well

- **Speed:** from cleaning straight to quantitative answers for all five questions in one turn, with internally consistent numbers.
- **Unprompted caveats:** one-off order reversals, customer concentration in Australia and the Netherlands, "first observed" not meaning new, credits not being defect rates, and no spend or margin data.
- **Decision asks:** few, clear, with recommendations, including a sensible revenue treatment backed by a full reconciliation.
- **Questions for other teams:** it named specific questions for IT, Finance and Merchandising rather than vague "further work".
- **Storage:** handled without fuss, with originals and the release copied to my folders and verified.
- **awb-status:** short, honest and actionable: done, open, blockers, next request.
- **Correction turnaround:** every review correction was made accurately in one turn.
