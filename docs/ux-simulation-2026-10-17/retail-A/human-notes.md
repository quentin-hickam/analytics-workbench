# Friction log — Priya Natarajan (retail-A)

## Turn 1 — first message
- Read README first. Followed the "What to say first" example: awb-init + business question + 5 sub-questions + audience/decision/length + data URL + storage folders + headline checkpoint mode.
- Expect: project setup, then a scoping round of up to four questions at a time. No data pulled in yet (README says setup/scoping bring no data in).
- README notes:
  - Good: the example first message is very helpful; clear list of what to include.
  - Somewhat jargon-heavy for a non-programmer: "Parquet", "DuckDB views", "MCP server", "check-draft", "R-periods-001". The analyst quick-start is mostly readable, but section 7 (review problems) is dense; I had to reread it.
  - Unclear what "preview-and-wait" vs "draft-then-review" difference means in practice for my timeline; chose preview-and-wait since I want to see the storyline first.
  - Unclear whether I need to download the ZIP myself or the agent will; README says the agent downloads from a web address when asked, so I gave the URL.

## Turn 2 — scoping round
- Agent set up project (.venv, Git, helpers), recorded storage paths, didn't download yet. As expected.
- Scoping: 4 clear questions, each with recommendation + alternative. Matches README promise. Good.
- Friction: agent linked me to the awb-scope SKILL.md and quoted its internal rule ("asking every open decision...") — irrelevant to me, felt like seeing the plumbing. Didn't open it.
- Friction: reply was a bit repetitive (said "setting up" three times before the questions).
- Mild jargon: ".venv/bin/python", "DuckDB and pandas", "Git" — meaningless to me but harmless.
- My answers: accepted 1–3; £1,000 threshold OK. Added: exclude non-product codes from product ranking; asked for recommendation on postage/fees in revenue (persona unsure).

## Turn 3 — scope recorded, ask for data intake
- Agent recorded definitions, gave a sensible revenue recommendation (include postage/customer charges, exclude internal fees like bank/Amazon fees and accounting adjustments, review manual "M" lines). Good, plain-English.
- Nice touch: it flagged on its own that "first purchase" only means first seen in this export, and that sales data alone can't settle the budget split.
- Friction: the reply repeated itself again (revenue recommendation stated twice, investigation status twice). Long for what it says.
- Didn't open brief.md; trusted the summary.
- Next: accepted recommendation, asked it to download the data.

## Turn 4 — intake + code audit
- Downloaded, landed copies in my storage folder, 1,067,371 rows, 25 checks passed. Found December 2010 overlap between sheets (22,523 lines, £377k) — I didn't know that; valuable catch.
- Code table with values was exactly what I asked for. Very useful. Gift voucher hiding under numeric code 22016 — good catch.
- Friction: again quoted the awb-clean SKILL.md with a link ("The user decides every other issue..."). Internal plumbing; didn't open.
- Friction: the reply is long and repeats itself (summary at the top and again below). Mentions "UCI sent no version headers... automatic upstream-change checks" — jargon I didn't need.
- Friction: it asked me what manual/bank postings represent — I don't know, that's an IT question. Made a business call instead: exclude from headline revenue, quantify in caveat.
- Several small decisions (11,812 repeats, C496350, trailing space) — fine, but a lot to absorb. Answered all.
- Said yes to the commit suggestion.

## Turn 5 — all five answers
- Big turn: all 5 answered with specific numbers, tables, and a sensitivity check on the M/bank exclusion (0.63% total; Japan/Norway swap). Exactly what I asked for. Very good.
- Q1, Q2, Q3, Q5 look usable. Good unprompted caveats (Australia = one customer 90%; "first observed" ≠ new customer).
- Q4 concern: the top of the cancellation ranking looks driven by one-off orders (jar: one £77k cancel; Black Cherry Lights 99% on ~£1.6k). For leadership "highest cancellation rate" ranking dominated by single orders is misleading. Asked for order/customer counts per product and a view excluding single-order-driven cases.
- Friction: commit hash "7f1ccf0", "91 validation checks", "no stale results" — meaningless to me.
- Friction: reply again has a progress narrative before the actual answer; the useful part starts halfway down.
- Asked awb-status here as well (README suggests it).

