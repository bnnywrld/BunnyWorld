# Developing BunnyWorld 0.2.0.5

Godot 4.5.1 stable, GL Compatibility. UI-only patch on complete 0.2.0.4. Application version 0.2.0.5; world scenario bunny_world_2000_0_2_0_3 and save schema 10 remain unchanged. Start fresh across releases. No save migration is authorized.

scripts/main.gd builds a full-window viewport with independent top-edge Control/PanelContainer boxes. _configure_overlay_layout reparents the existing controls out of their former full-width layout; _layout_overlay anchors compact groups to the current canvas. project.godot uses canvas_items with expand aspect handling. Use Window.size in resize tests; changing the low-level display size alone does not update the managed Window viewport in this test setup.

Territory content lives in a clipped 300-pixel viewport-adjacent control. Its panel and attached handle tween in opposite directions for own/foreign parents. The clip occupies the lower half of the window; the normal country panel stays at its outside edge. Collapse state and metric choices persist during inspection; parent close removes the entire drawer/handle.

scripts/compact_demographics.gd provides a single inline chart and four selectors, reusing the existing demography.gd/Pie and their exact population allocations/denominators. Country and State entries are computed on inspection and chart data reused on selector changes. No per-frame demographic aggregation. Legacy detailed demographic dialog stays available internally for diagnostics; normal country/territory UI uses inline charts.

scripts/foundation_ui.gd builds compact stat cells and disabled section navigation. Four additional UI icons are small authored SVGs. No changes to world_state, demographics data, terrain shaders, resident material library, fixed grid or scenery manager. Historical geographic regeneration remains under documentation/versions/0_2_0_3.

Current layout/interaction regression is tests/ui_0205_tests.gd. Source and the actual exported embedded pack must pass it plus full UI smoke. Core model/foundation/resource suites remain relevant. Build using tools/build_windows.py with the clean official Windows 4.5.1 release template and --embed-pck. Validate pack PE/footer, digests, embedded version and exact runtime scene. Exclude caches, temporary export files and historical validation artifacts from deliverables. Linux pack loading/rendering is not native Windows testing.
