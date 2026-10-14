# Blind ideation, 2026-10-14

Two agents, Codex and Claude Opus, were each given the same design prompt with no access to this repository. The prompt asked for a package for conversational data analysis that works under GitHub Copilot. Their proposals were then compared with the workbench as it stood at `5e8dc02`.

- [brief.md](brief.md): the prompt and session rules given to Codex. Opus received the same prompt with equivalent rules, and was allowed web research to confirm Copilot's extension mechanisms. Codex also ran web searches.
- [codex-proposal.md](codex-proposal.md): Codex's proposal, "Inquiry".
- [opus-proposal.md](opus-proposal.md): Opus's proposal, "Casefile".

The proposals agreed with the workbench on its core: skills as the entry point, a deterministic helper that owns state, a persistent question ledger, and deck inputs whose numbers trace to recorded results. Both went further than the workbench in three areas:
- They treat GitHub Copilot as the primary host.
- They hide the workbench's machinery from the person in conversation.
- They structure the ledger as a tree that drives the deck's storyline.

The resulting plan takes these up in phases. [../copilot-compat.md](../copilot-compat.md) records the Copilot research behind the first phase.

Copilot facts in the proposals reflect each agent's own web research on 2026-10-14. Where they differ from `copilot-compat.md`, the compatibility doc governs.
