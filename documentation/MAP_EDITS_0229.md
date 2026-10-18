# BunnyWorld 0.2.0.29 — edited-map integration

Changed-files patch over **0.2.0.28**. **224 countries, 1,261 states, 13,198 land provinces and 120 sea regions**. No new province IDs. World population remains **6,146,495,066**.

## Applied rules

- The uploaded `newsts.zip` maps are the approved geometry. All edited state pixels and sea pixels are preserved exactly.
- State borders override competing province shapes. Existing province colours/IDs are fitted inside the edited states.
- Detached inland pieces and small new fitting slivers are absorbed into bordering provinces of the same state. Real separate islands may share a province.
- Only two fully erased IDs are removed: **10465 — Istanbul · Province 7**, and **12585 — Maracaibo**. Maracaibo city and its buildings/scenery remain; the city now links to province 12597.
- All 2,340 city records, 2,787 scenery clusters and 8 landmarks remain, at their original coordinates. Fourteen city province links changed.
- This uploaded edit set did not change the land/water silhouette. The Åland correction changes state membership of existing land, rather than adding or removing coastline. Antarctic terrain is unchanged.
- Provinces remain movement/building tiles with no resident population. Global simulation and live offscreen owner changes remain independent of map visibility.

## Bookkeeping

Population moved between states is an **educated estimate** proportional to the source state’s transferred land area. This is not a fresh local census or an urban-density estimate. Residents are never created or discarded. Single-age profiles, religious categories, adult-25 education counts and workforce counts are carried with the source residents using exact integer allocation. Global counts are conserved; country totals change only where the painted border transfers land between controllers. All unaffected demographic profiles are unchanged. Buildings and building slots retain their accepted state inventories.

### Country population changes

| Country/controller | Before | After | Change |
|---|---:|---:|---:|
| Afghanistan | 12,551,523 | 12,553,507 | +1,984 |
| Canada | 30,651,732 | 30,651,552 | -180 |
| Germany | 81,268,498 | 81,263,857 | -4,641 |
| Indonesia | 209,683,909 | 209,623,525 | -60,384 |
| Moldova | 3,271,964 | 3,260,761 | -11,203 |
| Transnistria | 966,768 | 977,971 | +11,203 |
| Switzerland | 7,338,389 | 7,343,030 | +4,641 |
| Islamic Emirate of Afghanistan | 7,071,727 | 7,069,743 | -1,984 |
| United States | 286,532,215 | 286,532,395 | +180 |
| Timor-Leste | 745,088 | 805,472 | +60,384 |

## Fitted states

Province counts are preserved in each state except the two explicit removals; no province changed state ID. Pixel-level fitting stays within the approved state geometry.

