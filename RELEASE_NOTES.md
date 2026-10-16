# Bunny World 0.2.0.15 — State corrections and map audit

Apply this changed-files patch over working **0.2.0.14**. Close Godot, back up the folder, extract and replace files, then run **Prepare_BunnyWorld.bat in the game folder** so the updated border resources are restored. Open project.godot with Godot 4.5.1 and start a **fresh campaign**. No Windows executable is included. Offline generation tools are supplied for development; players do not need to run them.

## State changes

- The former Korean DMZ strip provinces and UNDOF strip province are dissolved into closest adjacent same-controller provinces. The long selectable strip shapes and their obsolete IDs are gone.
- UNDOF Zone is removed as a State. Its existing bookkeeping is incorporated into Southern Syria.
- Jersey/Sark become one **Channel Islands** State; island provinces remain distinct.
- The tiny Arctic State called Krasnoyarsk was a footprint of **Uyedineniya Island**, not the city. It is incorporated into Krasnoyarsk Krai, retaining the island province.
- The previous South Sumatra / Lampung State also contained Banten, Jakarta and West Java. It is separated into **South Sumatra–Lampung** and **Western Java**, using existing province footprints. Retained State population and inventories are apportioned by existing province area; country totals are unchanged. This is bookkeeping, not a revised local demographic estimate.
- Czech labels now describe the actual administrative unions: Western and Southern Bohemia, Northeastern Bohemia, Moravia–Silesia, Central Bohemia–Vysočina. Prague and Brno no longer appear under the wrong historic-region labels. Existing province footprints are retained.
- Incorrect inherited names are corrected in Kazakhstan, Afghanistan, Estonia, Mexico, Nigeria, Sudan, Tunisia, Yemen and Finland. Cornwall's actual Devon/Cornwall union is named explicitly. Full mappings follow below.
- Existing capital-city coordinates are used to correct country-capital State references where unambiguous, including Tokyo, Seoul, Canberra, Washington and Jakarta. Starting country ownership is preserved.

## Selection and borders

The old smoothing could remove a quarter of a long segment at a corner. Selection contours now preserve substantial geometric corners and bound incidental smoothing to less than half a source pixel. All State/province/sea selection fields are rebuilt from current categorical IDs. This is display preparation, not a general province redraw.

State and internal province meshes are regenerated together. Former State boundaries that are now internal province boundaries are included, and very short real adjacencies omitted by contour extraction are restored. Province borders remain visible slightly farther out. Countries with straight borders retain their genuine corners.

Country names stay enabled and retain the cached rendering from 0.2.0.13. Camera movement does not rebuild label meshes or decode/upload selection geography. Native Windows GPU performance still requires player testing.

## Audit scope and limits

The machine-readable worldwide report is `validation_0215/state_audit.json`. It records State identities, source subdivision unions, city-name mismatches, disconnected components, selection-mask coverage and actual province counts. All State/province/sea field records and all internal province adjacency edges are validated separately.

This is a worldwide automated audit with focused review of findings, not a historical certification of every boundary. Real archipelagos, enclaves, separated administrative pieces and accepted scenario control can explain disconnected footprints and are not erased merely to make shapes contiguous. Name heuristics can flag legitimate regional names that differ from ADM1 names; those flags are not automatically treated as defects.

Three coarse reference-overlap flags remain for the Bahamas, Riau Islands and Southwest Finland. Their audit samples include land absent from the generalized ADM1 source; a detailed coastline comparison remains appropriate. Their ownership and accepted land footprints are retained. Very small States below the coarse audit grid are covered by full-resolution identity/field integrity checks rather than a fabricated coarse overlap percentage.

**Turku:** the stored city position is already 60.45148° N, 22.26869° E, matching GeoNames 633679, and lies in Southwest Finland. It is not relocated to an invented coordinate. The reported visual misplacement was not reproduced as a data-coordinate error.

## Province work deferred

The full province shape/density redesign is deliberately separate. Central Denmark genuinely has 1 province, Southern Denmark 12, and North Rhine-Westphalia 4; this is not just hidden linework. These examples are recorded in the audit for the next patch. No general subdivision, smoothing or density redistribution is applied here. The only province geometry changes are the specifically requested strip dissolutions.

## Test order

1. North Dakota and a rectangular Australian State: select/deselect and change zoom. Corners should remain aligned with the State footprint.
2. North Sumatra: inspect the full State and its provinces; check all land portions and internal borders.
3. Both former Korean DMZ strips and the former Syrian UNDOF strip: no long separate strip provinces or strip States should remain.
4. Channel Islands, Prague/Brno, Astana/Qaraghandy, Devon/Cornwall, Uyedineniya/Krasnoyarsk Krai, and the Sumatra/Western Java split.
5. Verify country-capital State labels, names enabled during rotation/zoom, State panel without scrolling, and wheel blocking over UI.

## Corrected names

| Country | Previous | Corrected |
| --- | --- | --- |
| CZE | Sumava | Western and Southern Bohemia |
| CZE | Bohemia | Northeastern Bohemia |
| CZE | Czech Silesia | Moravia–Silesia |
| CZE | Moravia | Central Bohemia–Vysočina |
| KAZ | Kyzylorda | Jambyl–Turkistan |
| KAZ | Kostanay / Akmola | Akmola–Kostanay–North Kazakhstan |
| KAZ | Astana | Karaganda–Kyzylorda |
| AFG | Badakhshan | Herat |
| EST | Tartu | Southern Estonia |
| EST | Lääne | Harju–Lääne–Pärnu |
| EST | Harju | Eastern Estonia |
| MEX | Guanajuato | San Luis Potosí–Zacatecas |
| NIG | Sokoto | Kebbi–Niger |
| NIG | Kano — North | Sokoto–Zamfara |
| NIG | Kano — South | Kano–Kaduna–Katsina |
| SUD | Khartoum | Kassala–Al Qadarif |
| SUD | White Nile | Khartoum–White Nile |
| TUN | Gabès | Central Tunisia |
| YEM | Taiz | Al Hudaydah–Al Mahwit–Raymah |
| FIN | Lappi | Kainuu–Northern Ostrobothnia |
| ENG | Cornwall | Devon and Cornwall |

## Reference sources

- Natural Earth ADM1: https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/ — the supplied geographic_subdivisions.geojson, not an assertion that all current subdivisions existed in 2000.
- GeoNames settlement coordinates and island gazetteer, CC BY 4.0: https://www.geonames.org/ and https://download.geonames.org/export/dump/.
- Turku: https://www.geonames.org/633679/turku.html; https://www.turku.fi/en/about-turku/maps-and-geographic-information.
- Czech regional reference: https://csu.gov.cz/kraje-spolecne/territorial-units.
- Kazakhstan regional reference: https://stat.gov.kz/en/region/.

The accepted scenario country footprint and all country population totals are conserved. Dynamic city growth, resource deposits, political-system content and save compatibility are outside this patch.
