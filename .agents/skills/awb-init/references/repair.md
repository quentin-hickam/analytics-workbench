# Repair and upgrade

1. Run the installer with `--upgrade`. The request of the user authorizes this. The installer installs missing helpers and guides. It replaces only `earlier` copies, unmodified copies that its receipt recorded, of helpers, package formats, and workbench guides. It records what it writes in the `.awb-receipt.json` of the project.

   ```sh
   python3 <skill-directory>/scripts/install_helpers.py <project-root> --upgrade
   ```

2. When the installer reports `customized` files or `retired` files, ask the user one time about all of them:
   - Show the difference of each customized file (`git diff --no-index <project file> <asset>`, with the asset from `customized`). Ask if the user wants to replace, keep, or merge it.
   - Ask if the user wants to remove the unmodified retired files.
   - The project no longer imports a customized retired helper under `src/`. For such a helper, show its history and its uncommitted changes (`git log -p --follow -- <file>` and `git diff -- <file>`). Ask if the user wants to port its changes into the current helper or remove it.

   Then run the installer again with `--upgrade`, with a `--replace <path>` for each file to replace, and with `--remove-retired` if the user agreed. Make hand merges and ports with ordinary edits, and keep the changes of the project. Delete each ported helper. Other customized retired files belong to the project. Keep them and report them.
3. Reconcile `AGENTS.md` and `README.md` with the [agent instructions](../assets/workbench/AGENTS.md) and [orientation](../assets/workbench/README.md) templates:
   - Add what the template holds and the project does not have, for example routing to every skill, command conventions, and **Asking for things** requests.
   - Delete lines that name workbench skills, commands, or paths that the template no longer has.
   - Keep project-specific content.
4. Reconcile the `run.py` of each investigation with the [template](../assets/workbench/investigation/run.py) (`git diff --no-index`). Take the changes of the template, and keep the producers and other adaptations of the investigation.

Repair is complete when all these conditions are true:

- The last installer output shows each file as `installed`, `current`, `replaced`, or kept or merged by the choice of the user.
- The last installer output shows each retired file as `removed`, or kept by choice.
- Each customized retired helper is ported or removed.
- Each `run.py` matches its template, except for the adaptations of the investigation.
- Both root files match their templates, except for project content.

Also report each investigation that does not have a `run.py`. That investigation gets one before its next rerun.
