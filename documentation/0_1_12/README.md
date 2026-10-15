# BunnyWorld 0.1.12 — updated map and interface build

Extract the whole Windows ZIP and run **BunnyWorld.exe**. Keep **BunnyWorld.pck** beside it. Windows 10/11 x64, OpenGL 3.3. No editor, installation, HOI4 or internet connection is needed.

**Start a new campaign.** Urban accounting and geographic state population allocations changed; older scenario saves are not loaded into this starting world.

## Graphics and camera

- Actual raised land and mountain geometry driven by NOAA ETOPO 2022 surface elevations. A gentle land lift (about 80 m) and restrained 4× vertical exaggeration make relief readable; coasts transition smoothly toward ocean level. The prepared 8,192 × 4,096 field comes from a 3-arc-minute sample, so it represents broad geographic relief, not individual buildings or precise mountain summits.
- A bounded local mesh supplies finer geometry at close zoom. Borders, city markers and ray picking use the same height field. Camera clearance follows the surface.
- Automatic tilt begins only below camera distance 1.18, reaching **38° away from overhead** at the closest zoom. Zooming out returns overhead smoothly. The inspected point remains the camera target.
- Refined woodland, desert, grassland and rock materials, altitude/slope-aware snow and exposed rock, clearer city microdetail and slope lighting. Existing geographic terrain and the 24-slot offline tile cache remain.
- A wider, softer atmospheric limb, directional blue scattering and stronger physical-map horizon haze.

## Remote provinces

**40,031 land provinces**, down from 45,107. Adjacent remote cells are merged within each state, using conservative city/coastal buffers and state-level density proxies. Cities and their existing province areas are preserved. This is not a detailed population-density map.

| Country | 0.1.10 | 0.1.11 |
|---|---:|---:|
| Greenland | 734 | 290 |
| Algeria | 772 | 339 |
| Canada | 3,270 | 2,701 |
| Russia | 5,614 | 3,976 |
| Australia | 2,596 | 1,805 |
| South Korea | 38 | 38 |
| Luxembourg | 1 | 1 |

Greenland interior targets about 25,000 km²; remote Sahara cells about 15,000 km²; eligible far northern/continental interiors about 18,000 km². Populated cells retain their previous approximately 3,000 km² target. Small states and islands can still have smaller or disconnected clipped cells.

North/South Chishima and Karafuto remain separate and corrected. State buildings, cores/claims, province IDs, 118 ocean zones and lake exclusions are preserved. The local Vatican/Rome coverage is corrected in this updated build. Country population totals are preserved; state populations now follow the year-2000 grid on their actual game coverage. Scope: 223 active countries, 1,235 states, 19 organizations; total population exactly 6,144,737,528. Uniform starting values remain 100 political power, 65% Stability, 50% War Support.

## Cities, landmarks and population

