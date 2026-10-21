# Developing BunnyWorld 0.2.1.4

Godot 4.5.1 Standard, GL Compatibility. Fresh campaigns only. Provinces are movement tiles and unique-building sites; state populations/demographics are independent of province count. No save migration.

## Map style and capital decoration

Application 0.2.1.4 uses the existing 0.2.1.2 geography/display bundle. Shared shader defaults control near/far country tint, ribbon intensity, coastal shelf/foam and terrain detail strength. Border widths remain screen-space; state/province lines are subordinate to national outlines. No additional texture samples, buffers or terrain geometry are introduced by these style changes.

`python tools/clean_obsolete_capitals.py` removes only GeoNames cities500 additions ranked below 10,000 that are neither national nor current state capitals, together with their synthetic State capital clusters. Original mapped settlements and larger added cities remain. It clears stale capital flags, recomputes decorative priorities/weights and refreshes the ordinary JSON bundle checksums. It never changes world/province topology or resident populations. Rank is a decoration filter, not a demographic estimate. Repeat runs are safe; test with `python tests/obsolete_capitals_tests.py`. Historical generators remain historical reproduction tools, not commands to run over current geography.

Labels/city architecture, coastline province lookup and terrain geometry are separate future work.

## Clean globe stabilization

The current application is 0.2.1.4 on clean-globe; geography/display remain 0.2.1.2. Canonical IDs are 6144×3072 with 1,252 states, 13,074 land provinces and 784 seas. Earlier .28/.29 reproduction notes below describe historical geography; do not run those generators over this map.

The clean surface uses one 384×192 sphere, spatial border/river batches and the existing atmosphere. There is no detail patch. DisplayCoverage.initialize(target, false) loads the required coast/tiny-land/sea fields but skips the unused boundary hint/pair/distance textures and local coast packs. Legacy callers retain the default behavior. Three skipped fields are 3072×1536 × (1+4+2) bytes = 33,030,144 bytes (31.5 MiB), excluding driver overhead. The sandbox shares immutable textures between both materials.

Camera transforms/horizon scans are cached; selection visibility changes still trigger culling. View uniforms use distance/mode keys and are invalidated on palette/shader changes. Hover uniforms update only when the hover changes. The 10 Hz stationary redraw policy and independent simulation remain intact. Ocean-neighbor taps are gated to the union of the existing coastal-effect bands, including selected-sea behavior.

The published branch's scenery checksum and generator fingerprints were stale. Prepared borders/chunks were rebuilt from the unchanged PNGs/membership with the checked-in generators; active packs and contracts were republished together. Do not merely rewrite generator fingerprints to bypass rebuilds. Run preparation verification and repository hygiene after pulling.

Validation: Godot 4.5.1 model tests, political_ui_tests.gd, clean_globe_stability.gd; Python tools/restore_repository_assets.py --verify-only; Python tools/build_map.py --check; Python tools/repository_hygiene.py. A GL Compatibility render probe also exercises distant political/physical and close physical views under Mesa llvmpipe. This verifies rendering, not target-laptop speed. The fixed globe mesh remains coarser than the full CPU relief field at extreme zoom; this patch does not change terrain geometry/picking algorithms.

## Government and political power

GovernmentRules is the shared source of valid properties/options and the default 100 PP change cost. WorldState validates player ownership, a genuinely different valid option and sufficient PP before changing the property and charging atomically. New saves (schema 20) persist settings, balance and named additive daily modifiers; validate every political field before committing a load. No old-save migration.

WorldState.advance applies the number of crossed midnights × the actual daily total, once per country per day boundary; paused time gives no income. Base gain is +1. PP balances reuse starting_stats.political_power as the live statistic. Properties do not yet apply political modifiers. Government choice windows refresh affordability on daily ticks; purchases refresh the top bar immediately.

political_summary.gd shares the large/compact portrait and parliament layout. Only player-country compact parliament has an activation callback. political_panel.gd uses native buttons and an exclusive AcceptDialog. political_power_indicator.gd renders a BBCode tooltip from the same breakdown used by the simulation. Country panels remain 370px; Government is 600×480px, capped to available space. Run `Godot --headless --path . --script res://tests/political_ui_tests.gd` for integration checks.

Application/geography/display 0.2.1.2 uses one 8192×4096 province ID PNG and 4096×2048 universal border/coast fields. Active builders obtain native dimensions from map_dimensions.py; the source is province_ids.png. Tiny states/inhabited-island anchors are protected; no IDs or population are removed. See documentation/MAP_EDITS.md for reproduction and measurements. The existing government/PP systems are retained.

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
