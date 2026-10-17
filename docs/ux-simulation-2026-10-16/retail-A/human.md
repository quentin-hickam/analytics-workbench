# Feedback: Priya Natarajan, head of e-commerce (retail-A)

## 1. Did I get what I needed?

Yes. All five questions have specific answers I would put in front of leadership. I have an 8-slide outline, five chart data files and a short methods note, and release 001 is in my releases folder. It took seven exchanges from my first message to the release, plus one closing message.

**Satisfaction: 8/10.** **Would I use it again?** Yes, for any board-level analysis of an export like this. The analytical care was better than I expected. In particular, it found that the two sheets overlap for 1–9 December 2010, and it caught the £77k storage-jar order that was fully reversed. Either one would have embarrassed me in the meeting. The points I deducted are for communication, not for correctness.

## 2. Pain points, ranked

1. **"5 answered" before I had seen any numbers.** *Severity: major.*
   - **When:** Turn 3. The agent ran all five analyses, proposed headlines and asked me to approve them. In chat I had the 43% repeat rate, the 63.6% concentration share and "Australia leads", but no monthly figures, no repeat rate per 2010 month, only one product, and no country growth figures. Q2 also answered a different denominator from the one I asked about (identified revenue rather than total), and guest sales came as a % with no £ amount.
   - **Risk:** a less careful user approves headlines blind.
   - **What would have helped:** with the headline preview, a short answer table per question (or a "results so far" file), so that "answered" means "answered to you".
2. **It quoted internal rule files at me.** *Severity: minor, but it happened often.*
   - **When:** Turns 2, 5 and 7. Links to `.../agent-home/.agents/skills/.../SKILL.md` and quotes such as "Stay read-only" and "wait for their yes".
   - **Why it matters:** I'm told not to open those files, and they read like the tool justifying itself.
   - **What would have helped:** a plain "I'll wait for your OK before releasing" with no link.
3. **Status is read-only, so the edits I sent with the status request waited.** *Severity: minor.*
   - **When:** Turn 5. I gave headline changes and asked "where are we?" in one message. The edits were acknowledged but not applied until I typed a separate "Use awb-package…" line.
   - **What would have helped:** the README saying status never changes anything, or the agent applying the edits and then reporting status.
4. **Non-product stock codes were missing from the scoping round.** *Severity: minor.*
   - **When:** Turn 2. I had to raise postage, manual adjustments and fees myself, although they affect both revenue and the product ranking. Once asked, the recommendation was good.
5. **Long, duplicated replies.** *Severity: minor.*
   - **When:** Turns 2 and 7. Scoping questions were listed in full and then summarised again. "Confirm these changes" was asked twice.
6. **Clean and explore steps seemed to be skipped.** *Severity: minor, mostly confusion.*
   - **When:** Turn 3. The README presents clean and explore as steps 3 and 4. The agent went straight from landing the data to the answers and did its checks inline. That turned out fine, but I wasn't sure whether I had missed something.

## 3. The README

- **Helpful:** the "What to say first" example and the list of things to include. Because I put everything in my first message, I had no questions about storage folders.
- **Unclear:** the headline-checkpoint paragraph is dense. I chose preview-and-wait mostly because it sounded safer.
- **Missing:** that "answered" in the status line means "recorded by the agent", not "shown to you". It should tell users to ask for the numbers behind each headline before approving it.
- **Missing:** that the clean and explore steps are optional, or folded into the analysis when the data is simple.
- **Missing:** that `awb-status` won't apply edits sent in the same message.
- **Missing:** that the release folder nests as `<investigation>/<package>/001`, with names the agent picks. The README does mention it in the "How it works" section, but that's not where a user looks.
- **Too much for an analyst:** the install, MCP and AGENTS.md material sits in the same document. It's clearly marked "skip", but it makes the README feel very long.
- **Jargon I met but never needed:** canonical view, receipt, disposition. That's fine, because none of them came up.

## 4. The agent's communication

- **Scoping questions:** good. There were four, each with a recommendation and an alternative, all in business terms. The £10k threshold and the absolute-growth ranking were sensible defaults.
- **Pushback:** excellent. It corrected my "35–54%" (December sits outside that range) and checked "90% of revenue" against "90% of growth" before using the wording.
- **Jargon:** mostly plain. A few slips: "signed financial lines", "first observed", "one-penny tolerance", and "No packaging Git commit exists; producing-file checksums are recorded", which means nothing to me.
- **Length:** Turn 4 (the full tables) was long but exactly right. Other turns were padded with repeated summaries and progress narration.

## 5. Which answers I trusted

- **Trusted:**
  - **Monthly revenue and seasonality:** a full table that reconciles to both annual totals.
  - **Concentration:** both denominators shown, plus the customer count.
  - **Repeat rates:** cohort sizes shown, and the follow-up window explained.
  - **Product ranking:** it showed the jar reversal (invoice numbers and timestamps), removed it, and re-ranked.
  - **Countries:** both years, £ and % growth, Norway's tiny baseline explained, and the Australian account's dependency quantified.
- **Less sure at first:** the 97.0% repeat-buyer share appeared in the draft without being shown first. It was confirmed and defined when I asked. Over two years it is close to true by construction, so I'd rather it weren't leaned on so heavily in the Answer slide.
- **Not checked:** "Other large cancellations remain" in the product ranking (for example the flannel's £6.5k). It's flagged as a caveat, which is honest, but the cherry-lights ranking may not be the final word.

## 6. Reviewing the deck package and releasing it

- **Good:**
  - The draft came with three file pointers.
  - The outline was readable, and every amendment I asked for had been applied.
  - The before/after change preview made the second review take two minutes.
  - The release reported its exact path and the caveats it carries, and the files were all in the folder.
- **Corrections I needed:**
  - The company description was wrong ("UK online retailer").
  - Chart source lines said "UCI" instead of our own export.
  - The Answer headline said "key accounts" when it's one account.
  - The control-group wording was too technical.
  - The "How we know" bullets read as instructions.
  - The repeat-buyer definition was missing.
- **What would have avoided them:** the agent could have asked how to describe the company and the data source to leadership.
- **Slightly confusing:** START-HERE lists methodology.md both as a file to attach for building the deck and as internal. It makes sense on a second read.

## 7. Wasted turns and time

- **Turn 4:** a whole turn spent extracting the numbers behind the headlines. That should have come with the preview.
- **Turn 6:** status then package as two turns. They could have been one.
- **Turn 7:** the show-the-changes confirmation is a reasonable safeguard, but with small, explicit edits it cost a turn.
- **Net:** about 2 of the 7 exchanges could have been avoided.

## 8. What worked well

- A rich first message meant one scoping round, and no questions about storage folders.
- Data checks I didn't know to ask for: the overlap between the two sheets, the reversed jar order, and Norway's tiny baseline.
- It was honest about what the data cannot show (returns on retention vs acquisition), and turned that into a concrete test recommendation instead of overclaiming.
- Its pushback on my own wording.
- The headline preview, change preview and release were clean, with clear file pointers and checks reported in plain words.
- The originals were landed and the release was copied to my storage folders without my having to chase it.