| State | Provinces before → after | Population before → after | Fitted pixels | Fragment/sliver pixels absorbed |
|---|---:|---:|---:|---:|
| Ghazni / Baghlan (5) | 6 → 6 | 9,123,112 → 9,125,096 | 24 | 3 |
| Bahamas (60) | 5 → 5 | 325,014 → 325,014 | 0 | 0 |
| Wallonie (66) | 4 → 4 | 1,895,484 → 1,878,279 | 0 | 0 |
| Eupen-Malmedy (67) | 3 → 3 | 1,235,465 → 1,250,408 | 12 | 0 |
| Limburg (68) | 2 → 2 | 816,231 → 801,288 | 0 | 0 |
| Brussels (69) | 8 → 8 | 6,515,947 → 6,533,152 | 19 | 1 |
| Altiplano (88) | 16 → 16 | 3,642,426 → 3,642,426 | 0 | 10 |
| Pando el-Beni (90) | 17 → 17 | 2,887,599 → 2,887,599 | 0 | 6 |
| Rio Grande do Sul (100) | 13 → 13 | 10,493,218 → 10,493,218 | 0 | 7 |
| Paraná (106) | 11 → 11 | 9,917,995 → 9,917,995 | 0 | 1 |
| Maranhão (111) | 11 → 11 | 5,865,279 → 5,865,279 | 0 | 9 |
| Espírito Santo — North (120) | 4 → 4 | 3,185,796 → 3,185,796 | 0 | 4 |
| Rio de Janeiro (121) | 7 → 7 | 14,934,360 → 14,934,360 | 0 | 8 |
| São Paulo (122) | 23 → 23 | 38,364,529 → 38,364,529 | 0 | 31 |
| British Columbia (147) | 42 → 42 | 3,996,456 → 3,996,276 | 0 | 183 |
| Ontario (151) | 71 → 71 | 11,717,837 → 11,717,837 | 0 | 5 |
| Zhejiang (190) | 34 → 34 | 46,747,059 → 46,747,059 | 0 | 38 |
| Ecuadorian Andes (282) | 9 → 9 | 7,204,380 → 7,204,380 | 0 | 7 |
| Åland (363) | 2 → 2 | 26,941 → 24,453 | 0 | 0 |
| Bayern (419) | 17 → 17 | 8,293,010 → 8,293,010 | 0 | 7 |
| North Rhine-Westphalia (424) | 21 → 21 | 18,004,279 → 18,004,279 | 0 | 114 |
| Baden-Württemberg (425) | 16 → 16 | 10,272,064 → 10,267,423 | 0 | 35 |
| Hesse (430) | 10 → 10 | 5,967,791 → 5,967,791 | 0 | 9 |
| Central Greece (439) | 10 → 10 | 4,499,796 → 4,205,974 | 0 | 15 |
| Peloponnese (440) | 4 → 4 | 606,848 → 900,670 | 305 | 13 |
| Sud-Haiti (458) | 2 → 2 | 4,852,682 → 4,852,682 | 0 | 1 |
| East Nusa Tenggara / Viqueque (479) | 7 → 7 | 4,031,496 → 3,971,112 | 1 | 0 |
| East Java / Central Java (481) | 38 → 38 | 75,558,856 → 75,558,856 | 0 | 6 |
| Central Sulawesi / South Sulawesi (484) | 25 → 25 | 14,883,797 → 14,883,797 | 0 | 294 |
| Central Sumatra (486) | 23 → 23 | 12,525,396 → 12,680,450 | 194 | 0 |
| South Sumatra–Lampung (487) | 19 → 19 | 14,118,629 → 14,171,194 | 8 | 0 |
| Leinster (501) | 11 → 11 | 2,255,239 → 2,255,239 | 0 | 1 |
| Aosta Valley (528) | 5 → 5 | 2,813,347 → 2,813,347 | 0 | 2 |
| Puglia (531) | 6 → 6 | 3,587,459 → 3,584,498 | 0 | 0 |
| Campania (533) | 8 → 8 | 5,605,986 → 5,608,947 | 3 | 0 |
| Lazio (534) | 6 → 6 | 4,855,934 → 4,855,934 | 0 | 9 |
| Sabah / Labuan (651) | 5 → 5 | 1,272,630 → 1,272,630 | 77 | 0 |
| Selangor / Kuala Lumpur (654) | 5 → 5 | 5,522,121 → 5,522,121 | 0 | 4 |
| Malacca (655) | 8 → 8 | 4,179,635 → 4,179,635 | 1 | 0 |
| Chișinău–Bălți (687) | 7 → 7 | 2,578,499 → 2,567,296 | 0 | 0 |
| Guelmim-Es Semara / Laâyoune-Boujdour-Sakia El Hamra (693) | 5 → 5 | 412,833 → 397,982 | 0 | 0 |
| Guelmim-Es Semara (698) | 2 → 2 | 42,324 → 44,751 | 83 | 0 |
| W. Sahara (699) | 5 → 5 | 225,334 → 237,758 | 413 | 2 |
| North Island (753) | 21 → 21 | 2,917,804 → 2,917,804 | 0 | 0 |
| Panama (776) | 4 → 4 | 1,720,700 → 1,720,700 | 0 | 3 |
| Górny Slask (845) | 11 → 11 | 5,920,057 → 5,920,057 | 0 | 14 |
| Warmian-Masurian Voivodeship (850) | 6 → 6 | 1,436,321 → 1,440,031 | 9 | 0 |
| Pomeranian Voivodeship (854) | 7 → 7 | 2,204,638 → 2,200,928 | 0 | 0 |
| Masovian Voivodeship (855) | 13 → 13 | 5,177,668 → 5,177,668 | 0 | 9 |
| Junagadh and Manavadar (932) | 2 → 2 | 2,570,345 → 2,720,739 | 185 | 1 |
| Lower Amur (1024) | 32 → 32 | 1,468,266 → 1,468,331 | 579 | 0 |
| Zürich–Eastern Switzerland (1148) | 4 → 4 | 2,139,909 → 2,144,550 | 4 | 17 |
| Romandie-Alpes (1149) | 2 → 2 | 1,026,675 → 1,038,944 | 17 | 0 |
| Mittelland (1150) | 7 → 7 | 3,637,913 → 3,625,644 | 0 | 1 |
| Herat (1187) | 10 → 10 | 1,390,864 → 1,389,580 | 0 | 0 |
| Paktika / Ghazni (1189) | 3 → 3 | 321,308 → 321,253 | 27 | 0 |
| Zabul (1190) | 2 → 2 | 217,713 → 218,357 | 9 | 0 |
| Qalat (1191) | 6 → 6 | 765,693 → 763,120 | 0 | 0 |
| Hazarajat (1194) | 6 → 6 | 740,486 → 741,770 | 20 | 0 |
| Odessa (1254) | 14 → 14 | 2,474,820 → 2,474,820 | 0 | 59 |
| Western Australia (1406) | 50 → 50 | 1,827,441 → 1,827,441 | 0 | 8 |
| South Australia (1408) | 29 → 29 | 1,502,543 → 1,502,543 | 0 | 2 |
| Victoria (1412) | 25 → 25 | 4,720,683 → 4,720,683 | 0 | 174 |
| Costa Rica (1431) | 4 → 4 | 3,980,169 → 3,980,169 | 0 | 3 |
| Western Cuba (1434) | 6 → 6 | 4,362,125 → 4,362,125 | 0 | 5 |
| Aswan (1441) | 3 → 3 | 933,843 → 936,485 | 415 | 0 |
| Red Sea Coast (1442) | 5 → 5 | 279,516 → 276,700 | 0 | 0 |
| New Valley (1444) | 9 → 9 | 357,016 → 356,061 | 0 | 0 |
| Suez Canal (1445) | 4 → 4 | 1,835,002 → 2,013,659 | 32 | 0 |
| Eastern Delta (1446) | 7 → 7 | 11,156,342 → 10,977,685 | 0 | 1 |
| Northwest England (1455) | 9 → 9 | 6,777,435 → 6,777,435 | 0 | 50 |
| West Midlands (1456) | 8 → 8 | 5,259,903 → 5,259,903 | 0 | 6 |
| Southwest Scotland (1460) | 6 → 6 | 2,352,136 → 2,352,136 | 0 | 1 |
| Yorkshire (1461) | 8 → 8 | 5,006,838 → 5,006,838 | 0 | 160 |
| Aquitaine (1501) | 11 → 11 | 2,924,799 → 2,927,485 | 11 | 2 |
| Occitanie (1502) | 11 → 11 | 2,570,286 → 2,567,600 | 0 | 1 |
| Île-de-France (1518) | 12 → 12 | 10,990,480 → 10,990,480 | 0 | 5 |
| Southern Guatemala (1538) | 5 → 5 | 11,355,149 → 11,355,149 | 0 | 4 |
| Jerusalem (1552) | 1 → 1 | 1,140,247 → 1,158,261 | 4 | 0 |
| Tel Aviv (1553) | 2 → 2 | 2,643,719 → 2,625,705 | 0 | 2 |
| Northern Kyushu (1555) | 12 → 12 | 8,558,568 → 8,558,568 | 0 | 5 |
| Shikoku (1556) | 9 → 9 | 4,181,410 → 4,177,579 | 0 | 0 |
| Kansai (1558) | 24 → 24 | 23,216,338 → 23,220,169 | 4 | 7 |
| Kanto (1563) | 32 → 32 | 40,486,264 → 40,486,264 | 0 | 8 |
| Tokai (1564) | 15 → 15 | 12,138,364 → 12,138,364 | 0 | 2 |
| Hokkaido (1565) | 19 → 19 | 5,653,568 → 5,653,568 | 0 | 6 |
| Gyeonggi (1569) | 9 → 9 | 21,695,259 → 21,346,636 | 0 | 0 |
| Chungcheong (1570) | 5 → 5 | 4,670,036 → 4,670,036 | 0 | 4 |
| South Gyeongsang (1573) | 6 → 6 | 7,695,506 → 7,695,506 | 0 | 30 |
| North Gyeongsang (1574) | 6 → 6 | 5,273,395 → 5,273,395 | 0 | 6 |
| Navarre (1616) | 3 → 3 | 538,423 → 537,494 | 0 | 0 |
| Aragon (1618) | 8 → 8 | 1,204,373 → 1,272,004 | 87 | 0 |
| Castile and León (1623) | 15 → 15 | 2,435,229 → 2,450,705 | 5 | 0 |
| Valencia (1624) | 10 → 10 | 4,161,069 → 4,094,367 | 0 | 0 |
| Madrid (1632) | 7 → 7 | 5,452,757 → 5,437,281 | 0 | 3 |
| Central Taiwan (1648) | 5 → 5 | 5,007,437 → 5,007,437 | 0 | 5 |
| Southern Taiwan (1649) | 6 → 6 | 6,204,071 → 6,204,071 | 0 | 6 |
| Thrace (1656) | 5 → 5 | 1,259,448 → 1,286,139 | 2 | 0 |
| Istanbul (1661) | 7 → 6 | 10,292,625 → 10,293,227 | 0 | 1 |
| Balikesir (1662) | 5 → 5 | 1,376,641 → 1,349,950 | 0 | 0 |
| Kocaeli (1665) | 7 → 7 | 2,618,028 → 2,617,426 | 0 | 0 |
| Washington (1674) | 45 → 45 | 5,894,121 → 5,894,301 | 19 | 23 |
| Minnesota (1678) | 45 → 45 | 4,919,479 → 4,919,479 | 20 | 7 |
| Michigan (1679) | 52 → 52 | 9,938,444 → 9,938,444 | 0 | 10 |
| Arizona (1686) | 54 → 54 | 5,130,632 → 5,130,632 | 0 | 10 |
| California (1687) | 161 → 161 | 33,871,648 → 33,871,648 | 0 | 41 |
| Texas (1689) | 163 → 163 | 20,851,820 → 20,851,820 | 0 | 59 |
| Louisiana (1691) | 33 → 33 | 4,468,976 → 4,468,976 | 5 | 0 |
| Florida (1694) | 68 → 68 | 15,982,378 → 15,982,378 | 0 | 39 |
| Georgia (1695) | 49 → 49 | 8,186,453 → 8,186,453 | 0 | 13 |
| Connecticut (1703) | 10 → 10 | 3,405,565 → 3,403,232 | 0 | 0 |
| Rhode Island (1704) | 4 → 4 | 1,048,319 → 1,049,243 | 2 | 0 |
| Massachusetts (1705) | 17 → 17 | 6,349,097 → 6,350,506 | 1 | 13 |
| Oregon (1706) | 41 → 41 | 3,421,399 → 3,421,399 | 0 | 8 |
| Colorado (1711) | 47 → 47 | 4,301,261 → 4,301,261 | 0 | 10 |
| Illinois (1719) | 58 → 58 | 12,419,293 → 12,419,293 | 0 | 5 |
| Indiana (1724) | 33 → 33 | 6,080,485 → 6,080,485 | 0 | 13 |
| El Salvador (1746) | 2 → 2 | 5,952,218 → 5,952,218 | 0 | 1 |
| Timor-Leste (1749) | 3 → 3 | 745,088 → 805,472 | 56 | 1 |
| Halayib Triangle (1759) | 1 → 1 | 9,497 → 10,626 | 129 | 0 |
| Baengnyeong Islands (1763) | 1 → 1 | 1,187 → 349,810 | 43 | 0 |
| Okhotsk Kraj (1765) | 4 → 4 | 11,650 → 11,585 | 0 | 0 |
| Transnistria (1767) | 3 → 3 | 966,768 → 977,971 | 20 | 0 |
| Lower Austria and Vienna (1769) | 9 → 9 | 3,088,299 → 3,088,299 | 0 | 2 |
| Western Venezuela (1782) | 13 → 12 | 8,647,092 → 8,647,092 | 97 | 2 |
| Riau Islands (1811) | 3 → 3 | 1,123,455 → 1,103,011 | 0 | 0 |
| North Sumatra (1813) | 14 → 14 | 12,179,239 → 12,044,629 | 0 | 0 |
| Southwest Finland (1826) | 9 → 9 | 447,701 → 450,189 | 115 | 115 |
| Western Java (1827) | 24 → 24 | 54,987,536 → 54,934,971 | 0 | 4 |
| Saurashtra–Kutch (1847) | 8 → 8 | 13,470,230 → 13,319,836 | 0 | 0 |

