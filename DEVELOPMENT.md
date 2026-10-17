# Developing BunnyWorld 0.2.0.28

Godot 4.5.1 Standard, GL Compatibility. Fresh campaigns only. Provinces are movement tiles and unique-building sites; state populations/demographics are independent of province count. No save migration.

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
