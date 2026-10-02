---
name: awb-vault
description: Create an analytics workbench knowledge vault, or record knowledge about the data estate in one, only when the user explicitly asks. Reading the vault during project work is governed by the project's AGENTS.md and does not need this skill.
---

# Workbench knowledge vault

A knowledge vault records one analyst's knowledge about the data estate across projects. Its root `AGENTS.md`, written from the [vault conventions](assets/vault/AGENTS.md), owns page naming, layout, claim dating, and the writing rules; this skill supplies only the procedure for creating a vault and recording knowledge in it. Run it only on an explicit request. Other project work never writes to the vault as a side effect.

## Resolve the vault

Use the path the user names; otherwise the `WORKBENCH_VAULT` environment variable; otherwise an equivalent line in the user-level agent instructions. If none gives a path, ask for one. The skill works with or without a project, and no data-project target check applies. If the vault is a Git repository with a remote, follow the vault's team-sharing section: pull fast-forward-only before changing pages, and stop if the clone has diverged.

## Create a vault

1. Create the directory if it does not exist.
2. If `AGENTS.md` already exists there, leave it unchanged and report that the vault already exists, then continue at step 4.
3. Otherwise read the [vault conventions](assets/vault/AGENTS.md) and write that file as `AGENTS.md` at the vault root, unchanged. Create nothing else: system folders, object pages, `choosing.md`, and `glossary.md` are created later, on request, as knowledge is recorded. If the folder already holds other files, such as an existing Obsidian vault, leave them unchanged and tell the user that the conventions now apply alongside them.
4. Report the vault path and, when `WORKBENCH_VAULT` does not already point there, tell the user to set it or add an equivalent line to their user-level agent instructions so projects can find the vault. Leave their configuration for them to change.

A repeated create changes nothing.

## Record knowledge

If the resolved path has no `AGENTS.md`, the vault does not exist: stop, write no pages, and offer to create it.

1. Read the vault-root `AGENTS.md` and follow it for every step below.
2. Identify each object and each statement to record. Take them from the user's request and, inside a project, from the project records that hold the claim: `foundation/sources.md`, `foundation/quality.md`, `foundation/glossary.md`, and `foundation/catalog.md` only to understand which estate object a project dataset rests on. The project's own datasets, views, caches, and analytical conclusions never go in the vault.
3. Apply the vault's boundary test to each statement. Leave out every statement that fails it and explain why to the user.
4. For each object, read its system `README.md`, any database or schema page above it, and its own page before writing.
5. Write each statement on the narrowest page it applies to, with its date and basis. When it differs from a recorded claim, keep the earlier claim unchanged beside the new one, and narrow handling advice only as far as the new evidence supports. Record only what was supplied or established. Create only the pages these statements need, including a system `README.md`, `choosing.md`, or `glossary.md` when absent and needed.

### Project bookkeeping

Inside a project, project records stay governed by the project's `AGENTS.md`. When project work contradicted or extended a vault page, the relevant foundation record should already note it; if it does not, report the gap rather than editing the record. The one edit this skill makes to a project is a plain-text reference such as `vault: payroll/PAY.dbo.pay_detail.md` beside a claim the user asked to record, and only when that claim already sits in a foundation record. When unsure whether an edit qualifies, report it instead of making it.

## Finish

If the vault is a Git repository, commit only on explicit request, and push only on explicit request. Report:

- the vault path;
- pages created and pages changed;
- the statements recorded on each page;
- statements declined and why; and
- contradictions kept side by side.
