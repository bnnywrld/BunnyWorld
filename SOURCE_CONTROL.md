# BunnyWorld 0.2.0.6 geography candidate

The completed geography patch is saved on its own GitHub branch. The accepted 0.2.0.5 baseline remains on main until user testing establishes the next working baseline.

This source includes Godot code, scenario data, prepared resources, generation scripts and validation evidence. After checkout, run `python tools/restore_repository_assets.py` once, then open project.godot in Godot 4.5.1 stable. The restore script checks compressed parts and restored SHA-256 hashes. No Git LFS setup or external terrain downloads are needed.

Large prepared files are losslessly stored under repository_assets, indexed by ASSET_RESTORE.json. Deliberate resource rebuilds must update their parts/hashes and verify restoration. Windows EXEs, ZIPs and import caches are not source-control items.

Application 0.2.0.6; scenario bunny_world_2000_0_2_0_6; 223 countries, 2,107 States and 9,194 provinces. Existing country population/building totals remain bookkeeping. New local demographics are not refined. No old-save migration is authorized.

See DEVELOPMENT.md for the ordered geographic regeneration commands. The old bookkeeping/masks needed by the new build scripts are retained in tools/cartography/baseline_0205, with their original blob contents preserved. No MD province bitmap is used for new geometry. TEST_RESULTS.md and validation_0206 contain current validation evidence.
