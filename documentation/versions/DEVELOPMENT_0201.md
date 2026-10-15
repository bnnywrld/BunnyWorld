# Developing BunnyWorld 0.2.0.1

Use Godot 4.5.1 and the GL Compatibility renderer. Open project.godot; all prepared runtime data is bundled. Windows export uses the Windows x64 release template. tools/build_windows.py accepts --godot, --template and --output. Export presets exclude source-only generators/tests/verification and raw material masters; include the prepared BWM material bytes and relief binary.

Use a clean official export template, never an executable from a previous game release. Exported executables can carry an embedded PCK that takes priority over an external pack. The helper rejects templates containing embedded data, including the PE pack section and PCK footer. The current preset embeds this project's pack into BunnyWorld_0_2_0_1.exe; --embed-pck also enables it explicitly. The helper verifies the embedded footer/directory/Windows PE section, then loads the actual executable as the game pack and runs the exported-version test. Its source/hash/CRC and release checks are recorded under verification_0201. The clean template is templates/windows_release_x86_64.exe from the official Godot 4.5.1 export archive.

Current source: scenario bunny_world_2000_0_2_0_1; starting-world schema 8, save schema 9. Same-version save/load remains available. Do not add old-save migrations unless the user explicitly requests them.

## Terrain build

1. tools/build_resident_terrain_0201.py uses numpy, scipy and Pillow. The official year-2000 ESA CCI WMS samples, palette and requests are bundled under tools/cartography. The original material art is assets/materials/resident_master_0201.png. This prepares an eight-family classification/blend mask, regional colour and periodic material images.
2. Import assets with Godot, then run tools/compile_materials_0201.gd. It writes eight S3TC/DXT1-compressed 2048-square images with complete mipmaps into terrain_materials.bwm. Runtime creates one immutable texture array from these bytes. Total compressed library: 22,369,860 bytes. There is no JPEG decode, mipmap generation, tile replacement or texture upload during camera travel.
3. main.gd creates one 192 x 144 close-up grid; planet.gdshader applies its position and shared relief on the GPU. CPU ray picking uses relief_surface.gd. The four lossless province-ID textures and political lookup maps remain separate from natural terrain.

## Waterways

Run tools/build_waterways_0201.py, tools/build_water_passage_include_0201.py, then tools/compile_waterways_0201.gd. Natural Earth named river ranks 0–3 supply river courses. Canals and straits use approximate centre lines with explicit reciprocal sea-zone adjacency. The generated shader include and CPU classifier both read the same path coordinates and display widths. This supplies subpixel water fill/picking while retaining the accepted province atlas.

Update sea border contours from sea_ids.png with build_boundaries_021.py's contours/mesh helpers, then run tools/compile_boundaries.gd. Land and province border data remain unchanged. Inland lakes remain excluded from selectable sea regions; the Black Sea and Marmara are restored as linked sea zones.

## Scenery and UI

expand_scenery_0201.py runs once on original 0.2.0 data, not repeatedly on already expanded skylines. It adds representative buildings without changing population allocation, group or province IDs. urban_scenery.gd prepares all meshes at startup, retains them and only shows/hides nearby nodes during travel. Whole-group caps are 200; nearby limits are 1,024 buildings / 64 clusters. SIZE_MULTIPLIER is exactly 3.0 relative to the previous release. Labels show cities, not landmarks. The close-range fade and scenery toggle remain.

Demographics displays national or State data in four simultaneous cards. Keep denominators visible and provenance in data/documentation. Same-version saves retain the 0.2.0 finances/profiles/tension foundation. Future growth and politics remain covered by the bundled roadmap.

## Validation

Run model, relations, territorial rights, urban population, place catalog, relief and foundation tests. Python checks cover rendering fixtures, geometry, population/scenery placement and waterways. With a real Compatibility display, run terrain_cache_tests.gd for travel/revisit resource stability and narrow-waterway picking; foundation_ui_tests.gd for chart/control behaviour; main.gd --smoke-test for full scene checks. Capture flags remain available for reproducible views. tests/camera_benchmark.gd measures the isolated camera/terrain update, not overall FPS.

Export the final Windows executable and repeat the scene/render checks on its embedded pack using --main-pack BunnyWorld_0_2_0_1.exe. Native Windows execution and hardware performance require user testing. The historical generator files for older streamed tiles are retained as project history and are not current build steps.

Run tests/export_pack_version_tests.gd against the exported PCK using --headless --main-pack and the script's absolute path. It verifies the loaded project version and required new terrain/waterways/foundation resources. This complements the Windows launcher structure check; testing a PCK alone cannot detect a launcher that loads an older embedded game.
