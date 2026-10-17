# BunnyWorld 0.2.0.25 — follow-up fixes, Antarctic terrain and state audit

Apply over the complete **0.2.0.24** source project. Close Godot and the game,
extract beside `project.godot`, replace files, run **Prepare_BunnyWorld.bat**, reopen
the project and start a fresh campaign. App/geography/display version: **0.2.0.25**.

## Changes

- The supplied loading/menu photograph decodes directly from its JPEG, avoiding stale
  editor import-cache dependence. A single cached texture serves loading and menu.
  The original JPEG is also explicitly included in resource exports.
- Restored Antarctica from the bundled geographic coastline source using the existing
  neutral-land sentinel. No playable country, population, ordinary state or gameplay
  province was invented. A future Antarctica research/territory system can use special
  neutral regions rather than normal national diplomacy and elections.
- Added authoring checks so a world declaring Antarctic terrain cannot rebuild while
  known interior Antarctic land pixels are missing.
- Restored the inline state demographics chart and Age/Religion/Education/Activity
  buttons. State contents scroll on shorter screens. This restores the UI; local
  demographic distribution improvements remain their separate planned data patch.
- Rota joins Mariana Islands, keeping its province.
- Western Papua joins Southern Papua. Papuan Highlands and Sepik join Northern Papua.
  Papua New Guinea now has four states: those two mainland regions, Bismarck Archipelago
  and Bougainville. These broad unions retain the directional names that fit them.
- Added a complete MD count and naming audit, and Windows release-export instructions.

No owned province footprint changes. Country and world populations remain unchanged.
Current totals: **224 countries, 1,235 states, 13,308 land provinces**; population
**6,144,737,528**. The restored Antarctic terrain is outside these gameplay counts.

## State audit

See `documentation/state_audit_0225/AUDIT.md`, `country_counts.csv` and `audit.json`.
The bundled MD reference matches both the supplied archive's state-history and
province-definition checksums. It contains 1,250 states at 1 January 2000.

34 current countries fall below their raw MD counts, with 82 states of combined
country shortfalls. The global net difference is only 15, because other countries
have more states and country/territory groupings differ.

The report gives all country counts, current/MD names, regional candidates, naming
flags and a proposed order: Philippines first, then China/Syria, followed by Taiwan,
India, Pakistan, Morocco and Colombia. It preserves explicit user consolidations,
especially single-state Micronesia and the newly approved four-state Papua New Guinea.
The broader regional splits and naming pass are proposed separately; this patch
does not automatically redraw 82 states or reverse the user's island mergers.

## Local test order

1. Confirm the photograph on loading and the main menu. Check version .25.
2. Rotate south in political and physical modes: Antarctica should be land again,
   with an unclaimed-terrain tooltip, and no selectable Antarctica country.
3. Select a state. Check the inline pie and all four metric buttons. At a smaller
   window height, scroll the state drawer and ensure all contents remain reachable.
4. Inspect Mariana Islands and Papua New Guinea's four states. Check moved provinces
   select the new parent state and old state names are absent from the state browser.
5. Export/run a release EXE using `documentation/EXPORT_WINDOWS.md`; compare movement
   at the same settings with Godot closed. Report native appearance and smoothness.

## Validation and limits

92 full-application checks pass in Godot 4.5.1 GL Compatibility on Linux llvmpipe,
including startup with the photograph's imported cache deliberately absent, all four
inline selectors, prior UI interactions and visible Antarctic terrain in three modes.
The independent data suite passes 38,887 checks, including every owned province's
unchanged pixels, hierarchy/references, country totals and Antarctic interior/ocean probes.
The photo also survives a resource-export fixture and decodes from its exported JPEG.
Prepared map resources and geography/display/cache contracts pass.

Native Windows performance remains the user's test. No Windows executable was
exported here, and this patch does not contain the proposed renderer redesign.
The accepted performance priority is smooth play ahead of startup time.
