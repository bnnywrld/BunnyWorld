# BunnyWorld 0.2.1.2 — smaller map renderer inputs

Changed-files update over **0.2.1.1**. The existing renderer and UI are retained.

## Result

- One **8192×4096 province ID PNG**, replacing four 8192×4096 quadrants (formerly 16384×8192 total).
- All **224 countries, 1,259 states, 13,197 provinces and 120 sea regions** remain. No territorial IDs were removed.
- Population remains **6,146,495,066**. Every state population, demographic profile, owner, building inventory and recorded physical area is unchanged. Artificial enlargement affects the visible footprint only.
- The large shared border-pair, border-distance, border-hint and coast textures are also reduced in both dimensions. Small-island coverage is regenerated.
- Terrain colour, elevation and ground-material texture resolutions are retained. Only coastal coverage/displacement is adjusted to the final land outline.

## Small places and inhabited islands

- **Nauru** (673): enlarged from 2 ordinary-downsample pixels to a compact, selectable footprint (at least nine pixels).
- **Akrotiri** (1473): enlarged from 3 ordinary-downsample pixels to a compact, selectable footprint (at least nine pixels).
- **Gibraltar** (1489): enlarged from 0 ordinary-downsample pixels to a compact, selectable footprint (at least nine pixels).
- **Scattered Islands in the Indian Ocean** (1524): enlarged from 3 ordinary-downsample pixels to a compact, selectable footprint (at least nine pixels).
- **Melilla** (1615): enlarged from 1 ordinary-downsample pixels to a compact, selectable footprint (at least nine pixels).

Ordinary 2×2 voting lost two IDs: Gibraltar province 9440 and Somaliland province 12478. Both are retained. 68 valid city, landmark and state-capital locations receive a protected pixel where needed, preventing the loss of inhabited islands even when their province also occupies another island.

Existing coordinate/reference inconsistencies are preserved rather than moving unrelated cities into distant states. Only 6 display anchors needed small adjustments within their original state; no state membership or city/scenery records were removed. The exact changes are recorded in data/map_reduction_audit.json.

## Performance evidence

| Resource | Before | After | Change |
|---|---:|---:|---:|
| Province ID GPU texture payload (RG8) | 256 MiB | 64 MiB | −192 MiB |
| Listed province/border/coast/tiny-island GPU payloads combined | 560 MiB | 140 MiB | **−420 MiB (75%)** |
| CPU province picking images (RGB8) | 384 MiB | 96 MiB | −288 MiB |

The payload figures are exact format/dimension calculations, excluding driver overhead and other game assets. They are **not measurements of total VRAM or FPS**. On this host, a three-run interleaved Pillow RGB PNG-decode benchmark changed from median 1501 ms to 412 ms; it excludes GPU upload, simulation and drawing, and is not a 940MX benchmark.

The expected benefits are lower memory pressure, fewer/lighter ID-map resources, and better texture-cache behaviour. Actual frame pacing and FPS on the target laptop remain to be measured.

## Validation

**91,826 map/data checks**, **54,989 Godot 4.5.1 headless runtime checks**, and **99 government/PP UI checks** passed. These cover retained IDs, tiny-state footprints, land/sea agreement, unchanged simulation/demographics, every province and sea picking anchor, current resource checksums, same-version save/load, map modes and offscreen ownership updates. CPU/GPU relief data agree.

## Apply and compare

1. Close Godot and the game. Pull main, or apply the changed-files ZIP over 0.2.1.1.
2. Run **Prepare_BunnyWorld.bat**. Application, geography and display should all report **0.2.1.2**.
3. Open project.godot with **Godot 4.5.1 Standard**, allow imports to complete, and start a **fresh campaign** (save schema 20).
4. Use the same window size, map mode, graphics quality and zoom as .1.1. Compare continuous rotation and zooming, especially near dense coastlines. Check both political and physical modes.
5. Check Gibraltar, Nauru, Akrotiri, Melilla, Scattered Islands and small Pacific islands. Check Åland, the Turkish straits and your other accepted map edits.
6. Select small provinces, states and sea regions; inspect city/landmark positions and government/PP controls. Save/load within this version.

No Windows EXE is included. The source still uses Godot 4.5.1 Compatibility. Native Windows graphics/FPS were not tested here.

## Editable maps

BunnyWorld_0212_Editing_PNGs.zip contains **provinces.png, states.png and sea_regions.png**, each 8192×4096 with readable, unique colours and embedded colour-to-ID mappings. Keep PNG dimensions, use sampled existing colours, disable antialiasing, and retain the original files for recovery if your editor removes metadata.

## Reproduce

The accepted high-resolution source, accepted sea map, pre-reduction records, hashes and benchmark are under tools/cartography/reduced_0212. From the recorded .1.1 source commit, copy these inputs and run reduce_map_0212.py, refresh_reduced_terrain_0212.py, then build_map.py --godot <Godot 4.5.1>. All active map builders use the current layout through map_dimensions.py. Historical numbered generators are not current-map authorities.
