# Bunny World 0.2.0.14

Rebuilt source patch for the working 0.2.0.13 installation. This is a new rebuild, not a recovered copy of the lost original archive. Godot 4.5.1. Start a fresh campaign.

## Install

Close Godot. Back up your working 0.2.0.13 folder. Extract this ZIP into that folder and replace matching files. Run Prepare_BunnyWorld.bat if needed, then open project.godot. This patch contains changed files; it is not a standalone game or Windows executable.

## Interface

Country Control and Diplomacy share the left inspector and show domestic or foreign content as appropriate. State and sea information has an independent right inspector. The State inspector has no scroll container; population, area, capital, province count, slots, buildings, infrastructure and resources have compact sections. Capital names focus the map. Buildings use cached placeholder icons and counts; infrastructure types use levels out of 10. Ordinary slot capacity increases with population and never discards the existing inventory. Resource deposits are explicitly unavailable until authored.

Province population estimates and the 2000 starting-estimate line are removed. State population is authoritative. City scenery uses normalized State weights and a capital preference as groundwork for future growth; demographic growth and automatic city expansion are not implemented here.

## Map and cities

Prepared distance fields now drive close-view selected fill and outlines from the same coverage. This includes sea selection, coast clipping and the merged States. Existing country-name meshes remain cached and enabled; camera motion does not rebuild names or decode selection geography. Small differences at categorical picking boundaries remain possible because smoothing is visual.

Every State has a capital focus. The largest available mapped settlement by source rank is used for 1,292 States; 63 unresolved or remote States retain an explicitly labelled administrative anchor. 603 city markers and 554 capital scenery clusters were added. GeoNames ranks select settlements, not year-2000 local population. Decorative building instances decrease from 114,191 to 85,643, with offsets compressed to 88%. Functional building inventories are retained; infrastructure levels are capped at 10.

## State changes

| Removed / consolidated State | Destination |
| --- | --- |
| Korean Demilitarized Zone (North) | Kangwon |
| Southern DMZ | Gangwon |
| Samdu Valleys; Himachal Pradesh – Tirpani Valleys | Himachal Pradesh |
| Toba; Southern North Sumatra; Northern Sumatra | North Sumatra |
| Chișinău; Bălți | Chișinău–Bălți |
| Mainland pieces formerly in Åland | Southwest Finland |

Åland retains only original Province 6 (ID 3865). Each former DMZ strip is consolidated whole into its same-owner adjoining State. World and country population totals are conserved. Result: 1,355 States and 13,594 provinces.

## Before / after player checklist

1. Open Japan near Tokyo: select State, province, then Coast of Japan. Compare fill edges and coast lines at close zoom. Rotate and zoom with names enabled.
2. Open a densely built State: check the right inspector at 1100×700 and a larger resolution. All State sections should fit without scrolling. The mouse wheel over UI must not zoom the map.
3. Select your country, then another country: the left inspector should switch domestic/diplomatic content while the State inspector remains independent.
4. Check Åland Province 6, Southwest Finland, North Sumatra, Moldova, Himachal Pradesh and both former DMZ strips.
5. Verify State capital focus, province count, building slots and infrastructure n/10. Check cities look denser with fewer decorative buildings.

## Attribution and limits

Additional settlement coordinates/ranks: GeoNames, https://www.geonames.org/ and https://download.geonames.org/export/dump/ — retrieved 16 October 2026, CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Modern ranks do not assert historical population accuracy. Existing map/font/source attribution remains in the repository. Icons remain placeholders.
