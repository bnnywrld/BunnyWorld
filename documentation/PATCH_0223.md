# BunnyWorld 0.2.0.23 — smoother map interaction and terrain rendering

Changed-files source patch over the confirmed working 0.2.0.22. Application/display: 0.2.0.23; geography remains 0.2.0.21. No executable is included.

## Changes

- **Lower mesh residency.** Land, province, sea-border and river layers use their existing exact spatial batches without loading a second whole-world copy. Nearby terrain still uses the full 512×256 sphere batches. Beyond distance 4.5 the sphere uses 256×128 cells (65,536 triangles instead of 262,144); borders retain their prepared geometry and live ownership.
- **Cheaper distant physical terrain.** An immutable, mipmapped cache holds filtered tangent normals and snow coverage. Beyond distance 2.4, one cache sample replaces the five elevation/neighbor samples and snow calculations previously used per fragment. A smooth transition starts at distance 2.0. Close terrain continues using the original calculations and detail materials. Lighting is still applied at runtime and changes as the globe rotates; this is not a fixed lit picture.
- **Separate shader programs.** Political/information modes compile without the physical-material shading block. The programs share the cartography code and the same live textures. Mode changes preserve uniforms and do not rebuild geometry or upload the terrain cache. Existing startup warming covers both programs.
- **One hover query per frame.** Mouse-motion events queue their latest position, resolved after the current camera pose. A burst of motion events no longer runs a terrain query for each event. Click selection remains immediate; dragging suppresses hover work.
- **Less decoration-query work.** Conservative geographic buckets reduce city/building visibility candidates. The original visibility tests, marker collision ordering, building limits and landmark selection remain authoritative. Stationary scenery reuses its previous visibility result rather than repeating full scans every quarter-second.

These changes affect presentation only. All countries, states and provinces remain in the same WorldState; visibility never gates the clock or worldwide ownership updates. No geography, demographic, population, relief/picking data or simulation rules changed.

## Measured checks

- 121 full-application checks passed, including off-screen ownership, clock advancement with drawing disabled, accurate picking, shader mode changes and decoration equivalence.
- Renderer texture-plus-buffer counters dropped by **70.05 MiB net** relative to 0.2.0.22 in the minimal production-renderer harness. Removing duplicate buffers saves about 102 MiB; the new mipmapped cache adds 32 MiB. These are engine counters on Linux software rendering, not a measurement of Windows driver allocations.
- Indexed queries selected the same city labels and building clusters as complete scans in six representative views, including the dateline and a polar view. Candidate city records fell from 2,340 to 16–764; scenery candidates from 2,787 to 16–941. Repeated stationary updates performed no further scenery visibility scans.
- Forty queued mouse-motion events produced one hover query using the final position.
- Eight renderer comparisons retained exact close political pixels. The close Alps comparison differed by one channel value of 1/255. Filtered distant physical lighting has small expected differences (largest mean channel difference below 0.30/255). The far sphere changes a small number of silhouette pixels.

Detailed evidence is under validation_0223. Software wall timings varied and are not proof of target-PC FPS. Native Windows/940MX performance still needs testing.

## Install

1. Close Godot and the game.
2. Extract this ZIP into the working 0.2.0.22 project folder, replacing files beside project.godot.
3. Run Prepare_BunnyWorld.bat.
4. Reopen project.godot, press F5, and start a fresh campaign.

## Test order

1. **Political map:** rotate and zoom, move the pointer rapidly, hover and click small states/provinces and sea zones. Check that hover follows the latest position and clicking stays immediate.
2. **Cities:** pan around dense regions at close zoom. Verify that city names, buildings and landmarks remain present. Stop, then resume movement.
3. **Physical map:** compare close Alps/Himalayas with regional and globe views. Distant lighting/snow is now filtered and may look slightly different; close detail and relief remain. Check smooth transitions while zooming and correct light direction as you rotate, including polar views.
4. **Far globe:** zoom out fully and back in. Check the silhouette, country borders, labels and selections around the geometry transition.
5. **Modes/settings:** switch repeatedly between Political, Physical, Population and Relations; switch Light/Balanced. Confirm colors, selections and terrain textures stay correct.
6. **Off-screen ownership:** while viewing the Americas, enter `owner 1813 JAP` in ~, then rotate to North Sumatra and verify its current owner/color. Restore with `owner 1813 IND`. Run the clock while stationary and moving; simulation must continue independently of rendering.

The previous diagnostic commands remain: `perf status`, `perf start [frames]`, `perf stop`, `perf continuous`, `perf auto`. Reports save in the game's performance folder beside saves. Close the console after starting a capture. These commands do not alter simulation speed, graphics quality or the frame limit. Captures from a release export are preferable for native performance conclusions; F5 is identified as a debug build.

## Development notes

planet.gdshader and planet_physical.gdshader now wrap planet_surface.gdshaderinc; keep shared cartography in one place. Changes to physical shading should remain outside the political program through PHYSICAL_MAP preprocessing.

tools/build_far_terrain.py prepares the cache from relief_data.png only, evaluating native-resolution normals/snow before filtering. It contains no owner, state or light direction. tools/build_map.py checks its source/output hashes with the other resources. Prepared files are included, so users need no extra image-processing packages for preparation checks. If relief changes, regenerate the cache and contracts.

The new point index is a decoration broad phase, not a simulation partition. Any future dynamic relocation of cities/scenery must update that decoration index alongside its existing prepared positions.
