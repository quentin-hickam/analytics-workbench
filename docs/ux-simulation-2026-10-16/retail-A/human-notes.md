# Friction log: Priya Natarajan (retail-A)

## Turn 1
- Read README first. The quick-start was clear about what to put in the first message (question, audience, length, data location, storage folders, checkpoint mode), so I put all of it in.
- Inbox is empty; my data is a web download (ZIP with an Excel workbook). The README says a web address is fine.
- Confusing: the "headline checkpoint" paragraph is dense (preview-and-wait vs draft-then-review, and what happens with each). I picked preview-and-wait because it sounded safer.
- Jargon in the README I don't care about as a user: canonical view, receipt, disposition, MCP server. Most of the install section is irrelevant to me but sits in the same doc.
- Asked for: setup, then the scoping round. Expect: scoping questions (up to 4), likely about non-product stock codes, cancellations, and the period.

## Turn 2
- Setup worked, and four scoping questions came back, each with a recommendation. That matches the README. The questions were sensible and in business terms. Good.
- Friction: the reply quotes and links an internal SKILL.md path ("../agent-home/.agents/skills/awb-init/SKILL.md") twice to explain why it is waiting. As a user I don't need that and won't open it. It read like the tool explaining its own rules to me.
- Friction: the same four questions appear twice (once in full, once as a summary). Wordy.
- Surprise: it never asked about non-product stock codes (postage, manual adjustments, fees), even though they affect revenue. I raised it myself and asked for its recommendation.
- Answered all four: ranked priorities; customer basis OK; £10k threshold; absolute growth ranking. Added a hypothesis: retention pays better than acquisition, because most of our customers are repeat wholesale buyers.