## Turn 6 — Q4 comparison + status
- Agent gave both Q4 rankings with invoice/customer counts. It pointed out that my 3-customer screen still lets the jar through (one invoice = 99.6%), which I'd missed. Honest and helpful.
- Black Cherry Lights: 48 customers cancelled → genuinely a product problem. Good story for the deck.
- awb-status: readable, but mixes useful stuff (what's accepted, caveats, what's next) with plumbing ("14 results current, 98 checks", "seven supported and seven provisional findings" — I have 5 questions, why 14 findings?). Slight confusion.
- It ended with a clear next step. Good.
- Decision: version B, with a jar caveat. Asked for headline preview; told it: no datasets, methods note about one page.

## Turn 7 — headline preview
- The "14 findings" explanation was clear enough: supporting calculations. Still, "supported/provisional" per calculation vs per question is confusing for a user; the README's "Words you will meet" doesn't make this distinction.
- Explanation repeated twice in the same reply again (pattern: narrative paragraph + same content as bullets).
- Headline preview: 8 slides, sensible structure. Preview link is a relative path (deliveries/.../.preview/headlines.md) — hidden folder; I didn't open it, the chat list was enough.
- Friction: third time it quoted a SKILL.md at me.
- My edits: put numbers in slides 3, 4, 5 headlines; reframe slide 6 around France (broad-based) vs Australia (one customer) since that's the market decision; overall 2.9% growth should appear. Approved the order otherwise.

## Turn 8 — full draft review
- Agent pushed back on my "broadest growth" wording (Germany has more customers) and proposed "France merits an acquisition test" instead. Correct, and it explained why. Good.
- Opened findings.md, methodology-note.md, START-HERE.md (links were relative in chat; I had to work out the full path myself).
- findings.md: solid. 8 slides, numbers consistent with chat, caveats where they belong. Speaker notes are dense but useful to me as presenter.
- Problem: source described as "distributed by UCI" and methodology note credits "UCI Machine Learning Repository, attributed to Daqing Chen". To my leadership this is our own order-system export, so that wording would confuse them. Asked for a fix throughout.
- Minor: some jargon remains in notes ("signed quantity", "grouping keys", "permitted repeated line occurrences"). Asked to plain-English the How we know slide and the note's Method section.
- START-HERE.md is clear: what to send, what to attach to Copilot, one-line prompt. Good.
- Asked to see changed lines before releasing.

## Turn 9 — corrections shown, release
- Agent applied both corrections and quoted the changed lines in chat. That's exactly what I wanted. Wording is fine.
- Small oddity: "as confirmed by the e-commerce lead" was added to How we know. I did say they were plausible, so it's acceptable, but it makes my judgment sound like a verified fact. Left it.
- It asked whether to keep my correction as a check for later drafts (a "review rule"). Reasonable question, but it was asked in the middle of the reply with another SKILL.md quote, and the 3 options weren't explained (what does "for all packages" mean for me?). Answered: all packages.
- Asked to release as 001 and report the copy path.

## Turn 10 — released
- Release 001 made, copy confirmed in storage/releases/marketing-budget/leadership-budget/001/ (I checked: findings, note, 4 charts, START-HERE, deck rules, assembly, manifest all there).
- Friction: README says the agent "reports the copy's full path", but it gave a relative link (../storage/releases/...). I had to work out where that was.
- Caveat list at release was a good last reminder.

## Overall
- 10 exchanges from empty folder to release 001 (README's 6–11 range was about right).
- Went well: scoping questions with recommendations; data catches I wouldn't have made (sheet overlap, hidden voucher code, single-order jar cancellation); sensitivity check unprompted; agent pushed back on my overstated headline; changed lines shown before release.
- Main friction: (1) repeatedly linking/quoting internal SKILL.md files; (2) verbose replies that tell everything twice (narrative + summary); (3) plumbing jargon (commit hashes, checks counts, supported/provisional findings ≠ questions); (4) relative paths instead of full paths; (5) "distributed by UCI" source wording reached the draft and I had to catch it; (6) asked me a question only IT could answer (manual/bank postings), though it handled my business call well.
