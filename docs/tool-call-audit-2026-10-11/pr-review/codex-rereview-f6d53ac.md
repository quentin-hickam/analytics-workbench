The fixes in `f6d53ac` are sound. No actionable findings.

- Non-text flag keys no longer crash export or check-draft. Flag sync completes before file writes; state read failures preserve `revalidation_flags` and report `flags_error`.
- Manifest `results` includes serialized and narrative-only results. Status detects their reruns and reports unknown for older manifests without `results`.
- The regression tests reproduce the original failures on `bf8935b`. Additional probes passed for mixed chart/prose packages and write ordering.
- The manifest template and changelog describe the behavior accurately.

Full suite: **276 passed in 54.22s** using the supplied interpreter and command. No tracked files changed.