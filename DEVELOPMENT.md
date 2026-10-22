# Developing BunnyWorld 0.2.1.8

Godot 4.5.1 Standard, GL Compatibility. Fresh campaigns only. Provinces are movement tiles and unique-building sites; state populations/demographics are independent of province count. No save migration.

## Construction (0.2.1.8)

`construction.gd` owns the player-only queue via a weak reference to WorldState. Entries lock their construction-point quote and cash/borrowing split on purchase. Allocation walks queue order, at most 10 factories per job, from the current owned civilian-industry count; the remainder is labeled Manufactured Goods. No goods units/stockpile are fabricated. Completed jobs update state building counts and add their annual GDP output exactly once. Ownership losses pause affected jobs; existing progress can still be cancelled. Newly completed factories enter capacity the next day. Simulation uses daily batches; no queue work occurs while paused or empty, and a completed job's excess daily points are not carried between jobs.

MD's base construction speed is 4 points/factory/day. The first scaffold adapts the MD .75 infrastructure coefficient to a +7.5% speed bonus per level, excluding infrastructure itself. It does not implement technology, law or sector modifiers. Monetary prices are MD billion-USD values from the supplied building pricing table; construction-point costs and per-level extra costs are separate fields. Refunds return cash × unfinished fraction and reverse borrowed × unfinished fraction, with any already-repaid borrowing returned to cash. Queueing and cancellation never add GDP. Infrastructure/Internet/Railroads cap at 10 with independent slots. Other caps/shared/coastal rules follow MD. Existing counts above a normal per-type cap are retained as the minimum allowed cap; current networks are already within ten levels. Electrical-grid specializations are mutually exclusive for new construction.

Capacity = floor(2 + 5 ln(1 + area_km²/250) + 8 ln(1 + population/50,000)), with a floor of existing shared buildings + max(4, ceil(existing × .25)). Capacity is seeded once on fresh campaigns, reserves queued shared buildings, and never shrinks beneath an existing city layout. This is provisional game balancing, not an MD limit or physical land-use model. It gives large and populous states substantial room while keeping small states compact.

GDP retains the original country GDP/person × current owned population and adds completed state output. MD base per-building billion-USD coefficients are multiplied by the owner's starting overall_productivity/1000 (neutral sector modifiers, full staffing); network/energy direct contributions use the MD constants. Full staffing is a scaffold assumption: employment, resource inputs, energy constraints, productivity growth and macroeconomics are not enabled. GDP accessors feed country summaries, top bar, ledger and GDP map modes. Construction/manufacturing assignments do not remove an existing factory's GDP. Added output follows state ownership; it is not deposited in Treasury.

`construction_panel.gd` uses shared navy/gold styles, a building picker, bounded 30-entry queue pages, current/wanted factory counts, progress/ETA, priority and refund controls. `main.gd` dispatches state clicks without replacing the tab. Private map mode 8 disables the normal picker while open, saves the previous 0–7 mode, and restores it on close, Escape, tab switch or loading. States stay visible; province/city clutter is hidden. The shader uses an 8192×1 R8 queue flag texture (8 KiB) and a screen-space yellow stripe calculation only in Construction mode. No geography/membership assets or meshes are regenerated. Slot reservation caches rebuild once per queue topology revision; progress-only ticks refresh the UI without palette uploads.

`tools/import_construction.py /path/to/bunnyversion.zip` reproduces `data/construction.json` from the supplied MD building/money scripts. It derives coastal states offline from existing province/sea masks, excluding inland water, and writes no map files. The state Railroads entry deliberately uses MD rail_terminal as a state-network abstraction. Province rail routes/ports/forts, new Data Centers and research facilities remain separate future work.

Save schema 23 persists queue IDs, locked quotes, payment split, factory preferences, progress, completed buildings, state capacity and added GDP. Validation checks ownership tags, capacities, limits, coastal rules, finite amounts and valid queue identifiers before assigning any live state. No old-save migration.

## Organizations (0.2.1.7)

`organization_rules.json` adds metadata without modifying the canonical world/map data. `organization_rules.gd` overlays definitions onto the 19 existing scenario organizations at reset. All existing membership arrays stay byte-for-byte equivalent. Every imported membership initially remains full; associates, observers, partners and suspension are supported by status maps but no new status assignments or member lists are silently imported. Twenty-five additional definitions are visible only in the directory, with empty membership and no simulation presence. The document explicitly requires membership review before import; see DATA_SOURCES.md.

The toolbar's Organizations section uses `organizations_panel.gd`: country-specific cards, a back action, Members and Features tabs, flags/statuses on member rows, planned disabled actions, and map access. It inherits the current navy/gold theme. The existing unified country inspector is reused; map access updates the same organization detail instead of clearing its owner. The section uses the existing outer vertical scroll and releases children when switching views. No background or frame-processing node was introduced.

`trade_integration_level` returns the highest regional level from full memberships, respecting per-country opt-outs, and gives no live economy bonuses. Saved statuses/opt-outs are validated before assignment; full security memberships are exclusive, partnerships are not. Save schema 22 requires a fresh game, with no migration. PP, opinions, research, laws, approval, trade and military behavior remain unchanged: the design specifies no agreed bonus values or playable consent workflow. Do not debit PP for disabled actions or claim future effects as active.

HQ records resolve once against PlaceCatalog after startup; city matching includes the existing Washington, D.C. spelling. Runtime records link to city/state/province IDs, with an explicit country fallback. In Organizations mode, the city overlay projects at most one HQ, even from globe zoom, instead of scanning the national-city index. Countries without a fixed HQ show no marker. The cached city-view key includes map mode and organization, so changing either invalidates markers while a stationary view does no extra work. Existing map meshes, textures, ownership and geography are unchanged.

