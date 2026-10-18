# Developing BunnyWorld 0.2.1

Godot 4.5.1 Standard, GL Compatibility. Fresh campaigns only. Provinces are movement tiles and unique-building sites; state populations/demographics are independent of province count. No save migration.

## Government and political power

GovernmentRules is the shared source of valid properties/options and the default 100 PP change cost. WorldState validates player ownership, a genuinely different valid option and sufficient PP before changing the property and charging atomically. New saves (schema 18) persist settings, balance and named additive daily modifiers; validate every political field before committing a load. No old-save migration.

WorldState.advance applies the number of crossed midnights × the actual daily total, once per country per day boundary; paused time gives no income. Base gain is +1. PP balances reuse starting_stats.political_power as the live statistic. Properties do not yet apply political modifiers. Government choice windows refresh affordability on daily ticks; purchases refresh the top bar immediately.

political_summary.gd shares the large/compact portrait and parliament layout. Only player-country compact parliament has an activation callback. political_panel.gd uses native buttons and an exclusive AcceptDialog. political_power_indicator.gd renders a BBCode tooltip from the same breakdown used by the simulation. Country panels remain 370px; Government is 600×480px, capped to available space. Run `Godot --headless --path . --script res://tests/political_ui_tests.gd` for integration checks.

Application .2.1 uses unchanged .29 geography/display bundles. Do not regenerate or repackage map resources for this update.

## Reproduce .28 geography

Dependencies: Python 3, numpy, Pillow, scipy, rasterio, shapely, pyproj, scikit-image. The .27 baseline snapshot and accepted states_0228.npz are included for reproducibility. NOAA relief and ESA/river source datasets are retained from the existing project. No MD polygons are used; data/md_geography_reference.json provides counts only.

From a clean .27 project, capture its exact runtime demographic counts with tools/capture_baseline_0228.gd and preserve the data under tools/cartography/baseline_0227. Run tools/prepare_provinces_0228.py once to apply approved state unions and write the allocation report before generation. Its guard prevents repeated merging. The supplied final project already contains these inputs; do not run preparation again over .28.

Sequentially, with editor/game closed:

1. python tools/generate_provinces_0228.py
2. python tools/link_provinces_0228.py
3. python tools/build_map.py --godot /path/to/Godot_4.5.1
4. python tools/restore_repository_assets.py --verify-only
5. python tests/provinces_0228_tests.py
6. Godot --headless --path . --script res://tests/provinces_0228_runtime.gd

The shared build regenerates adjacency, canonical index, all live boundary/selection fields and spatial mesh batches. It packages checksum-verified prepared resource parts. Native PNG publication is atomic and decoded before replacement. Curve algorithm hashes are inputs to the map contract so a smoothing change cannot leave stale line meshes.

The allocation uses sqrt(area * population), one province minimum, country MD land targets at 1.0 scale, iterative cap redistribution and a global <=1.15× MD limit. The 400 km² allocation cap and 8 km width target are geometry safeguards, not a camera/clickability requirement. Tiny state and urban footprint exceptions are reported. Small original disconnected pieces share IDs; significant original islands can have seeds within the same fixed budget. A province grouping islands creates no artificial overland adjacency.

State/coast silhouettes remain immutable after the explicit unions. Do not run an older numbered state/province generator or restore an old grouped atlas over the canonical .28 tiles. Older numbered reports/caches describe historical releases and are not current ID authorities. data/population_grid_0227.json is a frozen source aggregation on .27 IDs, not population on new movement provinces.
