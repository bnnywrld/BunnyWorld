# Development — BunnyWorld 0.1.11

Godot 4.5.1 stable; GDScript; GL Compatibility; Windows x64. Prepared assets ship offline. Source is separate from the download/extract/run Windows release.

## Geometry and camera

NOAA ETOPO 2022 ice-surface elevation is sampled from the 60s global grid every third point (3 arc-min), resampled to 8192×4096 and quantized to integer meters. The prepared `etopo_021.npz` is an immutable geographic rebuild input, avoiding a network dependency. The accepted 0.1.10 land/water mask clips displacement; inland/coastal feathering spans 2.5 elevation pixels. Land lift .00035 sphere units; elevation multiplier 4 / 6,371,000; 16-bit linear radial displacement uses scale .008. The source is finite resolution and does not resolve precise summits or surveyed urban geometry.

`relief_data.png` packs displacement low/high bytes in RG, real altitude in B and land feather in A. It is lossless, without mipmaps, alpha-border fixing, premultiplication, sRGB or VRAM compression. The CPU `relief_data.bin` is the same little-endian 16-bit field (64 MiB). Both raw channel identity and relief-aware oblique ray intersections are tested.

The distant globe has a 512×256 sphere mesh with shader displacement. One 128×96 local geographic patch (12,513 vertices) provides close geometry; CPU vertices contain actual radial heights and shader UV2 flags distinguish the local patch from the distant mesh. The distant fragment pass is clipped inside the patch; small overlap/bias avoids a visible gap. The patch updates at most four times a second and only rebuilds after meaningful span/center changes. It hides beyond distance 1.4 and in the menu; texture streaming remains bounded to 24 slots/two decode jobs.

Borders sample the same displacement and their projected tangent follows the height derivative. City markers project raised points. Picking intersects the relief field instead of the unit sphere, with bounded first-hit marching and a grazing-ray bracket. Map IDs are still categorical and independent of visible antialiasing.

Camera tilt derives from saved zoom: smoothstep below distance 1.18 to a 38° maximum at 1.015. Its anchor is the raised front surface; clearance is at least .015 sphere units. Wide views retain overhead orientation. Load, focus, wheel input and tests update the same camera pose. No extra saved camera schema is needed.

## Material and atmosphere

One refined 2×2 woodland/desert/grassland/rock atlas was made with the built-in Image Generation tool. Master, runtime asset and exact prompt/provenance are included. The new atlas adds microdetail over the existing geographic terrain; it does not replace the 2,048 terrain tiles. Altitude/slope guide rock and snow; urban material receives sharper block/street detail. Surface shader uses 16 distinct samplers, within the GL 3.3 fragment minimum. Raw height is one shared vertex/fragment sampler; do not add another full-field normal sampler without revisiting this limit.

Physical shading uses geographic height gradients and world-space light direction. A radius-1.028 shell uses directional scattering with a fade at the outer silhouette; physical surface haze increases toward grazing view angles. These are lightweight visual approximations, not full atmospheric simulation or cast-shadow terrain.

## Conservative remote merges

`merge_remote_021.py` uses immutable `world_seed_020.json`, `province_seed_020.json`, and the existing geographic/province atlases. City-containing or built provinces are protected. Eligible cells use nearest-city spherical distance, coast/lake buffers and state population density, with explicit conservative Greenland/Sahara/far northern/Australian/Mongolian geographic gates. Egypt/Sudan's broad Nile corridor is protected. These proxies cannot establish that every eligible cell is uninhabited.

Adjacent eligible cells merge only within their existing state. Existing surviving global IDs and focus pixels remain; local ordering/atlas/lookup and shared-edge adjacency are rebuilt. 5,076 cells are removed (45,107→40,031). All country/state control, demographic/building totals and territorial rights are unchanged. Populated city-cell areas and the Chishima/Karafuto split remain exact relative to 0.1.10.

## Rebuild and verification