## Turn 3
- The agent did a lot in one turn: landed the data, found the 1–9 Dec 2010 overlap between the sheets (22,523 lines, a good catch I didn't know about), gave a revenue recommendation, ran all five analyses, and wrote a headline preview. Fast and impressive.
- It never ran a separate clean or explore step, which the README lists as steps 3 and 4. Unclear whether that matters. It did report data checks inline.
- Problem: it says "5 answered", but I don't have the actual numbers for most questions. There is no monthly figure for Q1, no 2010 month-by-month repeat rates for Q3 (only 43% overall), only one product for Q4, and no growth figures for Q5. Q2 gives the top-10% share of identified revenue, but I asked for the share of net revenue, and guest sales came as a % with no £ amount.
- Confusing: two totals, £18.475m all-in vs £18.539m merchandise-only. The non-product lines are net negative? Worth confirming. "Signed financial lines" is jargon.
- The slide 8 "How we know" headline reads like an instruction, not a finding. The appendix headline is fine.
- Opened headline-preview.md, which was clear and short. Good.
- Asked for the numbers behind each answer before approving headlines. Datasets: none.

## Turn 4
- Excellent reply. Every question now has full tables, and the storage-jar order is confirmed as a full reversal (74,215 units, cancelled 16 minutes later). The ranking was redone without it. Norway's % was flagged as a small-baseline effect. I accept all five answers.
  - Q1: £9.161m → £9.314m (+1.7%); Nov peak 2.67× / 2.96× the quietest month; Sep–Nov is 36–38% of the year.
  - Q2: top 10% (592 customers) = 55.1% of total, 63.6% of identified; guest sales £2.47m (13.4%).
  - Q3: 43.0% overall; months range 34.7–53.5%, with Dec 2010 at 15.8% (small cohort).
  - Q4: White Cherry Lights 35.6%, Pink Cherry Lights 29.2%, Fairy Cake Flannel 26.1%, ...
  - Q5: Australia +£108k (one account = 90%), France +£66k, Norway, Japan, Germany.
- Lesson: "answered" in the status line meant "computed and recorded", not "shown to me". I had to ask explicitly to see the numbers. A first-time user might have approved headlines blind.
- Very long reply, but appropriate here.
- Slide 6's headline still talks about storage jars, which no longer fits now that the jar is removed. Asked for that to change and for slide 5 to show the spread. Asked for awb-status before the full draft.

## Turn 5
- Status was short and clear: evidence, package, storage, code. Good. It rightly corrected my wording on two points: 35–54% excludes December, and "90% of revenue" is not the same as "90% of growth". Good pushback.
- Friction: because status is read-only, my headline edits weren't applied in that turn. I combined two requests and only half got done. I need to say a separate "Use awb-package ..." line, which feels mechanical.
- Friction again: it linked an internal SKILL.md and quoted its rule ("Stay read-only") at me. I don't need to see the tool's internal rulebook.
- "11 supported findings" vs my 5 questions: a bit confusing, but presumably it includes the follow-ups.
- Used the suggested phrasing to request the full draft.

## Turn 6
- The draft came with three clear file pointers. The reviewer pass and the Australia growth check (96.8% of growth) were reported in plain words. Good.
- Read findings.md, methodology-note.md, and START-HERE.md. The outline is solid and all my amendments landed. Numbers match what I was shown. The Australia slide is now very clear.
- Things I'd genuinely change:
  - The subtitle calls us a "UK online retailer". We're a giftware wholesaler selling mostly to small retailers.
  - Source lines say "UCI Online Retail II transaction export". To leadership this is our own order export, so the label is odd. Keep the attribution in the methods note.
  - The "How we know" bullets are written as instructions ("Use…", "Compare…"). They should be past-tense statements.
  - The Answer headline says "Australia's key accounts" (plural), but it's one account.
  - A new number appeared that I hadn't seen in chat: repeat buyers = 97.0% of identified revenue (70.6% of customers). Plausible, but I asked for a quick confirmation of the definition.
  - "Randomly assigned groups receiving no campaign": I'd say "holdout groups" for leadership.
- START-HERE.md is clear, though its step 2 lists methodology.md as both attached to the builder and "internal, do not send". That's slightly confusing, but I get it (attach to Copilot, not to the audience).
- Asked for the changes plus release in the same message, as the README says I see the changed slides first.

## Turn 7
- All six corrections applied and shown as before/after passages. Easy to check. The 97.0% definition was confirmed in one line. Good.
- Friction: it again linked an internal SKILL.md (twice) and quoted its rule "wait for their yes" at me. Third time this session. It feels like the tool justifying itself instead of just saying "confirm and I'll release".
- Friction: the "Confirm these changes" ask appears twice (bold line + checkpoint paragraph). Repetitive.
- Expected: show changes, then wait (matches the README). Fine, but it costs one extra exchange.
- Confirmed. Asked to release 001 and to tell me the path in my releases folder.

## Turn 8 (closing)
- Release 001 frozen and copied. I checked the releases folder: it holds findings, methods note, 5 chart CSVs, START-HERE, deck rules, the M365 assembly file, methodology.md, and the manifest. Caveats were listed clearly. Done.
- Small surprise: the folder path nests under investigation/package names ("marketing-investment/leadership-budget/001") that I never chose. That's fine, but it's worth knowing.
- "No packaging Git commit exists; producing-file checksums are recorded" means nothing to me as a user.

## Overall
- 7 exchanges from first message to release, plus this closing one. That's within the README's 6–11 range.
- Went well: the full first message saved questions; the scoping questions were good; it caught the sheet overlap and the reversed £77k jar order; it pushed back on the 90%-of-revenue vs growth wording; the before/after change preview was easy to check.
- Friction:
  1. "5 answered" before I'd seen any numbers. I had to explicitly ask for the tables before approving headlines.
  2. It repeatedly quoted and linked internal SKILL.md files to justify waiting.
  3. Status is read-only, so my edits sent with the status request weren't applied until a separate package request.
  4. Wordy, duplicated summaries in several replies.
  5. It didn't proactively ask about non-product stock codes during scoping.
  6. It skipped the separate clean/explore steps from the README; it wasn't clear whether that mattered.
  7. START-HERE lists methodology.md as both "attach to builder" and "internal". Clear on a second read.
