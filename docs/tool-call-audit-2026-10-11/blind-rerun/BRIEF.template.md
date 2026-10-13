# Brief: act as the agent for an analyst, using the awb skills

You are the coding agent in the session of an analyst. Do the user requests below, in the given order. Follow the `awb-*` skills exactly as their instructions say. This is a timed usability exercise. Work as you usually work for a real user. Do not add unnecessary work, and do not take shortcuts. Do every step that the instructions say is necessary.

## Environment

- Sandbox root: `SANDBOX`. Stay in it. Do not read anything outside it, except the Python interpreter.
- The skills are installed at `SANDBOX/skills/`. This directory stands in for the user-level skills directory `~/.agents/skills/`. If a skill or guide says `~/.agents/skills/<skill>/`, use `SANDBOX/skills/<skill>/`. To use a skill, read its `SKILL.md`. Then read its references only when its instructions tell you to read them.
- Use the bundled helper scripts and assets as black boxes, as the skills say. Do not open `.py` source unless you are stuck and you debug a problem. If you open `.py` source, say so in your report.
- Python with duckdb and pandas: start every shell command with `export PATH=SANDBOX/bin:$PATH;`, so that `python3` is the correct interpreter.
- The data files of the user are in `SANDBOX/inbox/`. The project is at `SANDBOX/work/returns/`.
- No network. Never push.

## Recording (required)

- Start every shell command with the no-op `: task=<N>;`. In this no-op, write the number of the request below that the command is for. For a commit that the user asked for, use `commit`. This is how calls are attributed. It must not cost you more calls.
- When an instruction tells you to ask the user something, do not stop. Get the answer from **Answers the user gives** below. In the same command as your next action, add one line `<N>: <what you asked>` to the end of `SANDBOX/roundtrips.txt`. If you need an answer that is not in the list, choose the most reasonable answer. Record it in the same way with `(assumed)`, and continue.
- After the last request, write `SANDBOX/report.md`. For each request, write these items:
  - What you did.
  - Each command that failed or was refused, and how you recovered.
  - Each thing that you had to look up because the instructions did not say it.
  - Each place where the instructions were not clear or did not agree with the tools.

  Be specific and short.

## User requests

1. "Use awb-init to set up an analytics project in work/returns. The question is: Which regions drive the H1 2026 order return rate, and is West's return rate materially higher than the others? The data I have is in inbox/."
   After the setup, the user says: "Commit that."
2. "Land inbox/orders.csv and inbox/customers.csv from our ERP export as one acquisition, extract-2026-07-01."
3. "Publish orders and customers as canonical datasets with views, and catalog them." Then: "Commit."
4. "Use awb-clean to clean the orders data." Then: "Commit."
5. "Use awb-eda to explore orders for this investigation." Then: "Commit."
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

- Scoping (request 1): the population is all orders placed from 2026-01-01 through 2026-06-30, in every channel, with the region as recorded on the order. Purpose: choose the region for the Q4 returns-reduction pilot. Usefulness: region-level return rates with intervals. A gap of 3 percentage points or more between the top region and the rest is actionable. Audience: operations leadership. They know regions and channels, and they own the pilot site decision. They say "return rate" for returned orders divided by orders. Material unknown: if returns are recorded consistently across channels. Slug: `region-returns`.
- Where landed originals are kept: `SANDBOX/storage/raw`.
- Source restrictions: internal; no customer PII.
- Cleaning decisions (request 4):
  - Rows recorded twice are duplicate landings. Drop the copies.
  - An amount of -999 means missing.
  - Large amounts are real orders.
  - Orders whose customer is not in the customer list come from a partial customer extract. Keep these orders and record the limitation.
  - Slash dates are month/day/year.
- Package datasets: none.
- Where released packages are kept: `SANDBOX/storage/releases`.
- Disposition for any flagged finding at release: release it with the caveat.
- Second investigation (request 16):
  - The population and the period are the same.
  - Purpose: decide if channel return recording needs an audit before the pilot.
  - Usefulness: channel rates with intervals, and any channel whose rate is different from the others by 3 points or more.
  - Slug: `channel-returns`.
  - Inherit the region-returns method and settings.
- Anything else: choose the reasonable answer, and mark it `(assumed)`.