```
python tools/merge_remote_021.py
python tools/build_relief_021.py
python tools/build_boundaries_021.py
godot --headless --path . --script tools/compile_boundaries.gd
godot --headless --path . --editor --import
python tests/import_tests.py
godot --headless --path . --script tests/model_tests.gd
godot --headless --path . --script tests/relations_tests.gd
godot --headless --path . --script tests/territorial_rights_tests.gd
godot --headless --path . --script tests/relief_tests.gd
godot --headless --path . --script tests/terrain_cache_tests.gd
godot --path . -- --smoke-test
```

Python dependencies: numpy, scipy, Pillow, shapely, scikit-image. Optional raw refresh passes NOAA ERDDAP NetCDF to build_relief_021.py. Normal rebuilding/export uses bundled prepared data. The original source URL/DOI and processing metadata are in data/relief.json. Exports must explicitly include assets/relief_data.bin. Historical builders/tests are provenance, not current atlas validation.

Capture CLI supports --capture-point=longitude,latitude and --capture-state=ID alongside country/map/zoom/province flags. Final captures log camera tilt, local-patch visibility and vertex count. Review exact exported-PCK rendering and reject script/shader/resource errors. Native Windows execution remains the user's test.

Save schema stays 7; scenario identity is bunny_world_2000_0_1_11, so previous scenario saves are rejected atomically. No migration is included. Same-scenario saves and explicit console edits retain their ordinary persistence.

## 0.1.12 urban foundations

`tools/prepare_population_022.py RASTER.tif` aggregates the official GHSL 2000 resident grid onto the unchanged 0.1.11 province atlas. Prepared `population_022.npz` and source metadata are included for offline rebuilding. `tools/build_urban_022.py` reconciles shares within countries, rebuilds state totals and urban groups, assigns area names from `urban_names_022.json`, and prepares deterministic tiny scenery layouts. Source scripts require numpy/scipy/rasterio; the packaged game requires none of these.

`WorldState.population_allocation` uses whole-number largest-remainder allocation, keeping state totals exact after debug edits. It caches only by state total; ownership changes move residents with state territory. Population growth is disabled. `urban_group_population` sums each member province once across state boundaries. Shared rural pools are never duplicated into province records.

`UrbanScenery` streams visible city batches, caps active clusters/buildings, disables shadow casting, and bakes landmark primitives into one mesh each. Buildings and landmarks share the camera tilt onset, with alpha fading over a short zoom range. The distant urban texture remains. All instance feet use the same relief field as terrain/picking.

Validation: `tests/urban_data_tests.py`, `tests/urban_population_tests.gd`, existing model/relations/rights/cache tests and built-in `--smoke-test`. Export with `tools/build_windows.py`. Growth integration and demographic categories belong to 0.2.

## Updated 0.1.12 map/interface refinements

`tools/refine_microstate_022r2.py` restores oversized Vatican atlas cells to neighboring Italian provinces, retains one coarse identity pixel, and writes a small vector override shared by GPU fill, boundary ribbons and CPU picking. `microstate.gdshaderinc` uses bounds checks and a 60-vertex reference polygon without adding a sampler. The actual game territory outside the polygon resolves to the Italian host. Keep the official stated area distinct from the approximate vector geometry.

Rebuild order: refine_microstate_022r2.py → prepare_population_022.py (official raster input, or retain bundled prepared aggregates) → build_urban_022.py → refine_shores_022r2.py → build_boundaries_021.py → Godot tools/compile_boundaries.gd → editor import → Windows export. New atlases are province_atlas_022r2.npz/grouped_atlas_022r2.npz; older inputs remain for provenance. Shore lift is 79.6375 m, with a smoothstep transition inland and original 4× mountain relief.

PlaceCatalog builds a bounded searchable catalog once and normalizes accented Latin names. Main handles modal pause/resume, navigation, current owner selection and persistent preferences. `tests/place_catalog_tests.gd`, `tests/refinement_022r2_tests.py`, existing accounting tests and expanded UI smoke cover the new behavior. The user explicitly does not want old-save compatibility/migration during this stage; use a new scenario identity for a changed starting world.
