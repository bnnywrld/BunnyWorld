# BunnyWorld 0.2.0.28 — province rework

**224 countries, 1,261 states, 13,200 land provinces.** MD has 13,221 land provinces; the previous game had 13,308. The final count is 0.998× MD, below the 15,204 ceiling. World population remains **6,146,495,066**.

## Approved state unions

Lebanon's Beqaa / Nabatieh, North and Mount Lebanon states become **Lebanon** (ID 624, population **3,483,203**). Hezbollah's South Lebanon (ID 461) retains its controller, as confirmed. Shebaa Farms (1758) is absorbed into **Golan Heights** (1750, population **25,898**); starting Israeli control is unchanged.

Population, buildings and building-slot totals are conserved per country. Religion/age are merged by resident counts, education by adults 25+, and workforce by employed/unemployed/working-age counts. At the baseline retirement age, every country's exact displayed demographic counts and workforce totals match .27. Other state profiles are unchanged. No geography merge creates new people or averages percentages indiscriminately.

## Allocation and shapes

The per-country target starts at 1.0× MD's province count. State weights are **sqrt(area × population)**, with one minimum and capped iterative redistribution. Allocation caps use floor(area / **400 km²**) and at most three provinces for states below 2,500 km². The 400 km² value is a geometry safeguard rather than a camera calculation. The pixel-click rule was explicitly discarded. An **8 km inscribed-width target** identifies narrow exceptions; it is not an absolute ban on naturally tiny states, islands or city footprints. Those cases are listed in data/province_width_exceptions_0228.json.

Micronesia keeps 11 provinces against MD's 32 and Tuvalu one against four because of the caps. Missing MD entries for Nauru and Timor-Leste retain their existing country budgets. Targets are not inflated elsewhere merely to spend an island-country shortfall.

Local Lambert equal-area growth uses NOAA relief, major rivers and settlement hints. Constrained centroid relaxation and multi-label smoothing encourage compact shapes. MD polygons are never warped or copied. Major-city tiles use connected sampled ESA year-2000 urban footprints where usable; the city tile stays inside the state budget. A single-province state necessarily combines its city and countryside. Coarse or absent urban footprints fall back to settlement-guided partitioning rather than invented exact city boundaries.

Tiny disconnected original footprint pieces share province IDs rather than attracting their own seeds. Different source islands may share a province, without adding artificial overland neighbor links. The native connectivity audit reports **0 disconnected same-landmass scraps**. It records 1435 province groups spanning distinct original components and 41 narrow footprint exceptions. Existing state/coast geography is preserved; this patch does not repair inherited state enclaves.

Generated internal corners use bounded rounded curves. State/coast junction endpoints remain pinned; real administrative/coastal/geographic angles may remain. Line meshes, fills and highlights use the same shared curve preparation. This is a finite-resolution raster plus smooth render curves, not an exact cadastral vector map.

## Data and rebuilding

Provinces contain **no population**: they are movement tiles and unique-building sites. Age/religion/education and workforce remain on states. No jobs, migration, military movement or population simulation is introduced. All approved earlier territory removals and state exceptions remain. Antarctica stays neutral terrain outside ordinary gameplay state/province counts.

The validated shared pipeline rebuilds canonical province PNG IDs, index, province/state adjacency, borders, current selection distance/pair fields, boundary hints, coastal windows and spatial render batches. It also relinks capitals, cities, city groups, scenery and protected-territory references. All 2,787 scenery clusters, their decorative instances, eight landmarks and 2,340 city records are retained. A previously unlinked Managua source point now has a valid controller/state/province reference.

Province-border mesh triangles: **605,540 → 395,232**. Counts and curves are checked; no FPS claim is made. Native Windows visuals and GPU performance still need user testing. Terrain materials and graphics settings are unchanged.

## Verification

- **110,687 data checks** passed, including exact accepted state/coast/Antarctic pixel preservation, no orphan live IDs, all 23,851 internal neighbor edges represented, pickable province anchors, valid references, and country total conservation.
- **39,260 Godot 4.5.1 headless checks** passed, including all runtime picking-image anchors, live membership, inline charts, workforce, exact national demographic totals, browser hover, offscreen ownership transfer and same-version save/load.
- Prepared assets, map build contract, asset restoration fixtures and whitespace checks passed. Ownership upload checks inspect CPU upload bytes, not hardware GPU readback.

## Apply and test

Apply the changed-files ZIP over **0.2.0.27**, with Godot/game closed. Run **Prepare_BunnyWorld.bat**, open with **Godot 4.5.1 Standard**, allow imports to finish and start a **fresh campaign**. Application, geography and display versions must all be .28. Old saves are unsupported; province IDs have been regenerated. This is source/prepared data, not an exported EXE.

1. Inspect Lebanon and Golan Heights; check population, inline charts and separate workforce figures. Confirm Hezbollah still has South Lebanon.
2. Inspect province density and borders in India/China, Germany, the continental USA, Sahara and Greenland. Check Tokyo or another major city, Micronesia, Papua New Guinea and the retained neutral Antarctica.
3. Click provinces, hover state-browser buttons and check capitals. Change a state owner while another continent is in view, then inspect the result and use F5/F9 save/load. Compare political-mode movement smoothness with .27.

The complete before-generation country/state table is [ALLOCATION.md](provinces_0228/ALLOCATION.md). Machine-readable allocation, generation, width and connectivity reports are under data/. Historical numbered caches/reports, including the frozen .27 population-grid aggregate, describe their original IDs and are not current province authorities. See DEVELOPMENT.md for regeneration order and dependencies.
