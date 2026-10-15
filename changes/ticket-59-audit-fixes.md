### Added

- Optional per-question `audience` wording for the Open questions slide, set through `questions add --audience` or edited in any status through `questions edit --audience`. Whitespace is collapsed, an empty value clears it, and question lists and the rendered ledger show it when set.
- Server registration warnings for Python older than 3.10 or an interpreter running in a virtual environment; the entry still prints unchanged.

### Changed

- The single project MCP rule covers `awb.py`, investigation run scripts, and every shipped skill script, with explicit tool and command routes and the absolute project root on every call. Initialization names the `setup` route before project instructions take effect.
- Scoping assigns question priority and parent from the decision the question serves; brainstorming carries its ranking into those fields, and exploration records the parent with `should` priority unless the user says the decision rests on the answer.
- Packaging saves audience wording without changing analytical question text and presents it with the headlines for approval. An approved reorder that priority and parent cannot express without changing their meaning keeps the derived order and is explained to the user.

### Fixed

- Open questions matches each required question's audience wording when set and its text otherwise. Unset wording whose text fails the names check gets a precise `questions edit … --audience` repair instruction. Answered required questions awaiting recheck can keep their analytical identifiers while passing both draft checks.
- Ledger trouble no longer blocks finding writes or deletes new evidence: findings, state, and history are saved, the question view stays untouched, and the result reports a `questions` error naming its repair, plus the link command for a result that declares answers. Ledger writers continue to refuse drift.
- Release reporting relays what to copy and the full storage destination when storage is unreachable, including after recording a location and when copying existing releases without creating one.
- Reviewer launch distinguishes an unavailable agent from a failed `awb/read` call, counts the latter as a command problem, and names installation, Local session, or server registration remedies.
- Guide paths include VS Code's shared skills location; registration reports offer the printed entry with its destination and require a stable Python 3.10+ interpreter outside project virtual environments. Compatibility documentation leaves reviewer tool behavior to field-test confirmation, and status suggestions use plain requests.
