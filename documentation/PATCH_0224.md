# BunnyWorld 0.2.0.24 — interface and island cleanup

Changed-files source patch over the complete **0.2.0.23** project. This is separate
from the proposed experimental map renderer. Existing .23 performance changes remain.

## Installation

1. Close Godot and the game. Keep your working .23 folder as a backup.
2. Extract the ZIP into the .23 project folder containing `project.godot`, replacing files.
3. Run `Prepare_BunnyWorld.bat` in that folder and wait for success.
4. Open `project.godot` in Godot 4.5.1 Standard and press F5.
5. Confirm version **0.2.0.24** and start a fresh campaign. No Windows executable is included.

Prepared map resources are included as checksum-verified compressed parts. Preparation
restores those resources; it does not run the expensive geography authoring pipeline.
Obsolete hash-named repository parts left by ZIP overlay are unused and harmless.

## UI test group — your native appearance/interaction check

1. Launch: the supplied Moon/Earth photograph should appear during loading and behind
   the main menu, without stretching. The menu sits to the left so the Earth and Moon remain visible. It disappears when entering country selection.
2. Start as South Korea. Open Country Control, then another country's diplomacy view:
   both use the wider 370-pixel inspector (previously 330).
3. Click a South Korean state. The country breadcrumb should show a small flag.
   Click that country button: the globe centers on the country and opens its state list.
4. Hover different state rows: the corresponding state highlights temporarily. Moving
   away, collapsing/hiding the drawer, or selecting a state clears that preview.
   Hover does not change the selected state, ownership or camera position.
5. Click Research, then Economy, Production, Trade and the other planned toolbar sections.
   Each should replace the left inspector with an empty panel titled for that section.
   Close with × or click the same toolbar button again. Country inspection should reopen normally.
6. Repeat the layout check at your usual window size. Report clipping or overlap with a screenshot.

## Geography test group

| Area | Expected result |
| --- | --- |
| Mariana Islands | One state including former Saipan and Tinian provinces |
| Hawaii | Also includes former Johnston and Midway provinces |
| Micronesia | One state including all former Micronesian states and Palau's province |
| Palau | No separate country or state; Koror remains a mapped settlement in Micronesia |
| Malpelo and Navassa | No state, province, land footprint or island scenery |

Province IDs survive all state mergers. Only provinces 3024 and 13050 are deleted
(five native raster pixels). World population stays 6,144,737,528. Palau's population
joins Micronesia; the old Malpelo/Navassa statistical allocations remain within their
original countries, assigned to the nearest remaining owned state (373 to
Tolima / Antioquia; 8,250 to Guantanamo Bay). This avoids silently changing national
demographics during a geography cleanup; demographic refinement remains separate.

Expected totals: **224 countries, 1,239 states, 13,308 land provinces**.

## Technical checks

The authoring entry point rebuilds adjacency, borders, spatial batches, smooth
province-pair/coast fields and the tiny-island fallback from the final categorical
province raster. There are no country-specific repair masks. The tiny-land fallback
now rebuilds on topology changes too, preventing deleted islands remaining visible.

State previews only change presentation uniforms and existing coast-window selection.
The actual selected state/province and worldwide simulation remain untouched.
Placeholder sections share the existing country inspector rather than stacking panels.

Automated results are recorded in `validation_0224`. Native Windows appearance,
input feel and performance are the user's final test; no new FPS claim is made.
