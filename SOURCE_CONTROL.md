# Working baseline: BunnyWorld 0.2.0.5

This repository contains the complete 0.2.0.5 Godot source, prepared game resources, rebuilding tools, release documentation and validation evidence. `main` is the current working baseline. Historical 0.1 project attachments are not the development baseline.

## First checkout

1. Clone/download this repository.
2. Run `python tools/restore_repository_assets.py` from the repository root (`python3` on Linux/macOS).
3. Open `project.godot` with Godot 4.5.1 stable, GL Compatibility. Godot regenerates its own import cache.

All required prepared assets are stored in the repository. Large prepared resources are stored as lossless compressed parts under `repository_assets/` because GitHub's upload API rejected the largest single-file payloads. The restore script uses only Python's standard library, checks every part and restored SHA-256 value, and recreates the exact tested files. There are no external asset downloads and no Git LFS setup. Restored files are intentionally ignored by Git; their compressed parts and `ASSET_RESTORE.json` are tracked.

Normal Windows testing still uses the separately delivered Windows ZIP and requires no Python or editor. Compiled EXEs/ZIPs, editor caches and local save files are not source-control items.

## Baseline identity and checks

Application/EXE version: **0.2.0.5**. World scenario remains `bunny_world_2000_0_2_0_3`, save schema 10. Counts: 223 countries, 1,233 States, 13,481 provinces and 6,144,737,528 residents.

`BUILD_INFO.json` identifies the tested executable and source baseline. `TEST_RESULTS.md` and `validation_0205/embedded_ui_results.json` record the 58 final UI checks, full interaction smoke, model/resource checks and exact-pack integrity verification. Native Windows hardware testing remains separate from the matching Linux runtime tests. `Bunny_World_Project_Handoff.md` describes the accepted behavior and continuation constraints.

This Git import preserves the tested source and assets. Only repository setup/documentation, ignore/attribute rules and the lossless asset-restoration packaging are added. Run the asset restore command before importing/testing/exporting.

## Future changes

Work from `main`, make focused commits, retain the prepared assets, and update version/release notes when a patch is ready. Preserve smooth camera travel, resident materials, fixed terrain grid and cached scenery. The user tests fresh campaigns; do not add old-save compatibility or migration unless explicitly requested.

If a large generated resource is deliberately rebuilt, regenerate its compressed parts and hashes/sizes in `ASSET_RESTORE.json`, then verify restoration before committing. Do not commit ignored uncompressed duplicates or an exported game EXE. Full geographic regeneration may require the original raw datasets/mod, as documented under `documentation/versions/0_2_0_3`; those inputs are not needed to open the prepared baseline.
