### Fixed

- Cross-part copies are removed without another decision only when the user or source documentation calls the parts re-extracts. An observed overlap or prior knowledge is insufficient.
- Cleaning scans separate `duplicate-rows:across-parts` from remaining `duplicate-rows`. Their counts follow the correction view's dropped and retained rows, allowing independent quality decisions and rescan statuses through the CLI and MCP.

### Changed

- Pairwise comparison is needed only when a cross-part issue spans more than two parts; lineage guidance identifies the part column first.
