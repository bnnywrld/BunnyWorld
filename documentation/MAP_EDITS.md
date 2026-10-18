# BunnyWorld 0.2.1.1 — approved map edits

Changed-files update over 0.2.1. Source resolution remains 16384×8192 for land, 8192×4096 for sea; downscaling is deferred.

## Result

224 countries, 1259 states, 13197 land provinces, 120 seas. Total population: 6,146,495,066.

Priority: sea map (including land/water changes), then states, then province shapes. Sea edits are exact at their native resolution; each changed coast pixel controls its corresponding 2×2 land pixels. Fine existing coast pixels outside those edits remain unchanged. Province IDs retain their parent state, except when that state is merged. Empty areas and fitting fragments are absorbed into neighbouring provinces within the final state.

## State removals

- North Borneo (657) → Sabah / Labuan (651): all 1,244,443 residents and their demographic counts transferred; buildings and base building slots combined.
- Nugal (1764) → Somaliland (1752): all 381 residents and their demographic counts transferred; buildings and base building slots combined.

Retained-state partial border transfers use source land area as a population estimate. Coastal water removal does not delete residents. Religion, education, age groups and workforce counts are conserved globally. Provinces still have no population.

## Geography and references

Sea-grid coastline edits: 44 pixels become land; 878 become water. Province IDs fully removed after fitting: 1. City references updated: 13.

All existing city and scenery records are retained. The display anchors/scenery for Istanbul, San Andrés, Mariehamn and Sonsorol Village were moved to the nearest surviving land within their assigned province because the sea edit submerged their old pixels. Other city coordinates remain unchanged. Capitals, province/state/country membership, neighbours, lookup textures, borders, coast fields, selection fields, terrain displacement and CPU picking data are updated together. CPU and GPU relief use identical values. Current restore packs replace obsolete packs.

## Validation

88,411 data checks and 41,790 Godot headless runtime checks passed. Native Windows visuals and performance need the user test. No performance gain is claimed for this geography-only patch.

## Apply and test

1. Close the game and Godot. Pull main, or extract the changed-files patch into the 0.2.1 project folder.
2. Run Prepare_BunnyWorld.bat. Application, geography and display must report 0.2.1.1.
3. Open project.godot in Godot 4.5.1 Standard and start a fresh campaign.
4. Check the edited Baltic/Åland, Crimea and Turkish coastline: physical/political fill, province picking and sea highlights should agree.
5. Check Sabah/Labuan and Somaliland: removed states are absent and recipient population includes their residents.
6. Inspect Amur/Okhotsk, Kashmir, your province edits, and the changed sea regions. Rotate to the opposite hemisphere and back.
7. Check Government/property costs and +1 daily PP remain functional; save/load within this version.

A Windows EXE is not included. The next separate task can test smaller ID-map resolution.

## Reproduce

From the recorded 0.2.1 commit, restore assets and capture pre-edit runtime demographics. The decoded original/edited PNG IDs and baseline records are under tools/cartography/edits_0211. Run apply_edits_0211.py once, refresh_coast_0211.py, then build_map.py --godot <Godot 4.5.1>. Run map_edits_0211_tests.py and map_edits_0211_runtime.gd. The latter checks all province/sea picking anchors, selections, demographic counts, save/load and offscreen ownership.

## Absorbed province IDs

- 6611: Amur · Province 2 (fully absorbed by higher-priority state/coast fitting).
