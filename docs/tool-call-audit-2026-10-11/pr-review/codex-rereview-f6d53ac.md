The fixes in `f6d53ac` are sound. There are no actionable findings.

- Non-text flag keys no longer crash export or check-draft. Flag sync completes before file writes. State read failures preserve `revalidation_flags` and report `flags_error`.
- Manifest `results` includes serialized and narrative-only results. Status detects their reruns and reports unknown for older manifests without `results`.
- The regression tests reproduce the original failures on `bf8935b`. More probes passed for mixed chart/prose packages and write order.
- The manifest template and changelog describe the behavior accurately.

Full suite: **276 passed in 54.22s** with the supplied interpreter and command. No tracked files changed.