## Rebuilt together

Current categorical PNGs, province index, province/state adjacency, province/state border meshes, sea border mesh and neighbours, spatial render batches, shared boundary fields, coast fields/windows, tiny-island coverage, sea selection fields, GPU sea mask and versioned/checksummed restore bundles. The shared pipeline now registers sea-ID edits instead of reusing old sea selection geometry.

## Validation

**101,898 data checks** and **42,073 Godot 4.5.1 headless checks**, zero failures. Includes exact uploaded state/sea pixels; retained province IDs; 4-connected province fragments on all fitted state landmasses; references/capitals; city and scenery preservation; exact global demographic/workforce conservation; every province interior picking anchor; all 120 sea anchors and selection uploads; map modes; save/load; and offscreen ownership updates without geometry rebuilding.

Headless validation does **not** establish Windows visual quality or FPS. The previously reported close-zoom border-rendering artifacts and broader city-province generation refinements still need their own investigation.

## Apply and test

1. Close Godot and the game. Back up the working .28 folder.
2. Extract the patch over .28, replacing included files. Run **Prepare_BunnyWorld.bat**; all reported versions must be **0.2.0.29**.
3. Open with **Godot 4.5.1 Standard**, allow imports to finish and start a **fresh campaign**.
4. Check Åland/southwest Finland, Brussels, the edited Egyptian/Afghan borders and Timor. Select states and provinces on both sides.
5. Check your city-province edits, especially Chicago/Tokyo/Yokohama and Maracaibo; confirm the city remains after its tile merger.
6. Check sea borders and highlights in the Baltic, North Sea, Canadian Arctic, Japan/Okhotsk and Indonesia.
7. Change an offscreen state owner with the existing console, return to it and verify the colour/owner.
8. Try physical and political modes at several zoom levels. Compare close-zoom border artifacts separately; this patch does not claim to fix them.
9. Save/load within .29. Old-version saves are unsupported.

No Windows EXE is included. Use the existing Windows export instructions. `PATCH_REMOVED_FILES_0229.txt` lists obsolete prepared asset parts; unreferenced old parts are harmless if retained.

## Reproducibility

`tools/cartography/edits_0229/tile_*.npz` and `sea.npz` retain the exact decoded old/new editing maps. `baseline/` and `runtime_before.json` retain the .28 data used for bookkeeping. Starting from the recorded .28 commit, restore prepared assets, copy the included decoded inputs/baseline capture, run `tools/apply_edits_0229.py`, then `tools/build_map.py --godot <Godot 4.5.1>` and the .29 tests. Run the baseline capture only before editing. `data/map_edit_audit_0229.json` records transfers, fitting, removals and exact expected demographic counts.
