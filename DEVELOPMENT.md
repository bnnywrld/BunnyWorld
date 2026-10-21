# Developing BunnyWorld 0.2.1.5

Godot 4.5.1 Standard, GL Compatibility. Fresh campaigns only. Provinces are movement tiles and unique-building sites; state populations/demographics are independent of province count. No save migration.

## Map style and capital decoration

Application 0.2.1.4 uses the existing 0.2.1.2 geography/display bundle. Shared shader defaults control near/far country tint, ribbon intensity, coastal shelf/foam and terrain detail strength. Border widths remain screen-space; state/province lines are subordinate to national outlines. No additional texture samples, buffers or terrain geometry are introduced by these style changes.

`python tools/clean_obsolete_capitals.py` removes only GeoNames cities500 additions ranked below 10,000 that are neither national nor current state capitals, together with their synthetic State capital clusters. Original mapped settlements and larger added cities remain. It clears stale capital flags, recomputes decorative priorities/weights and refreshes the ordinary JSON bundle checksums. It never changes world/province topology or resident populations. Rank is a decoration filter, not a demographic estimate. Repeat runs are safe; test with `python tests/obsolete_capitals_tests.py`. Historical generators remain historical reproduction tools, not commands to run over current geography.

Labels/city architecture, coastline province lookup and terrain geometry are separate future work.

## Clean globe stabilization

The current application is 0.2.1.5 on clean-globe; geography/display remain 0.2.1.2. Canonical IDs are 6144×3072 with 1,252 states, 13,074 land provinces and 784 seas. Earlier .28/.29 reproduction notes below describe historical geography; do not run those generators over this map.

The clean surface uses one 384×192 sphere, spatial border/river batches and the existing atmosphere. There is no detail patch. DisplayCoverage.initialize(target, false) loads the required coast/tiny-land/sea fields but skips the unused boundary hint/pair/distance textures and local coast packs. Legacy callers retain the default behavior. Three skipped fields are 3072×1536 × (1+4+2) bytes = 33,030,144 bytes (31.5 MiB), excluding driver overhead. The sandbox shares immutable textures between both materials.

Camera transforms/horizon scans are cached; selection visibility changes still trigger culling. View uniforms use distance/mode keys and are invalidated on palette/shader changes. Hover uniforms update only when the hover changes. The 10 Hz stationary redraw policy and independent simulation remain intact. Ocean-neighbor taps are gated to the union of the existing coastal-effect bands, including selected-sea behavior.

The published branch's scenery checksum and generator fingerprints were stale. Prepared borders/chunks were rebuilt from the unchanged PNGs/membership with the checked-in generators; active packs and contracts were republished together. Do not merely rewrite generator fingerprints to bypass rebuilds. Run preparation verification and repository hygiene after pulling.

Validation: Godot 4.5.1 model tests, political_ui_tests.gd, clean_globe_stability.gd; Python tools/restore_repository_assets.py --verify-only; Python tools/build_map.py --check; Python tools/repository_hygiene.py. A GL Compatibility render probe also exercises distant political/physical and close physical views under Mesa llvmpipe. This verifies rendering, not target-laptop speed. The fixed globe mesh remains coarser than the full CPU relief field at extreme zoom; this patch does not change terrain geometry/picking algorithms.

## Government and political power

GovernmentRules defines six ordered categories, 28 law choices and the default 100 PP cost. The section uses horizontal rows of 56px icon-only buttons, current-option pictograms, identifying tooltips and small exclusive choice dialogs anchored beside the clicked button and clamped to the viewport. The government title above parliament derives from the form, executive and competition choices. The existing country scroll container scrolls the entire Government content; the pinned country heading remains visible. Government is 600×720px, capped to available space. Country panels retain their 370px width.

`data/government_laws_2000.json` supplies a complete starting law set for each of the 224 active countries. These are editable scenario seeds combining imported MD recruitment/healthcare/labor ideas with broad country policy profiles and explicit anchors (e.g. Japan/UK monarchies, US presidential republic, China one-party rule). They are gameplay abstractions, not a verified historical legal database; minor-country and broad social/economic defaults need future historical refinement. Same-sex marriage is initially illegal everywhere in the 2000 scenario. Nuclear deterrent is seeded only for the scenario's declared nuclear states; Israel uses ambiguity and DPRK starts non-nuclear.

WorldState loads the law seeds once, copies them on reset and atomically validates player ownership, a valid different option and sufficient PP before charging. No choices modify stability, approval, daily PP, economic statistics, elections or diplomatic/military permissions in this UI-only patch. Reform/approval gates await their gameplay implementation. Save schema 21 requires complete valid law dictionaries; fresh campaigns only, no migration. Invalid saves are rejected before altering live state.

`law_icons.gd` contains lightweight vector pictograms and a cached icon per law/option, distinguished by accent and option marks. They rasterize only on first use, with no frame processing or map resources. The UI refreshes after purchases and on existing daily ticks. `political_summary.gd` retains the shared portraits/parliament layout; only the player-country compact parliament activates Government.

PP income remains base +1 per crossed midnight, plus existing additive modifiers, with no income while paused. The top-bar indicator uses the same breakdown; purchases refresh its balance immediately. Run `Godot --headless --path . --script res://tests/political_ui_tests.gd` for all country seed validation, law purchase/affordability checks, popup bounds, no-effect checks, daily income and save/load integrity.

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