OAU/AU and CST/CSTO use dated display names, preserving stable IDs and current membership. These are presentation changes, not event-driven expansions. The remaining founding/succession records are inactive definitions; implementing campaign events is separate work.

Run `tests/organizations_tests.gd`, existing model/political/research UI suites and clean_globe_stability.gd with Godot 4.5.1. Set BUNNYWORLD_QA_DIR to an external directory for optional GL screenshot capture. Screenshots and packaged outputs do not belong in the repository.

## Map style and capital decoration

Application 0.2.1.4 uses the existing 0.2.1.2 geography/display bundle. Shared shader defaults control near/far country tint, ribbon intensity, coastal shelf/foam and terrain detail strength. Border widths remain screen-space; state/province lines are subordinate to national outlines. No additional texture samples, buffers or terrain geometry are introduced by these style changes.

`python tools/clean_obsolete_capitals.py` removes only GeoNames cities500 additions ranked below 10,000 that are neither national nor current state capitals, together with their synthetic State capital clusters. Original mapped settlements and larger added cities remain. It clears stale capital flags, recomputes decorative priorities/weights and refreshes the ordinary JSON bundle checksums. It never changes world/province topology or resident populations. Rank is a decoration filter, not a demographic estimate. Repeat runs are safe; test with `python tests/obsolete_capitals_tests.py`. Historical generators remain historical reproduction tools, not commands to run over current geography.

Labels/city architecture, coastline province lookup and terrain geometry are separate future work.

## Clean globe stabilization

The current application is 0.2.1.8 on clean-globe; geography/display remain 0.2.1.2. Canonical IDs are 6144×3072 with 1,252 states, 13,074 land provinces and 784 seas. Earlier .28/.29 reproduction notes below describe historical geography; do not run those generators over this map.

The clean surface uses one 384×192 sphere, spatial border/river batches and the existing atmosphere. There is no detail patch. DisplayCoverage.initialize(target, false) loads the required coast/tiny-land/sea fields but skips the unused boundary hint/pair/distance textures and local coast packs. Legacy callers retain the default behavior. Three skipped fields are 3072×1536 × (1+4+2) bytes = 33,030,144 bytes (31.5 MiB), excluding driver overhead. The sandbox shares immutable textures between both materials.

Camera transforms/horizon scans are cached; selection visibility changes still trigger culling. View uniforms use distance/mode keys and are invalidated on palette/shader changes. Hover uniforms update only when the hover changes. The 10 Hz stationary redraw policy and independent simulation remain intact. Ocean-neighbor taps are gated to the union of the existing coastal-effect bands, including selected-sea behavior.

The published branch's scenery checksum and generator fingerprints were stale. Prepared borders/chunks were rebuilt from the unchanged PNGs/membership with the checked-in generators; active packs and contracts were republished together. Do not merely rewrite generator fingerprints to bypass rebuilds. Run preparation verification and repository hygiene after pulling.

Validation: Godot 4.5.1 model tests, political_ui_tests.gd, clean_globe_stability.gd; Python tools/restore_repository_assets.py --verify-only; Python tools/build_map.py --check; Python tools/repository_hygiene.py. A GL Compatibility render probe also exercises distant political/physical and close physical views under Mesa llvmpipe. This verifies rendering, not target-laptop speed. The fixed globe mesh remains coarser than the full CPU relief field at extreme zoom; this patch does not change terrain geometry/picking algorithms.

## Shared UI and Research scaffold (0.2.1.6)

`ui_style.gd` is the shared source of panel/button styles and heading/accent colors. Main's existing style helpers delegate to it without changing their output. New windows use `styled_popup.gd`, which inherits the existing briefing frame, the host theme and gold corner accents instead of a native OS title bar. The UI convention is recorded in AGENTS.md for future changes.

Law pickers are nonmodal: outside clicks dismiss without consuming the event, so clicking another law immediately replaces the previous picker. They sit beside the grid, keeping the other law buttons exposed. Floating panels stop pointer/scroll events over their bounds, are included in the globe input guard and are freed with their owner. Escape closes a floating panel before closing its tab; tab toggles/switches also dismiss it. No frame loop was added.

Research uses the existing sidebar tab with institution buttons. Each opens a styled, centered window identifying the institution and containing a genuinely empty tree canvas. No placeholder technology nodes, research effects, timers, funding or save-schema changes. `research_institutions.gd` gives deterministic UI identities: curated names for 13 major countries, otherwise unique capital-based university/research-institute names using `state_capital`. Named lists use 3–6 slots; other countries provisionally get 2/3/4 slots at <5k/5k–20k/≥20k scenario GDP per capita. These are UI scaffolding choices, not a calculated scientific-capacity model. No specialization bonuses yet. Names can be recomputed without duplicates or random changes; research state persistence comes with the later playable system.

Run `tests/research_ui_tests.gd` for actual pointer dispatch between laws and institutions, Escape/close behavior, lifecycle cleanup, all-country identity bounds/determinism and smaller viewport bounds. Run the existing political/model suites for PP and persistence regression coverage.

## Government and political power

GovernmentRules defines six ordered categories, 28 law choices and the default 100 PP cost. The section uses horizontal rows of 56px icon-only buttons, current-option pictograms, identifying tooltips and small nonmodal floating choice panels beside the law grid and clamped to the viewport. The government title above parliament derives from the form, executive and competition choices. The existing country scroll container scrolls the entire Government content; the pinned country heading remains visible. Government is 600×720px, capped to available space. Country panels retain their 370px width.

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
