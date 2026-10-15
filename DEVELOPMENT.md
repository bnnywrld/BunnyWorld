# Developing BunnyWorld 0.2.0.7

Baseline: `main` 0.2.0.6 (`47d553c`), Godot 4.5.1 Standard, GL Compatibility. The accepted country/coast mask and resident terrain/camera/scenery architecture are retained. No Windows export is part of the normal source-update workflow.

## Geography rules

Original MD January-2000 state history and definition.csv are the count authority. Exclude dummy ID 0, sea and lake entries: 1,250 States and 13,221 land provinces. Every country has MD <= new State count <= floor(1.2 * MD), with at most one recorded extra State for an important geographic area in a small country. Natural Earth ADM1 units are grouped along shared boundaries, prioritizing MD regional-name hints and source administrative groups. A terrain-guided Bavaria/Franken subdivision is needed to meet Germany's MD minimum of 17.

Natural Earth disputed polygons reserve State boundaries with the existing scenario controller. Small secondary country intersections caused by source generalization are removed. A >95% protected-country coverage absorbs unprotected coastline fringes. Sapodilla/Southern Belize, the two Danube islands, and the nested Jerusalem features use explicit protected groupings to respect strict budgets; each source identity is retained. This is geographic preparation, not an implementation of future dispute activation/events.

Province budgets use original MD land counts per country and geographically registered MD province centres as smoothed distribution hints. No MD boundary shape is reused. Independent provinces grow on local Lambert equal-area grids with settlement, relief, river and administrative guidance. Every State has at least one province; substantial separate islands can require additional seeds. Native atlas repair removes slivers and disconnected pieces on the same landmass.

## Regeneration

Python dependencies: numpy, Pillow, scipy, rasterio, shapely, pyproj, scikit-image; matplotlib for offline QA. Prepared input datasets are bundled; restore them first. `tools/md_geography_reference.py path/to/bunnyversion.zip` rebuilds the factual MD reference when needed. The original archive is read only.

Run sequentially:

1. `python tools/build_states_0207.py`
2. `python tools/build_provinces_0207.py`
3. `python tools/repair_province_fragments_0206.py`
4. `python tools/finalize_geography_0207.py` (atomic, verified runtime identity textures)
5. `python tools/link_geography_0206.py`
6. `python tools/build_boundaries_021.py`
7. `godot --headless --path . --script tools/compile_boundaries.gd -- land`
8. `godot --headless --path . --script tools/compile_boundaries.gd -- province`
9. `python tools/package_repository_geography.py`
10. `python tools/restore_repository_assets.py --verify-only`
11. `godot --headless --path . --editor --import --quit`

Close any Godot editor/importer while regenerating. Earlier numbered helper/atlas names remain internal compatibility paths; current final province data are also saved as province_atlas_0207.npz. Do not run the old State coarsener after the budgeted State build.

Country totals are transferred for bookkeeping. Local demographic estimates are deferred. No old-save migration is authorized.

## Focused checks

`python tests/geography_0207_tests.py`; `python tests/asset_restore_tests.py`; the existing model, foundation and territorial-rights GDScript suites; resource_load_tests.gd; geography_0207_ui_tests.gd and ui_0207_tests.gd. Set BUNNY_VALIDATION_DIR to record engine integration results. Headless assertions cannot validate native Windows rendering/performance. `python tools/preview_geography_0207.py` gives offline regional/orthographic views of the exact final atlas.
