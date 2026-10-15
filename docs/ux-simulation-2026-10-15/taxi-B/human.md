# Feedback from Dana Ortiz

## 1. Outcome and satisfaction

I got specific answers to all five questions, a reviewed eight-slide outline, chart data, complete top-10 zone tables, a plain-language methodology handout, and release 001 copied to the shared releases folder. I accepted a reasoned limitation on full borough tipping comparisons. Satisfaction: **7/10**. I would use this again for the reproducibility and careful caveats, provided routine approvals and packaging constraints become less intrusive.

I received a deck assembly package, not a finished PowerPoint. The README disclosed this, but building the actual presentation still requires another application and additional work. I verified the released folder and the presence of the handout and ranking attachment; I did not independently reproduce the calculations.

## 2. Ranked pain points

1. **Presentation rules overrode straightforward editorial requests — major.** During headline approval and again during draft delivery, the agent said moving airports before volumes required reducing the volume question's priority. It also initially said the format required 11 slides despite my request for about eight. I eventually accepted the wrong order to keep moving. Question importance and slide order should be separate choices; let the agent make the requested deck structure without making me negotiate internal records.
2. **The requested one-page handout arrived as a technical reference — major.** At first package review, methodology.md was a long document with code paths, internal question numbers, evidence links, and chart mappings. I had to request a separate audience-facing note. The final note was useful but still dense; its claimed one-page fit was not demonstrated in a rendered document. Ask who will read the note, or use my explicit handout request to generate it alongside the technical reference from the start.
3. **Too many stops for routine authorization — major.** The agent asked before installing required packages, making local commits repeatedly, investigating a tipping anomaly, and drafting after I had already requested the package. A necessary anomaly test should proceed as part of answering my question. Bundle real analytical choices and proceed with routine work already within scope.
4. **Some first-pass claims outran the evidence — major.** Early replies treated cash tips as definitively missing, suggested matched positive fares were voided trips, and later called Manhattan and Queens reliable after one sensitivity test. I had to distinguish observation from explanation several times. The final review caught other overstatements too. Apply that caution before showing findings, and seek authoritative documentation without treating my memory as confirmation.
5. **Long process reports made the next decision hard to find — minor.** Setup brought an inventory of helper files, 16 questions, dependency instructions, and optional connector configuration. Later replies reported commit state and review mechanics repeatedly. Lead with findings or the specific decision needed; keep the setup inventory available elsewhere.
6. **Initial answers lacked useful completeness — minor.** The first findings draft omitted values for several top-10 zones, exact zero-distance totals, the overall monthly tip median, and an explanation of overlapping airport shares. A compact complete results table would have saved a follow-up.

No issue ultimately blocked delivery.

## 3. README

The initialization, status, package, and release example requests were helpful. The storage explanation and distinction between drafting and releasing were particularly useful. The README also correctly disclosed that M365 builds the presentation from the package.

For a first-time analyst, installation and host-specific material overwhelms the everyday workflow. I needed a short path from business question to files, findings, review, and delivery, with the technical setup separated.

It did not prepare me for mandatory headline approval, format-driven extra slides, or slide order being tied to the question ledger. I cannot tell whether those constraints came from the product or the agent's interpretation; either way, they were presented as rules I had to accommodate. The README should explain actual user-facing constraints and make clear how to change presentation order without changing analytical priorities.

It also did not clearly distinguish the internal methodology reference from the plain-language one-page handout I wanted. An example package inventory with intended readers would help. Explain what the user reviews to accept findings, which routine tasks the agent can handle automatically, and what a useful final package looks like before the M365 handoff. A clearer statement that no PowerPoint is produced here would prevent disappointment even though the assembly workflow is described.

## 4. Agent communication and scoping

The scoping questions about pickup month, airport zones, revenue definition, validity cutoffs, and storage were substantive and usually came with useful recommendations. Asking for board thresholds was reasonable; accepting that we had none was also appropriate. It did not expect me to answer deep TLC-process questions once I said I could not.

However, the interview felt spread across administrative gates. Asking me about installing packages and connector registration alongside analytical definitions increased the burden. Sixteen open questions sounded like a large workload before any analysis had begun.

Messages were generally readable but too long. Terms such as canonical preparation, supported findings, publication identifiers, validation frames, and ledger priority belong in technical records unless they affect a decision. The explanation of the join validation exception became understandable once it said that the same number of records came out as went in. Reporting six review rounds, then two more, made the process sound expensive without helping me review the results.

## 5. Trust in the answers

I accepted the volume, airport, exclusion, and ranking results as descriptive answers under the agreed definitions. Specific counts, stated denominators, normalized weekday averages, explicit fare definitions, and sensitivity results helped. The ranking measure was clearly separated from driver earnings, and the trip minimum prevented tiny samples from dominating without explanation.

I trusted the statement that these files do not support a full borough tipping comparison more than any claim about actual borough tipping behavior. Manhattan and Queens were relatively stable under the test, but that does not establish complete tip capture. Cash tips and payment code meanings lacked documentary verification. I supplied payment types from memory; the agent initially muddled that provenance but corrected it.

I did not accept that negative/positive twins were proven voids or reversals. Keeping otherwise-valid positive records in the main analysis and showing a sensitivity was reasonable. Vendor differences describe record quality under our rules, not why a provider sent those records. Two selected months cannot establish seasonality or causes. These limitations made it into the final package.

The invalidity share is also a result of chosen rules, not an independently established count of all broken trips. Reporting zero distance separately and as a union with invalid records was important.

## 6. Package review and release

Opening the actual outline was worthwhile: numbers and caveats were visible, charts had specifications, and the ranking attachment was useful. I requested real corrections, including a plain-language handout, an explicit 3.1% volume comparison, and removal of the claim that TLC publishes every trip. Those changes were incorporated.

The agent reached eight slides but refused the requested airport-first order. The process exposed too much of its own format machinery. A full table with twenty ranking rows may also be demanding on a single slide; I could review the outline, not the final PowerPoint layout.

Release was the smoothest administrative step. It froze release 001, reported both locations, listed the contents, and said the external copy matched file for file. I checked the shared release directory and found the expected material. The explanation that later changes become release 002 was clear.

## 7. Wasted turns and time

- Repeated permission requests for local commits and routine setup.
- Asking whether to investigate a material anomaly after identifying it.
- Stopping at headline approval after I asked for a full draft.
- Negotiating eight slides and slide order against internal format requirements.
- Requesting a genuine one-page handout after the technical reference was supplied instead.
- Following up for complete numerical tables and overlap explanations that should have accompanied the first findings.

I cannot quantify runtime from the conversation, but the reported review rounds and repeated checkpoints made the work feel slower. Review itself was valuable; its internal iteration count was not useful to me.

## 8. What worked well

- Concrete recommendations made analytical choices easier.
- Landed originals and numbered releases were copied to the specified storage locations.
- Excluded records were counted instead of silently disappearing.
- The agent found the vendor/rate-code tipping anomaly and tested its consequences.
- It respected the decision to keep missing passenger counts and suspected positive twins, with flags and sensitivities.
- The status request gave a useful account of remaining questions, limitations, and delivery readiness.
- Review improved claims about demand, completeness, recorded zeros, and the unexplained tip group.
- The final package separated audience findings, chart data, ranking data, and technical documentation, and included the requested handout after correction.
- Release confirmation was concrete and easy to check.
