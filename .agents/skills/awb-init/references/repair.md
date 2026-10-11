# Repair and upgrade

1. Run the installer with `--upgrade`. The user's request authorizes it: it installs missing helpers and guides and replaces only `earlier` copies, unmodified versions the skills shipped, of helpers, package formats, and workbench guides. It records what it writes in the project's `.awb-receipt.json`.

   ```sh
   python3 <skill-directory>/scripts/install_helpers.py <project-root> --upgrade
   ```

2. When it reports `customized` files or `retired` files, ask the user once about all of them: show each customized file's difference (`git diff --no-index <project file> <asset>`, the asset from `customized`) and ask whether to replace, keep, or merge it; ask whether to remove the unmodified retired files. A customized retired helper under `src/` is no longer imported: show its history and uncommitted changes (`git log -p --follow -- <file>` and `git diff -- <file>`) and ask whether to port its changes into the current helper or remove it. Then rerun the installer with `--upgrade`, a `--replace <path>` for each file to replace, and `--remove-retired` if agreed. Make hand merges and ports with ordinary edits, keeping the project's changes, and delete each ported helper. Other customized retired files are the project's own; keep and report them.
3. Reconcile `AGENTS.md` and `README.md` with the [agent instructions](../assets/workbench/AGENTS.md) and [orientation](../assets/workbench/README.md) templates: add what the template holds and the project lacks, such as routing to every skill, command conventions, and **Asking for things** requests; delete lines naming workbench skills, commands, or paths the template no longer has; keep project-specific content.
4. Reconcile each investigation's `run.py` with the [template](../assets/workbench/investigation/run.py) (`git diff --no-index`): take the template's changes and keep the investigation's producers and other adaptations.

Repair is done when the last installer output shows every file `installed`, `current`, `replaced`, or kept or merged by the user's choice, every retired file `removed` or kept by choice, each customized retired helper is ported or removed, each `run.py` matches its template apart from the investigation's adaptations, and both root files match their templates apart from project content.

Report also each investigation without `run.py`, which gets one before its next rerun.
