# Repository scope

Keep main runnable. Read README.md, DEVELOPMENT.md and SOURCE_CONTROL.md.

- Commit changed source, current game data, required assets, reproducible build inputs and concise current documentation only.
- Do not add release ZIPs/EXEs, editor caches, CSV translations, patch delivery manifests, screenshots, temporary logs or copied project trees.
- Put temporary work and ZIP packaging outside this checkout. Update existing documentation instead of adding another numbered handoff for each patch.
- Preserve the cartography inputs/baselines used by the toolchain. Numbered source filenames alone do not mean a file is unused.
- After packaging assets run `python tools/repository_hygiene.py --prune`. Stage deletions as well as additions, then run `python tools/repository_hygiene.py`.
- Keep only manifest-referenced asset parts; never remove an active part or a map-contract dependency to save space.
- Do not create persistent remote branches unless requested. Do not rewrite published history without explicit approval.
