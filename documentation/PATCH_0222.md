# BunnyWorld 0.2.0.22 — rendering performance

Changed-files source patch over 0.2.0.21 (GitHub base ca86fe36fd39ea7122c9836933fed091fc99c456). Application/display version 0.2.0.22; geography remains 0.2.0.21. No executable is included.

## Changes

- Reuse one accurate terrain intersection for region, province and sea picking at the same mouse position and camera pose. Moving the pointer, camera, globe or changing viewport/projection invalidates it. Ownership is read live, never cached with the ray.
- Replace the GPU's RGB sea IDs with an exact R8 sea mask at the same 8192×4096 resolution: 96 MiB becomes 32 MiB of nominal texture payload. CPU selection retains the original sea IDs. All 33,554,432 mask pixels match the previous shader predicate.
- Skip unused biome classification and urban-density sampling in distant physical views. Retain the current terrain colors, relief lighting, snow, borders and nearby material detail. Default rendering resolution is unchanged.
- Render the map at full application rate while camera, hover, selection or other tracked visuals change, then use a maximum 10 Hz redraw heartbeat while stationary. A short settling period lets labels/scenery finish updating. UI processing and the world simulation continue every application frame. Palette and membership changes explicitly wake the renderer; unknown future scene changes also appear on the heartbeat.
- Apply Light/Balanced/High terrain quality immediately from the settings menu. Light uses the existing 2048 material array; Balanced/High use 4096. Switching Balanced/High changes MSAA without uploading the same terrain array again. Explicit texture-quality changes can briefly pause while loading; camera travel does not load textures.
- Add adapter identification and optional bounded timing reports through the console.

No state, province, ownership, population, demographic or simulation rules changed. A hidden hemisphere is still part of the same WorldState. Future controller/ownership systems must update world data and notify the presentation; viewport redraw decisions must never gate simulation work.

## Install

1. Close Godot and the game.
2. Extract this ZIP into the existing 0.2.0.21 project folder, replacing files beside project.godot.
3. Run Prepare_BunnyWorld.bat.
4. Open project.godot, press F5, and start a fresh campaign.

## Test order

1. Political map: rotate, zoom, hover, select states/provinces and sea zones. Check mountains, tiny islands and coasts for selection accuracy.
2. Leave the map stationary, then move it again. Check that camera movement, hover and selection respond immediately. Border glow continues at a slower refresh while idle.
3. Physical map: compare close mountains and cities, medium zoom and the whole globe. Existing relief and snow should remain visible without a transition pop.
4. Settings: switch to Light and back to Balanced. Texture quality now changes without restarting; camera travel should not cause additional texture loading.
5. Ownership: while viewing the Americas, open ~ and enter `owner 1813 JAP`. Rotate to North Sumatra: its current owner/color should be Japan. Restore it with `owner 1813 IND`. This tests a real off-screen state transfer; province controllers/peace deals are future systems.
6. Run the clock with the camera stationary and rotate around the world. Clock/world data must continue changing independently of rendering. The automated test also advances the clock while map draws are disabled.

## Optional performance report on your PC

Open ~ and enter `perf status` to see the adapter and whether this is a release build. If the adapter is Intel HD 620, select the NVIDIA GPU for the game/Godot in Windows graphics settings before comparing results.

Use `perf start` (600 frames), close the console, and test one fixed view/motion. The report saves automatically in the game's `performance` folder, beside the existing saves folder. The completion message gives its full path. `perf start 1800` records longer; `perf stop` saves early. Captures never change the frame limit, graphics settings, pause state or game speed. Close the console to resume a previously running clock.

To compare idle redraw behavior within this version, use `perf continuous`, close the console and record a stationary view. Then use `perf auto` and record the same view/settings again. `perf auto` restores the normal behavior; the diagnostic override is not saved between launches. These commands only control drawing.

Reports include adapter/build information, frame pacing, application process time, settings/mode/viewport, paused/hour state, map redraw count and engine memory counters. Wall intervals include the frame limit/vsync and are not GPU timings. Native release captures are preferable for performance conclusions; F5 captures are identified as debug builds.

## Verification limits

Automated source/data, graphical regression, ownership/picking and simulation-separation checks are included under validation_0222. Linux uses llvmpipe software rendering. Its wall timings varied and do not establish an FPS improvement or regression on the 940MX. The demonstrated savings are the exact sea-texture payload reduction, reused picking intersections, skipped unused shader work and lower idle draw requests. Native Windows performance remains for testing.
