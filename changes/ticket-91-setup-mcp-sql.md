### Added

- The MCP `setup` tool takes an `interpreter` argument, the absolute path of the Python that will run the project's analysis, and runs the installer under it, so setup records that interpreter.
- `awb.py sql` binds a query's `$name` parameters: `--param name=value`, repeatable, reads each value as a TOML value as settings are (`2026-01-01` is a date, `5` an integer, other text a string), and `--settings <investigation>` binds that investigation's settings `[parameters]`, with `--param` winning. The MCP `read` tool's `sql` takes them as `params` and `settings`.

### Changed

- The installer refuses, writing nothing, to record an interpreter outside the project that cannot import the helpers' packages, such as the MCP server's own Python on a fresh project; it names the missing packages, the install command, and the `interpreter` argument. Its refusal over a README naming another interpreter spells the line that switches to the one it runs under.
- `awb-init` creates the project's `.venv` with `duckdb` and `pandas` before setup when the project has no virtual environment and the user names no interpreter, asking once when that fails, and reports which interpreter setup recorded. It also writes the storage locations the user names on README's `Landed data is kept at` and `Released packages are kept at` lines, and states the forms the helpers copy to.
- The project `AGENTS.md` names the `awb` MCP tools as the route for helpers and the command line as the fallback, instead of a second paragraph saying to run helpers with `python3 src/awb.py`, and asks the user before changing a shipped helper or `package-format/` template. Each skill that runs helpers says the same in one line under its heading.

### Fixed

- `awb.py sql --read-only` no longer answers every statement it cannot plan, an unbound parameter or an ambiguous column included, with advice to run it without `--read-only`; it returns DuckDB's error with the likely fix. Without `--read-only`, an unbound parameter gets the same fix, and `profile`, which binds no parameters, says to write the value into the query or run it with `sql --param`.
- A query argument on one line ending in `.sql` that names no file is reported as a missing query file by `sql` and `profile`, instead of being parsed as SQL text.
