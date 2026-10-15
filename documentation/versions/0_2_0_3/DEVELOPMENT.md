# Developing BunnyWorld 0.2.0.3

Godot 4.5.1 stable, GL Compatibility. Scenario bunny_world_2000_0_2_0_3, starting-world schema 9, save schema 10. Fresh campaigns only across versions; same-version save/load remains supported. Prepared runtime resources are included.

## Regeneration

Python dependencies: numpy, scipy, Pillow, rasterio, shapely and scikit-image. Run from this project directory. Large raw inputs are external, but prepared intermediates and minimal immutable 0.2.0.2 baseline inputs are bundled. Do not use the original 0.1 attachments as the baseline.

0. `python tools/build_hover_flags_0203.py` prepares a compact 4,526-variant tooltip atlas. Run it after reimporting flags. Hover uses this atlas; normal large flag controls keep the original pages.
1. `python tools/register_reference_0203.py /path/to/bunnyversion.zip` decodes the supplied RGB bitmap/definitions/State membership and matches original baseline settlement names to victory-point provinces. Source centroids and real settlement coordinates drive a smooth local thin-plate fit; ambiguous name matches are rejected. Narrow controllers have explicit footprint anchors. registration_0203.json records anchors. reference_registered_0203.npz is already prepared.
2. `python tools/build_geography_0203.py` uses tools/cartography/baseline_0202 by default. An explicit path to the accepted complete 0.2.0.2 project can also be supplied. It jointly repairs affected State groups, fixes island identities, preserves an Åland water route through downsampling, merges Quebec accounts, consolidates eligible sparse cells, splits significant same-land-mass fragments, and rebuilds provinces, atlases, lookup, adjacency, focus points and city links. NPZ/PNG output uses buffered atomic writes. The source bitmap is never stretched into individual State rectangles or seeded with missing one-pixel labels.
3. Run `python tools/prepare_population_022.py /path/to/GHS_POP_E2000_GLOBE_R2023A_4326_30ss_V1_0.tif`, then `python tools/build_urban_022.py`, then `python tools/layout_cities_0202.py`. Historical filenames remain, but these builders implement the current accounting/layout. All province estimates sum exactly to their State. City groups are aggregates. The street builder checks displayed footprint radii, monument grounds, land/controller/province containment and river buffers. Do not run the historical scenery expansion tool.
4. Run `python tools/build_surface_0202.py --relief-only`, then `python tools/finish_surface_0203.py`. The first regenerates the uncarved shared height field from ETOPO/current land; the second prepares city ground, finite border bands, local coastal sea IDs and trial channels. Always run the first before the second to avoid accumulating channel depression. Existing compressed material libraries are unchanged from 0.2.0.2. All coordinate variation is in the shader; no new texture library upload is triggered by movement.
5. Run `python tools/build_waterways_0201.py` and `python tools/build_boundaries_021.py`. Their historical names remain active. Import using Godot `--headless --path . --editor --import`. Compile waterways with `--headless --path . --script tools/compile_waterways_0201.gd`; compile each boundary kind separately with `--headless --path . --script tools/compile_boundaries.gd -- land` (then sea, then province). Never import while prepared assets are being written.

The full historical material-source rebuild still requires the six listed Poly Haven 4K photographs and bundled forest master. Its recipe is documented in documentation/versions/0_2_0_2/DEVELOPMENT.md. It is unnecessary for this patch or for opening the prepared project.

## Runtime invariants

One immutable eight-layer material array, one 27,985-vertex terrain grid, startup-prepared city meshes. Camera changes uniforms and cached visibility only. No geographical JPEG decoding, camera-triggered material uploads, terrain-grid rebuilds or city regeneration. Deterministic material variation stays world-anchored. Shader texture gradients are computed before conditional sampling.

Relief radial scale .016 and exaggeration 8 remain shared by shaders and relief_surface.gd. Trial river channels modify the same prepared CPU/GPU field. Province selection reads lossless IDs independently of physical shore filtering. Suez/Panama/Bosporus/Dardanelles retain explicit fills, picking and reciprocal links; inland lakes remain excluded.

Every province has a stored starting estimate; world_state.gd proportionally reconciles cached allocations after a same-version State population edit. States run demographics. No migrations or demographic/building growth.

## Verification and delivery

Current tests: patch_0203_tests.py, waterways_0201_tests.py, model/relations/rights/urban_population/place_catalog/relief/foundation/resource-load GDScript tests, full UI smoke, map_0203_ui_tests.gd, foundation_ui_tests.gd, terrain_cache_tests.gd and travel_performance_0203.gd. Historical version-locked geography tests are reference history. Inspect country/province maps and physical views, particularly corrected islands, rivers and textures.

Build from a verified clean official Windows release template using tools/build_windows.py --embed-pck. Never reuse an already exported game EXE as the template. Verify PE pack/footer, directory file digests, exact embedded runtime data/version and full scene from the actual EXE. Linux loading of an embedded Windows pack is not native Windows execution. Package unique EXE/folder/ZIP names, prepared source, notes, validation and checksums. Confirm final saved bytes against the tested artifacts.

Performance is a standing priority: push back on expensive quality requests and explain efficient alternatives. Longer initial loading is acceptable. Measure travel frame times/resource reuse and memory instead of inferring safety from download size alone.
