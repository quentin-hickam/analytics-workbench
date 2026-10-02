# Knowledge vault

This vault records what one analyst has learned about the data estate they work with: its systems, databases, schemas, and tables. It lives outside every analytics project so that knowledge gained in one project is found when a later project touches the same object. It is plain Markdown, opened in Obsidian; agents read and write it through the filesystem, and no plugin is required.

This file owns the vault's conventions. Read it once per session before consulting or changing any page.

## What belongs here

- Record knowledge about data objects and how to read and use them: meaning, grain, coverage, keys and joins, code values and their meanings, refresh behavior, known issues and their handling, and which object to use for which need.
- Do not record analytical conclusions. Test each statement: would it change if the business changed? "pay_detail excludes contractors" belongs here; "contractor share is rising" does not. A known issue may note that ignoring it once changed a result, without saying which way.
- Do not mirror schemas. Leave out exhaustive column lists, types, and row counts; include a structural detail only where it explains meaning or handling, and say on each object page where its full column list can be read.
- Never record credentials or other secrets, record-level data, or paths that work only on one machine. System, server, and database names, code values, and access instructions are allowed.

## Layout

```text
<vault-root>/
├── AGENTS.md               # This file; the only file a new vault starts with
├── choosing.md             # Which object to use for which need (created when first needed)
├── glossary.md             # Business terms that span objects (created when first needed)
└── <system>/               # One folder per system the analyst connects to or receives data from
    ├── README.md           # What the system is, how it is identified and accessed, system-wide behavior
    └── <qualified-name>.md # One page per object used or assessed, e.g. PAY.dbo.pay_detail.md
```

- A system is a database server, warehouse, application, or provider. Its folder has a short name the analyst chooses. Its `README.md` records what the system is, how it is identified in connections (server, host, or provider name), the databases it holds, how it is accessed, and behavior that applies across it.
- An object is a table, view, file extract, or API endpoint in a system. Name its page by its qualified name within the system: `database.schema.table` for a database, or the extract name or endpoint path otherwise. Replace any character not allowed in file names, including `/`, with `_`.
- If two exact names map to the same file name, including names that differ only in letter case, give each a distinct file name and list the exact-name-to-file mapping in the system `README.md`.
- Start every object page with a line stating the object's exact qualified name. Before using or changing a page, check that this line names the intended object.
- To find an object's page, go by path; otherwise use the system `README.md` mapping, or search the system `README.md` files for the server, provider, or database name when the folder is not obvious. Listing the system folders and searching their `README.md` files is a lookup, not a sweep; do not read pages beyond those you are looking for.
- Put knowledge that applies to many objects on the narrowest page that covers them: the system `README.md`, or a database or schema page named by its qualified name (`PAY.md`, `PAY.dbo.md`).
- Create a page only for an object the analyst has used or assessed, including one rejected for a need, and only when something is recorded about it. Never populate the vault from a system catalog.

## Pages

- An object page covers, as far as known: what the object is and its grain; keys and how it joins to other objects, with cardinality and conditions; fields whose meaning, coding, or behavior is not obvious from their names; coverage and refresh behavior; known issues and how to handle them; copies of it in other systems, or the object it copies, with any lag; and where its full column list can be read, usually the system's own catalog. No section and no frontmatter is required.
- `choosing.md` has one entry per recurring need: the preferred object, alternatives and when they fit, objects to avoid and why, and the coverage and date the preference rests on. Comparative preference lives only there; object pages state facts.
- `glossary.md` holds business terms used across objects or systems, even when one field defines them. Link each entry to the object pages its definition rests on. A term that describes only one field of one object is recorded on that object's page.
- Give each claim, inline, its date and how it was established (documentation, a query or check, the system owner's word, or the analyst's statement when no other basis was given), for example "a rerun pay run duplicates rows per (employee_id, pay_period); keep the highest run_id within each (checked by query, 2026-08)". Use the date the fact was observed, or the recording date when none was given. State the period a claim covers when it is about a period. Refreshing one claim never makes another look current.
- When new evidence differs from a recorded claim, keep the earlier claim unchanged, with its date, basis, and whatever scope it stated, and add the new claim beside it with its own. If handling advice needs narrowing, add a separate dated line saying how far the new evidence narrows it rather than editing the earlier claim.
- When an object is renamed or moved, rename its page, update links to it, and keep the old name on the page.
- Write file-relative Markdown links between pages, linking to the page file rather than a heading. Obsidian resolves those and any wikilinks a person adds.

## Writing

- Write to this vault only when the user explicitly asks. Before writing about an object, read its system `README.md`, any database or schema page above it, and its own page. Apply the boundary test above; when a candidate statement fails it, explain why and leave it out.
- Put each fact on the narrowest page it applies to, creating that page and its system `README.md` when absent. Create `choosing.md` or `glossary.md` only when there is an entry for it.
- Record only facts that were supplied or established; do not fill in what was not.
- Git is optional. If this vault is a Git repository, commit only on explicit request.

## Sharing with a team (optional)

A solo vault never depends on this section. A team can share a vault by keeping it in a Git repository with a remote. Then pull fast-forward-only before changing pages and stop if the clone has diverged; push only on explicit request; do not also sync the folder through a file-sync service or Obsidian Sync; and add the observer's initials to each new claim. Curation and review policy are the team's choice.
