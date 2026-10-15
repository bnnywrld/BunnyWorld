# BunnyWorld 0.2.0.10 — geography and UI input corrections

Base: GitHub main 0.2.0.9, commit cb61e7c3db749ca079ee1aa077395143af215bdb.
This is a changed-files source patch. Start a fresh campaign.

## Changes

- Central Kalimantan, South Kalimantan, Western Central Kalimantan and Eastern Central Kalimantan form Central–South Kalimantan. East and West Kalimantan remain separate.
- Courantyne Headwaters joins Mahaica-Berbice. The retained union is named Mahaica-Berbice.
- The southern West Polynesia arm and its narrow eastern remnant join Tasman Sea. Tasman and West Polynesia are each one connected water region across the date line. A four-pixel Tasman registration shard west of Tasmania joins the neighbouring Southern Indian Ocean.
- Redraw 215 existing provinces in the 15 states where 0.2.0.9 added density: Ghazni/Baghlan, seven eastern Ukrainian regions and seven Syrian regions. Local equal-area grids, terrain slope, mapped rivers, settlement anchors and smooth broad-scale variation replace near-uniform growth. Province IDs/counts and state/country boundaries are preserved. These are gameplay provinces, not surveyed administrative borders.
- Rebuild the global inward border shading from current ownership. This removes the stale pre-transfer shading around Sweden/Åland and refreshes other earlier ownership corrections. Sweden and Finland keep exactly their accepted 0.2.0.9 land footprints. Rebuild all land, sea and province border meshes.
- Country, diplomacy and territory panels stop wheel propagation. A camera input guard also rejects panel-covered map events and stops a drag entering UI. Panel contents still scroll and exposed map areas still zoom.
- Retain 223 countries, 13,594 provinces and total population 6,144,737,528. The two requested unions reduce states from 1,364 to 1,360. Population/building accounts, city/scenery links, province adjacency and protected-territory references are reconciled.

## Map review

Reviewed six globe projections and 18 regional views covering the populated continents, polar areas and the requested locations. A connected-component scan flagged 122 states with multiple substantial pieces; these flags include legitimate archipelagos, lake/river separations, date-line splits and protected territories, and were not automatically merged. Complete atlas checks find no uncovered land, invalid province-to-state pixels, missing IDs or substantial disconnected province pieces on the same state landmass. Both corrected sea regions have a single wrapped component. The additional confirmed artifact repaired here is the four-pixel Tasman shard.

A visual review is not a claim that every world border is geographically exact. Earlier coarse historical Russian lines remain approximate.

## Debugger report

The reported 32 entries could not be reproduced from this baseline in headless or graphical Linux testing with Godot 4.5.1. They are **not claimed fixed**. The graphical test uses Mesa software OpenGL, not the user's Windows/NVIDIA drivers. If entries remain, drag the Godot executable onto Capture_Debug_Log.bat, reproduce the issue, close the game and attach Debug_Log.txt. If the entries only occur when running from the editor, also copy the first expanded entry from its Debugger panel.

## Install and test order

1. Close Godot. Extract the ZIP directly into the existing 0.2.0.9 project folder, where project.godot is located. Replace included files.
2. Run Prepare_BunnyWorld.bat. It must confirm that the geography bundle is 0.2.0.10.
3. Open project.godot with Godot 4.5.1, allow imports to finish, and start a fresh campaign. The project name/version must show 0.2.0.10. This ZIP contains no replacement Windows EXE.
4. Open your country panel, another country's diplomacy panel, and a State/province drawer. Scroll over text, charts and empty panel areas. Contents should scroll when applicable and globe distance must stay fixed. Move to the open map and confirm zoom works.
5. Inspect Kalimantan: one Central–South Kalimantan state replaces the four requested states. Inspect Guyana: Courantyne Headwaters is part of Mahaica-Berbice.
6. Inspect West Polynesia/Tasman around and east of New Zealand. The southern arm is gone and the southeastern Tasman area is connected.
7. Select Sweden, then Finland; inspect both the normal political shading and selection outlines near Stockholm/Åland. Also inspect the physical map's inward border tint.
8. At close zoom compare province shapes in Ghazni, eastern Ukraine and Syria. Check province picking, cities and drawer population totals.
9. Check the Debugger panel after a fresh launch. If entries remain, capture the log as described above.

## Maintainer regeneration

The original 0.2.0.9 snapshot is retained locally in .geography_0210_baseline, excluded from delivery. On a clean 0.2.0.9 source checkout, tools/fix_geography_0210.py creates that snapshot before editing. It requires the established Python geography dependencies and restored source assets.

Run tools/fix_geography_0210.py; tools/build_boundaries_021.py; Godot with --headless --path . --script tools/compile_boundaries.gd; then tools/package_repository_geography.py and tools/restore_repository_assets.py --verify-only. Set the project version to 0.2.0.10 before bundle verification. Run Godot's editor import before integration testing. The regression tests need the retained baseline snapshot; render previews with tools/preview_geography_0210.py.