- Sparse representative buildings appear as the close camera starts tilting. They fade in below distance 1.18, reach full visibility at 1.08 and disappear farther out. Buildings render in every map mode; existing urban textures remain at wider zoom.
- Towns receive 2 models, cities 4–8, large cities 8–16, metropolises 16–24 and megacities up to 40. These are representative scenery, not individual simulated buildings. A metropolitan group shares its allowance across its provinces and settlements. Dense settlement population drives the class; surrounding countryside does not inflate the skyline. Development influences height.
- Eight lightweight landmarks: Eiffel Tower, Statue of Liberty, Big Ben, Tokyo Tower, Pyramids of Giza, Colosseum, Sydney Opera House, Christ the Redeemer. Their approximate real locations are retained; visual size is exaggerated for readability. All existed by the 2000 start.
- At most 384 building instances in 32 nearby clusters; repeated geometry is batched, landmark parts are baked into one mesh each, no individual shadows/physics, and at most two new clusters are constructed per refresh. Actual performance still needs testing on Windows hardware.
- 2,220 provinces carry urban population, organized in 1,557 city/metropolitan groups. Their population includes all residents within the province, including countryside. Other provinces share a single remaining pool per state and have no individual population number.
- Large-city pieces use district/locality area names; multicity provinces use established metropolitan names where curated, otherwise clearly descriptive names. The general province layout is retained, with the local Vatican correction described below; district/locality names describe coarse game coverage rather than municipal borders. All 1,735 represented map settlements are linked to their province and starting controller; this is not a complete census of every town.
- Year-2000 resident estimates use European Commission JRC GHS-POP R2023A at 30 arc-seconds. Grid shares are reconciled within each country to the supplied scenario country total, then summed to rebuild geographic state totals. This corrects inherited state-total/coverage mismatches. Small zero-grid islands retain scenario-based fallback shares. Country and global totals remain exact.
- The selected province panel shows its population, whole city/metropolitan group total and the state shared pool. The state population map follows the rebuilt totals. Estimates are labelled; country reconciliation and sparse-grid fallback details are in `data/urban_population.json`.
- No annual growth, migration, demographics or automatic skyline expansion yet. These will use the same structure when population simulation arrives in 0.2. Console population edits keep the accounting consistent but do not regenerate scenery.

## Additional improvements in this updated 0.1.12

- **Find place** on the map toolbar, or **Ctrl+F**, searches cities, states, countries/tags, metropolitan groups and the eight landmarks. Accented names can be typed without accents. Choose a result or press Enter to move the camera and open its information; the player country remains unchanged. Search pauses the clock and restores its prior pause state on dismissal/navigation.
- Population tooltips distinguish whole urban-province residents, the combined city/metropolitan total, and the pool shared by all non-city provinces of a state. Long descriptions wrap within the tooltip. Small province areas retain decimals.
- Game menu → **City buildings and landmarks** enables/disables close-range models. City labels, distant urban texture and population information remain. The choice is saved between launches, together with sound, graphics and frame-limit settings.
- The former flat land lift was too high. It is now about 80 m with a smooth coastal transition; 4× mountain relief remains. This reduces abrupt elevation changes without redrawing the accepted coast/lake geography. The source coastline still has finite resolution.
- Vatican City's oversized 111 km² raster control patch is restored to Italy. Its country fill, border and clicks now share a small geographic-scale vector reference. The official stated area (0.44 km²) appears in its information panel, and the Colosseum remains in Italy. The reference polygon is approximate and distinct from the official stated area. No additional microstate countries are introduced into the scenario roster.

## Controls

Right drag rotates; wheel zooms. Left click inspects land or an ocean zone. Click your upper-left flag/name for country controls. F focuses the inspected country. Space pauses/plays; 1–4 change speed; F5/F9 save/load; F11 fullscreen; Escape menu; backtick console. States appear at 1.65, provinces at 1.20. Start → choose country → Play; time starts paused.

Eight modes remain: Political, Organizations, Population, Outlook, GDP, GDP/person, Physical Earth and Relations. Terrain geometry and camera tilt apply across modes; physical materials and stronger slope lighting apply to Physical Earth.

Saves: `%APPDATA%/BunnyWorld/saves`. Save before closing. Loads resume paused; overwrites retain a backup. Schema 8, scenario `bunny_world_2000_0_1_12_r2`.

## Sources and limits

NOAA NCEI ETOPO 2022, DOI [10.25921/fd45-gt74](https://doi.org/10.25921/fd45-gt74), sampled through NOAA ERDDAP; ice-surface edition retains Greenland/Antarctic ice-sheet elevation. Geographic source imagery, height resolution, city annotations and special control footprints remain approximate. The new material master and exact built-in Image Generation prompt are in `assets/materials/DETAIL_021.md` in the source.

Calendar/interface foundations remain; economy, construction, armies, war and campaign AI are not implemented. Native Windows launch and performance on your hardware remain your play test. Completed checks are recorded in TEST_RESULTS.md.
