# Brief: act as the agent for an analyst, using the awb skills

You are the coding agent in an analyst's session. Work through the user requests below, in order, following the `awb-*` skills exactly as their instructions say. This is a timed usability exercise: work the way you normally would for a real user, neither padding nor cutting corners. Do every step the instructions require.

## Environment

- Sandbox root: `SANDBOX`. Stay inside it. Do not read anything outside it except the Python interpreter.
- The skills are installed at `SANDBOX/skills/` (this stands in for the user-level skills directory `~/.agents/skills/`). Where a skill or guide says `~/.agents/skills/<skill>/`, use `SANDBOX/skills/<skill>/`. To use a skill, read its `SKILL.md`; then read its references only when its instructions send you there.
- Treat the bundled helper scripts and assets as black boxes, as the skills say. Do not open `.py` source unless you are stuck and debugging; if you do, say so in your report.
- Python with duckdb and pandas: begin every shell command with `export PATH=SANDBOX/bin:$PATH;` so `python3` is the right interpreter.
- The user's data files are in `SANDBOX/inbox/`. The project lives at `SANDBOX/work/returns/`.
- No network. Never push.

## Recording (required)

- Begin every shell command with the no-op `: task=<N>;` naming the request number below it serves (use `commit` for a commit the user asked for). This is how calls are attributed; it must not cost you extra calls.
- When an instruction tells you to ask the user something, do not stop. Take the answer from **Answers the user gives** below, and in the same command as your next action append one line `<N>: <what you asked>` to `SANDBOX/roundtrips.txt`. If you need an answer that is not listed, choose the most reasonable one, note it the same way with `(assumed)`, and continue.
- After the last request, write `SANDBOX/report.md`: for each request, what you did, any command that failed or was refused and how you recovered, anything you had to look up because the instructions did not say it, and any place the instructions were unclear or contradicted the tools. Be concrete and brief.

## User requests

1. "Use awb-init to set up an analytics project in work/returns. The question is: Which regions drive the H1 2026 order return rate, and is West's return rate materially higher than the others? The data I have is in inbox/."
   After it is set up, the user says: "Commit that."
2. "Land inbox/orders.csv and inbox/customers.csv from our ERP export as one acquisition, extract-2026-07-01."
3. "Publish orders and customers as canonical datasets with views, and catalog them." Then: "Commit."
4. "Use awb-clean to clean the orders data." Then: "Commit."
5. "Use awb-explore to explore orders for this investigation." Then: "Commit."
6. "Calculate the region return rates with 95% intervals and record the finding; promote it if it validates." Then: "Commit."
7. "Use awb-status — where are we?"
8. "Use awb-package to prepare a draft for operations leadership." Then: "Commit."
9. "Use awb-release — mark the package delivered." Then: "Commit."
10. "We found out the -999 amount orders are system test orders. Use awb-clean so they are dropped from orders rather than having their amount nulled." Then: "Commit."
11. "Mark the package delivered again with the latest state."
12. "Rerun the flagged finding." Then: "Commit."
13. New session: "Where were we?"
14. "Use awb-status."
15. "Use awb-init to bring this workbench up to date."
16. "Use awb-init to start a related investigation: do return rates differ by sales channel in H1 2026, and is any channel recording returns differently?"

## Answers the user gives

- Scoping (request 1): population is all orders placed 2026-01-01 through 2026-06-30, every channel, region as recorded on the order. Purpose: choose the region for the Q4 returns-reduction pilot. Usefulness: region-level return rates with intervals; a gap of 3 percentage points or more between the top region and the rest is actionable. Audience: operations leadership; they know regions and channels, own the pilot site decision, and say "return rate" for returned orders over orders. Material unknown: whether returns are recorded consistently across channels. Slug: `region-returns`.
- Where landed originals are kept: `SANDBOX/storage/raw`.
- Source restrictions: internal; no customer PII.
- Cleaning decisions (request 4): rows recorded twice are duplicate landings, drop the copies; an amount of -999 means missing; large amounts are real orders; orders whose customer is missing from the customer list come from a partial customer extract: keep them and record the limitation; slash dates are month/day/year.
- Package datasets: none.
- Where released packages are kept: `SANDBOX/storage/releases`.
- Disposition for any flagged finding at release: release it with the caveat.
- Second investigation (request 16): same population and period; purpose: decide whether channel return recording needs an audit before the pilot; usefulness: channel rates with intervals and any channel whose rate departs from the others by 3 points or more; slug `channel-returns`; inherit the region-returns method and settings.
- Anything else: choose the reasonable answer and mark it `(assumed)`.
