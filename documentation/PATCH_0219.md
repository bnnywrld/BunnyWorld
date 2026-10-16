# BunnyWorld 0.2.0.19 — requested State consolidation

Apply over 0.2.0.18. Close Godot, extract beside project.godot, replace files, run Prepare_BunnyWorld.bat, then start a fresh campaign. This is a changed-files source patch; no new Windows executable is included.

All 55 request numbers are covered. 53 State records are merged, giving 1,252 States and 13,311 land provinces. Islands keep their footprints inside their destination States. Tiran and Sanafir are dissolved into Sinai Province 14. Global population is preserved. Country population moves only with the requested ownership-changing mergers.

| Request | Removed State | Destination |
| --- | --- | --- |
| 1 | Hans Island (448) | Qaasuitsup / Pituffik (447) |
| 2 | Minsk — North (85) | Minsk (84) |
| 3 | Crimean Border Strip (1262) | Crimea (1277) |
| 4 | Danube disputed islands (972) | South Bačka / Central Banat (971) |
| 5 | Dragonja River (248) | Adriatic Croatia (1776) |
| 7 | Islas Chafarinas (704) | Melilla (1615) |
| 8 | Olivenza (1756) | Extremadura (1620) |
| 9 | Penon de Alhucemas (703) | Melilla (1615) |
| 10 | Peñón de Vélez de la Gomera (702) | Melilla (1615) |
| 11 | Isla del Perejil (705) | Meknès-Tafilalet / Rabat-Salé-Zemmour-Zaër (695) |
| 12 | Tiran and Sanafir (1762) | Sinai (1440) |
| 13 | East Jerusalem (1760) | Jerusalem (1552) |
| 13 | Latrun (1761) | Jerusalem (1552) |
| 14 | Central (1551) | Tel Aviv (1553) |
| 15 | North Pemba / South Pemba (1204) | Zanzibar (1203) |
| 16 | Duhok (502) | Duhok (591) |
| 17 | Baghdad (515) | Babylon (516) |
| 18 | Sulaymaniyah (506) | Sulaymaniyah (874) |
| 19 | Abu Musa I. (818) | Hormozgan (801) |
| 20 | Herat (4) | Herat (1187) |
| 21 | Rockall I. (1490) | Outer Hebrides (1469) |
| 22 | Chandigarh (914) | Punjab — South (891) |
| 23 | South Karnataka (910) | Karnataka (906) |
| 24 | Dadra and Nagar Haveli and Daman and Diu (903) | Gujarat (893) |
| 25 | Yunnan (1382) | Shan State / Chiang Mai (1383) |
| 26 | Lesser Sunda Islands (494) | West Nusa Tenggara (483) |
| 28 | Natuna Islands (497) | Riau Islands (1811) |
| 29 | Scarborough Reef (224) | Central Luzon (1792) |
| 30 | Spratly Islands (1796) | Mimaropa (1789) |
| 31 | Pratas Islands (211) | Southern Taiwan (1649) |
| 32 | Dokdo (1576) | North Gyeongsang (1574) |
| 33 | Senkaku (1567) | Okinawa (1566) |
| 34 | Jervis Bay Territory (1411) | New South Wales (1410) |
| 35 | Lord Howe Island (1415) | New South Wales (1410) |
| 36 | South Island — South (748) | South Island (752) |
| 37 | Chatham and Antipodes Islands (749) | North Island (753) |
| 38 | Southern Patagonian Ice Field (34) | Patagonia (29) |
| 38 | Southern Patagonian Ice Field (231) | Southern Chile (229) |
| 39 | Bajo Nuevo Bank (547) | Magdalena / Santander (236) |
| 40 | Archipelago of Saint Andréws (237) | Magdalena / Santander (236) |
| 41 | Serrana Bank (241) | Magdalena / Santander (236) |
| 42 | Serranilla Bank (242) | Magdalena / Santander (236) |
| 43 | Brazilian Island (33) | Rio Grande do Sul (100) |
| 44 | Corner of Artigas (129) | Rio Grande do Sul (100) |
| 45 | Western Mindanao (1787) | Northern Mindanao (1790) |
| 47 | Chechen Republic (1007) | Chechnya (176) |
| 49 | Tristan da Cunha (1481) | Saint Helena (1482) |
| 50 | Amsterdam and Saint-Paul Islands (1529) | Kerguelen Islands (1526) |
| 51 | Clipperton Island (1530) | French Polynesia (1523) |
| 52 | Matthew and Hunter Is. (359) | New Caledonia (1521) |
| 53 | Saint Barthélemy (1525) | Saint Martin and Saint Barthélemy (1520) |
| 54 | Free Hanseatic Bremen (428) | Lower Saxony (423) |
| 55 | Monaco (1500) | Nice (1497) |

| Request | Renamed State | Name |
| --- | --- | --- |
| 2 | Minsk — South (84) | Minsk |
| 6 | Liechtenstein (1148) | Zürich–Eastern Switzerland |
| 27 | West Papua — South (480) | West Papua |
| 36 | South Island — North (752) | South Island |
| 46 | Xinjiang — North (177) | Xinjiang |
| 48 | Jewish (1023) | Jewish Autonomous Oblast |
| 53 | Saint Martin (1520) | Saint Martin and Saint Barthélemy |
| 46 | Tibet — South (178) | Tibet |

Zürich–Eastern Switzerland reflects the Swiss cantons in the incorrectly labelled Liechtenstein State; the separate Liechtenstein country is retained. Mainland Chinese Yunnan is untouched. Monaco joins Nice, France. Duhok, Sulaymaniyah, Herat and Chechnya use the main existing State and its scenario owner. Spanish offshore enclaves join Melilla; Perejil joins its existing Moroccan parent region. Distant UK/French islands join the larger territory named above.

## Test order

1. Check Minsk, Crimea, Switzerland, Bremen and Monaco. Confirm former internal State borders disappear.
2. Check Sinai Province 14, Jerusalem/Tel Aviv, Iraqi duplicate sectors, Herat and Chechnya.
3. Check Wa State, Mindanao, Natuna/Riau, Taiwan/Japan/Korea and New Zealand.
4. Check the Caribbean, Brazil/Uruguay, Patagonia and the remote island destinations.
5. Select merged States at close zoom and switch political/physical modes. Smooth shared-boundary rendering remains enabled.

Performance is unchanged in this checkpoint; it is being addressed in the next separate patch.
