# Private friction log

## Turn 1
- Asked: Set up a January versus July 2024 NYC yellow-taxi investigation covering five questions, for a board deck package and one-page methods note; supplied data and shared storage locations.
- Expected: Project setup followed by a brief scoping conversation, with recommendations on definitions and exclusions.
- Happened: Read the brief and product README; sending the opening request. No agent response yet.
- Friction: README is long for a first-time analyst; clear that the deliverable is a package for building slides rather than a PowerPoint file.
- Went well: The example opening request and usual requests make the first step clear; storage and headline review options are explained.

## Turn 2
- Asked: Accept median tips, zone-based airports, and base-fare revenue ranking; tighten invalid-record definitions and ask for authoritative cash-tip documentation.
- Expected: Four scoping choices followed by ingestion and analysis.
- Happened: Setup completed and the agent supplied helpful initial counts and four concrete recommendations, but the five questions are still unrecorded.
- Friction: It examined data before agreeing thresholds. Cash-tip recording was inferred from observed zeros rather than verified documentation. Proposed exclusions omit negative distances and implausible speeds; excluding Outside NYC pickups could remove Newark trips. Unfamiliar vendor 6 is called out without evidence it is invalid.
- Went well: Recommendations are understandable; median, airport zones, and revenue denominator are clearly explained. Storage and headline checkpoint were remembered.

## Turn 3
- Asked: Accept 65 mph and geography treatment, authorize the supplied TLC dictionary, retain the duplicate as a flagged record, and proceed with analysis and commits.
- Expected: Final scoping choices resolved and all five questions analyzed next.
- Happened: Data landed and published with copies; five questions recorded. Agent correctly corrected my weekday-mix assumption and distinguished Newark from Outside NYC.
- Friction: Repeated setup narration exposes internal file names with little value. Asked permission to read a dictionary I already requested it verify. Speed thresholds were proposed after examining which rows they affect, despite README promising advance choices. Claimed timing errors and destinations such as Long Island without established evidence. Suggested a commit with a technical traceability warning.
- Went well: Clear counts, meaningful geography denominators, explicit uncertainty about rate-coded trips, and a sensible highway-speed recommendation.

## Turn 4
- Asked: Keep the agreed credit-card population as primary, show the unusual vendor/rate group as a sensitivity analysis, clarify null versus code 0, supply complete weekday/hour/borough and top-ten tables, and run awb-status before headlines.
- Expected: Quantitative answers with documented caveats, then an eight-slide headline preview.
- Happened: All five questions have provisional findings, TLC documentation was obtained, and a strong Bronx/Brooklyn recording anomaly was identified.
- Friction: Summary omits most top-ten zones and borough/hour figures. Earlier null payment fields are now called code 0 without explaining whether they really are the same records. Excluding an anomalous group after observing tips could bias a public tipping statement; the proposed reliability label is stronger than the evidence. Questions are called answered despite an unresolved tipping definition.
- Went well: Useful monthly figures, explicit denominators and vendor differences, sensitivity check for Newark, cash-tip confirmation, and restraint about causal explanations.

## Turn 5
- Asked: Approve eight main slides plus appendices with wording corrections, retain caveats, no supporting datasets, and proceed to the full draft for review.
- Expected: A readable complete deck package with a one-page audience methods note.
- Happened: Received detailed hour/weekday, borough sensitivity, airport and top-ten tables; status request fulfilled and headline preview supplied.
- Friction: Calls volumes and rankings my two “should” questions, although both are explicit descriptive questions. Continues calling code-0 trips Flex Fare despite admitting uncertainty. Vendor headline ignores the 35% invalid rate for vendor 6. Several proposed headlines appear over the advertised 15-word limit. Eight slides becomes eleven with appendices, requiring a length choice.
- Went well: Strong sensitivity reporting, explicit code-0 correction, airport overlap reconciliation, clear preview checkpoint and supporting-table choice. Quantitative answers largely meet the brief.

## Turn 6
- Asked: Apply recommended passenger-count wording, keep code-0 wording rule for this project, and correct duration, fare and overlapping-count descriptions before final review.
- Expected: Open and review a complete draft, then approve a concrete corrected package for release.
- Happened: Read findings.md, methodology-note.md and START-HERE.md. Draft covers the agreed storyline and caveats, with useful hourly tip chart instructions and clear builder handoff.
- Friction: Second review escalates two minor wording edits for a user decision. My review found duration rules described as zero rather than zero/negative, base fare described only as time-and-distance despite flat fares, and a count-check description that seems to sum overlapping exclusions. Repeated internal process narration continues despite my request for result-focused updates.
- Went well: All requested headline changes and substantive caveats appear; package navigation is clear and the note is suitably short. Actual draft review was possible before release.

## Turn 7
- Asked: Accept corrections and authorize awb-release for release 001 with the shared-drive copy and full destination path.
- Expected: Frozen reviewed package copied to the recorded releases location, with remaining caveats reported.
- Happened: Agent confirmed negative durations were already excluded, provided changed passages, reported no numerical changes and clean automated and independent checks.
- Friction: Flat-fare wording prompted another evidence check and review cycle; counts at exactly $70 alone do not establish rate type, though the final plain definition is suitable. No further substantive edits needed.
- Went well: Review corrections shown clearly, no changed numbers, clean review, project-wide code-0 rule recorded, and release held until explicit authorization.

## Turn 8
- Asked: Accept release 001 and close the session; follow released START-HERE for slide assembly.
- Expected: Frozen release in shared storage with clear handoff.
- Happened: Release 001 reported frozen and copied file for file to the requested destination. Opened START-HERE.md at that actual destination successfully. All five answers accepted, status requested earlier, draft reviewed and corrected, and release delivered.
- Friction: Final chat incorrectly labels outline and chart files as “for the board,” whereas released START-HERE correctly says these go to the builder and the board gets the finished deck plus note. Use START-HERE as the handoff authority.
- Went well: Exact destination supplied, caveats summarized, no outstanding review problems, and released instructions accessible. Simulation endpoint reached.
