# BunnyWorld 0.1.12 — Cities, population and map/interface improvements

Start a new campaign. Extract the whole Windows ZIP and run BunnyWorld.exe.

- Sparse city skylines and eight simple landmarks, appearing only at close zoom as camera tilt begins.
- Shared metropolitan building allowances, distributed among represented settlements; 4–8 models for ordinary cities and at most 40 for megacities. Nearby rendering has a fixed 384-building / 32-cluster limit.
- Urban province names and city/metropolitan groups; district/locality area labels for large-city coverage.
- Whole urban-province populations include surrounding countryside. Other provinces share the remaining state pool, avoiding thousands of independent population records.
- Historical year-2000 resident-grid estimates, with geographic state populations rebuilt while preserving all country totals. Province and metropolitan populations reconcile exactly with state pools. These are estimates on game province boundaries, not exact municipal census figures.
- Province population information and shared pools appear in inspection panels and close-range tooltips. Tooltips are suppressed directly over open country panels.
- All 1,735 represented city points are linked to the scenario’s starting controller, including separate rebel/de facto territories and year-2000 Ukrainian control of Crimean city points.
- Previous terrain, tilt, materials, atmosphere, sea/lake boundaries and Karafuto/Chishima fixes remain.

Population growth and changing skylines are postponed until demographics in 0.2.

The landmark starter set contains the Eiffel Tower, Statue of Liberty, Big Ben, Tokyo Tower, Pyramids of Giza, Colosseum, Sydney Opera House and Christ the Redeemer.

Native Windows execution remains untested in this environment; final exported-pack checks use Godot 4.5.1 Compatibility on Mesa. See TEST_RESULTS.md.

## Additional approved improvements

- Find place / Ctrl+F with camera navigation for cities, states, countries/tags, metropolitan areas and landmarks; accent-insensitive matching.
- Clear population-scope tooltips and readable fractional areas for tiny provinces.
- Persistent city-buildings/landmarks toggle; sound, graphics and frame preferences save together.
- Gentle land lift and smoother shore elevation transitions, retaining mountain relief.
- Geographic-scale Vatican vector footprint shared by colour, border and picking; restored surrounding Italian territory and corrected Colosseum selection.

The application remains version 0.1.12. This updated starting world uses scenario bunny_world_2000_0_1_12_r2; test from a fresh campaign. No old-save migration is added. Demographics and politics remain in 0.2.
