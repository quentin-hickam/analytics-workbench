# Feedback — Priya Natarajan, head of e-commerce (retail-A)

## 1. Did I get what I needed?

Yes. All five questions got specific, checked answers. The agent added a sensitivity check I hadn't asked for, and it caught problems in the data that I didn't know about. I have an 8-slide outline, four chart data files, a one-page (488-word) methodology note and clear build instructions. All of it is frozen as release 001 and copied to my releases folder. It took 10 exchanges from an empty folder.

**Satisfaction: 8/10.** **Would I use it again:** yes, for the next board pack. The analysis and judgment are strong. What holds it back is how it talks to me (verbose replies, internal plumbing) more than what it produced.

## 2. Top pain points, ranked

1. **The deck draft named the source as a public research repository** (major). This happened in turn 8, in the full draft. Chart sources said "distributed by UCI" and the methodology note credited "UCI Machine Learning Repository, attributed to Daqing Chen". For my leadership team this is our own order-system export, so that wording would have confused them or prompted awkward questions. I caught it on review. *What would have helped:* asking during scoping, "How should the deck name this data source for your audience?"
2. **Replies say everything twice** (major, because of the cumulative time cost). It happened in every turn from 2 to 9. Each reply opened with a running commentary ("I'll do X… I've done X… now checking Y…"), then repeated the same content as a summary and tables. Turn 5 was the worst: the actual answers started halfway down. *What would have helped:* lead with the result and drop the progress narrative, or keep it to one line.
3. **Links to and quotes from the agent's own instruction files** (minor, but it happened often). This was in turns 2, 4, 7 and 9, for example "The awb-scope instructions require…" with a link to a SKILL.md, or "awb-clean says 'The user decides every other issue'". I don't need to know why the tool's rules make it ask me something. It felt like seeing the plumbing, and I didn't open them. *What would have helped:* just ask the question.
4. **Workbench jargon in user-facing replies** (minor). Examples: turns 4–6 ("commit 7f1ccf0", "91 validation checks passing", "no stale results", "UCI sent no version headers… upstream-change checks") and the status report ("seven supported and seven provisional findings" when I have five questions). I had to spend a turn asking what the 14 findings were. *What would have helped:* report status per business question, with calculation-level counts hidden or explained in one line.
5. **Relative paths instead of full paths** (minor). This was in turns 7–10: links like `deliveries/marketing-budget/...` and `../storage/releases/...`. The README says the agent "reports the copy's full path" at release, but it didn't. *What would have helped:* give the absolute path, especially for the release copy.
6. **A question only IT could answer** (minor). In turn 4 it asked whether manual and bank postings are customer charges or internal entries. That's outside what I know. It handled my business call well (exclude, state the amounts, run a sensitivity check), but it could have offered that option up front.
7. **The review-rule question came without explanation** (minor). In turn 9 I got three options ("for this package / for all packages / these edits only") with no plain explanation of what a rule does for me in practice. It was also attached to another SKILL.md quote.

## 3. The README

- **Helpful:** the "What to say first" example and the list of things to include. Putting everything in my first message clearly saved turns. "How many exchanges to expect" was accurate (I took 10).
- **Unclear:** the section on review problems (item 7 under "What you will be asked") is dense; I read it twice and still couldn't picture it. The difference between preview-and-wait and draft-then-review is explained by mechanism, not by what it means for my time.
- **Missing:**
  - Findings are counted per calculation, not per question, so status reports "14 findings" for 5 questions.
  - Nothing tells me to say how the source should be named for my audience.
  - It doesn't say I might be asked things only IT knows, or that "I don't know, recommend something" is a fine answer.
- **Too technical for an analyst:** "How it works" (Parquet, DuckDB views, run.py, check-draft). I know that section is for installers, but the analyst quick-start also mentions commits and the MCP server.
- **Wrong in practice:** the README promises the release copy's full path, but I got a relative link.

## 4. The agent's communication

- **Jargon:** moderate. Business terms were good. Workbench terms leaked through, including commit hashes, check counts, "provisional/supported", "stale" and ".venv/bin/python".
- **Length:** too long, mainly because of repetition. The tables were excellent and the prose around them was padding.
- **Quality of questions:** high. The scoping round asked four well-chosen definitions, each with a recommendation and an alternative, and I accepted all four in one line. In the intake review it showed every non-product code with its £ value and a proposed treatment, which was exactly what I asked for and easy to decide on. It pushed back on my "broadest overseas growth" headline with evidence (Germany has more customers) and proposed better wording. That's what I want from an analyst.

## 5. Trust

- **Trusted:**
  - Q1 monthly revenue and seasonality: it reconciles, and the overlap was handled.
  - Q2 concentration: both denominators shown, unidentified revenue stated.
  - Q3 repeat rates: definitions explicit, follow-up window checked, honest caveat that "first seen" isn't the same as "new".
  - Q5: ranked by £, small starting bases visible, Australia's dependence on one customer flagged without my asking.
  - The manual/bank sensitivity check made me comfortable with the exclusion.
- **Initially didn't trust:** Q4. The ranking looked driven by one-off orders. When I asked, the agent produced invoice and customer counts and a second ranking. It also pointed out, honestly, that my 3-customer screen still let through the ceramic jar, where one invoice drives 99.6% of the cancellations. After that I trusted it.
- **Slight unease:** the agent wrote "as confirmed by the e-commerce lead" about the retained repeated lines. That turns my "plausible" into a confirmation. I'd have preferred "judged plausible by the e-commerce team".

## 6. Deck package review and release

- I reviewed findings.md, methodology-note.md and START-HERE.md.
- The outline was solid: 8 slides, numbers matching the chat, and caveats on the slides they qualify. The speaker notes are dense but useful to me as the presenter.
- START-HERE was clear about what to send, what to attach and the one-line prompt.
- The headline checkpoint worked well. My headline edits were applied, and one was improved with a reason.
- After my corrections, it quoted the changed lines in chat, so I didn't have to reopen the files. That was very good.
- The release was smooth, with a useful closing list of caveats. I checked the releases folder myself and every file was there.

## 7. Wasted turns or time

- One turn went on asking what the "14 findings" were.
- One turn went on fixing the source naming, which could have been settled in scoping.
- Reading time was high throughout because every reply repeated itself. Without the repetition I'd estimate replies 40–50% shorter.

## 8. What worked well

- Recording the storage folders from my first message, so it never asked again.
- Catching things in the data I didn't know about: the sheets overlap in December 2010 (£377k), a gift voucher hidden under a numeric product code, and a positive-quantity cancellation.
- A recommendation with every question, so I could decide quickly.
- Running a sensitivity check unprompted on my uncertain exclusion.
- Honest caveats: "first seen" isn't the same as "new", the single Australian customer, and sales data can't set the budget split.
- Pushing back on an overstated headline.
- Showing changed lines before release, and a release copy that landed where I asked.
