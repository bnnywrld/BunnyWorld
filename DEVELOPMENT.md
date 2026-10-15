# Developing BunnyWorld 0.2.0.6

Godot 4.5.1 stable, GL Compatibility. Application 0.2.0.6; scenario `bunny_world_2000_0_2_0_6`; same-version save schema remains 10. Fresh campaigns only. No save migration is authorized.

The complete 0.2.0.5 source/resources were the baseline. Terrain, resident materials, fixed surface grid, camera and scenery architecture are retained. Existing scenery positions are retained; only geography links change. The only rendering code fix outside map resources guards pie charts against zero-radius/full-circle/tiny degenerate polygons.

## Geographic regeneration

Restore repository assets first. Python dependencies: numpy, Pillow, scipy, rasterio, shapely, pyproj, scikit-image; matplotlib for previews. Old masks/bookkeeping are in tools/cartography/baseline_0205. Raw geographic subdivisions, elevation, rivers and classification inputs are bundled through repository restoration. No MD province bitmap is used.

Run in this order:

1. `python tools/build_geography_0206.py states`
2. `python tools/coarsen_states_0206.py`
3. `python tools/build_geography_0206.py provinces`
4. `python tools/repair_province_fragments_0206.py`
5. `python tools/link_geography_0206.py`
6. `python tools/build_boundaries_021.py`
7. `godot --headless --path . --script tools/compile_boundaries.gd`
8. `godot --headless --path . --editor --import`

Province generation uses a local Lambert azimuthal equal-area projection for each State, kilometre distances, administrative/river barriers, relief and separated settlement seeds. The 16384×8192 latitude/longitude atlas is the final storage format. Connectivity repair operates within each State/landmass; separate islands may legitimately share a province.

Country control is copied from the accepted baseline. Administrative intersections are grouped within each controller. Small source-border differences are assigned to neighboring geographic units of the same controller. No per-State rectangle fitting or MD geometry warping remains. Contemporary administrative divisions supply geographic shapes, not a claim of exact January-2000 administrative organization.

Minimal existing population/building totals are transferred to keep model/UI contracts valid. Local demographic accuracy is deferred.

## Validation and export

Run geography_0206_tests.py, model_tests.gd, foundation_tests.gd, territorial_rights_tests.gd, resource_load_tests.gd, ui_0206_tests.gd and geography_0206_ui_tests.gd. BUNNY_VALIDATION_DIR controls integration report output. The 58-check UI regression skips screenshots on the headless display server while retaining layout/control assertions.

preview_geography_0206.py renders the exact categorical atlas in regional and orthographic views. These are offline map diagnostics, not native Windows screenshots.

Export using tools/build_windows.py, the clean official Godot 4.5.1 Windows x64 release template and --embed-pck. Validate PE/footer/directory and embedded project identity; rerun integration tests against the actual exported executable using the matching Linux runtime. Native Windows rendering and hardware performance remain user testing.
