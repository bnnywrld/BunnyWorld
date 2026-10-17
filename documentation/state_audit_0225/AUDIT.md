# State count and naming audit — 0.2.0.25

Bundled MD reference: **1250 states** at 1 January 2000. Current BunnyWorld: **1235 states**.
**34 countries** are below their raw MD counts, with **82 states** of combined country shortfalls. These are not the global net difference: other countries have more states, and ownership/territory grouping differs.

The supplied MD archive matches the bundled state-history and province-definition checksums.

The user-approved single Micronesia state and four Papuan states remain explicit exceptions. Other requested island/state unions stay intact; useful inhabited regions should receive additional detail instead of recreating discarded islands.

| Country | Current | MD | Shortfall |
| --- | ---: | ---: | ---: |
| Philippines (PHI) | 8 | 20 | 12 |
| China (CHI) | 35 | 43 | 8 |
| Syria (SYR) | 8 | 15 | 7 |
| Micronesia (MIC) | 1 | 7 | 6 |
| India (RAJ) | 40 | 45 | 5 |
| Republic of China (TAI) | 6 | 11 | 5 |
| Morocco (MOR) | 7 | 11 | 4 |
| Pakistan (PAK) | 8 | 12 | 4 |
| Colombia (COL) | 5 | 8 | 3 |
| Georgia (GEO) | 2 | 4 | 2 |
| Somaliland (SML) | 1 | 3 | 2 |
| United States (USA) | 62 | 64 | 2 |
| Afghanistan (AFG) | 2 | 3 | 1 |
| Angola (AGL) | 2 | 3 | 1 |
| Argentina (ARG) | 7 | 8 | 1 |
| Azerbaijan (AZE) | 4 | 5 | 1 |
| Bhutan (BHU) | 1 | 2 | 1 |
| Bosnia (BOS) | 5 | 6 | 1 |
| Chile (CHL) | 5 | 6 | 1 |
| Comoros (COM) | 1 | 2 | 1 |
| Costa Rica (COS) | 1 | 2 | 1 |
| El Salvador (ELS) | 1 | 2 | 1 |
| Germany (GER) | 16 | 17 | 1 |
| Greenland (GRN) | 3 | 4 | 1 |
| Indonesia (IND) | 16 | 17 | 1 |
| Madagascar (MAD) | 3 | 4 | 1 |
| Moldova (MLV) | 2 | 3 | 1 |
| New Zealand (NZL) | 4 | 5 | 1 |
| Papua New Guinea (PAP) | 4 | 5 | 1 |
| Serbia (SER) | 3 | 4 | 1 |
| Solomon Islands (SOL) | 1 | 2 | 1 |
| Spain (SPR) | 19 | 20 | 1 |
| United Kingdom (ENG) | 34 | 35 | 1 |
| Wa State (WAA) | 1 | 2 | 1 |

## First geography passes

1. Philippines: the largest shortfall; split meaningful inhabited regions while preserving approved Mindanao and reef unions.
2. China and Syria: major economic/administrative regions and recognizable governorate names.
3. Taiwan, India, Pakistan, Morocco and Colombia: prioritize inhabited regions and poorly named mixed unions.
4. Remaining countries: review the complete country table, ownership differences and approved mergers before changing geography.

Counts are targets, not instructions to copy MD polygon geometry. Each approved split should reuse current province footprints where appropriate, preserve country totals, update capitals and references, and pass the shared map build.

## Regional candidates and constraints

### Philippines

Prioritize Metro Manila, Cordillera, Ilocos, Cagayan, Bicol, Calabarzon, Central Visayas, Mindoro, Palawan, Caraga, Davao and Bangsamoro. Respect the approved Western/Northern Mindanao union; omit reef-only replacements. Check actual source geometry before deciding twelve additions.

Current: Central Luzon; Eastern Visayas; Mimaropa; Northern Luzon; Northern Mindanao; Southern Luzon; Southern Mindanao; Western Visayas.

MD reference: Cordillera; Ilocos; Central Luzon; Metro Manila; Bicol; Eastern Visayas; Western Visayas; Mindoro; Caraga; Southern Mindanao; Northern Mindanao; Zamboanga; Sulu Archipelago; Cagayan; Calabarzon; Central Visayas; Bangsamoro; Davao; Palawan; Eastern Spratlys.

### China

Review Pearl River Delta, Nanjing, Liaoxi, Songjiang, Hulunbuir, Shandong Peninsula, Northern Hebei and Western Sichuan as candidate population/economic regions. Preserve current country control and approved Xinjiang/Tibet unions.

Current: Aksai Chin; Anhui; Beijing; Chongqing; Demchok; Fujian; Gansu; Guangdong — North; Guangxi; Guizhou; Hainan; Hebei; Heilongjiang; Henan; Hubei; Hunan; Inner Mongolia; Jiangsu; Jiangxi; Jilin; Liaoning; Ningxia; Paracel Islands; Qinghai; Shaanxi; Shaksgam Valley; Shandong; Shanghai; Shanxi; Sichuan; Tianjin; Tibet; Xinjiang; Yunnan; Zhejiang.

MD reference: Ningxia; Liaoxi; Songjiang; Hulunbuir; Northern Hebei; Shandong Peninsula; Northern Spratlys; Hainan; Pearl River Delta; Guangdong; Nanjing; Fujian; Zhejiang; Shanghai; Jiangsu; Shandong; Beijing; Tianjin; Hebei; Liaoning; Jilin; Heilongjiang; Inner Mongolia; Shanxi; Shaanxi; Gansu; Jiangxi; Anhui; Henan; Hubei; Hunan; Guangxi; Yunnan; Guizhou; Chongqing; Western Sichuan; Sichuan; Qinghai; Xizang; Aksai Chin; Xinjiang; Paracel Islands; Macclesfield Bank.

### Syria

Use governorate/settlement regions around Aleppo, Idlib, Hama, Homs, Latakia, Daraa and As-Suwayda to replace broad unions; validate the footprint rather than copying MD straight boundaries.

Current: Central Syria; Damascus; Deir ez-Zor; Jazira; Northern Syria; Raqqa; Southern Syria; Syrian Coast.

MD reference: Daraa; Al-Suwayda; Damascus; Homs; Latakia; Idlib; North Raqqa; South Deir ez-Zor; Al-Hasakah; Central Desert; Aleppo; Hama; Azaz; South Raqqa; North Deir ez-Zor.

### Micronesia

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Micronesia.

MD reference: Phoenix Islands; Nauru; Gilbert Islands; Line Islands; Palau; Marshall Islands; Caroline Islands.

User explicitly requires ONE Micronesia state including Palau; do not split it to meet raw MD count.

### India

Prioritize missing Awadh/Purvanchal and important urban/economic regions such as Mumbai/Vidarbha/Rayalaseema. Keep user-approved Karnataka, Chandigarh and other mergers.

Current: Andaman and Nicobar Islands; Andhra Pradesh; Arunachal Pradesh — Arunachal Pradesh; Arunachal Pradesh — South; Assam — Arunachal Pradesh; Assam — South; Bara Hotii Valleys; Bihar; Braj; Chhattisgarh; Delhi; Goa; Gujarat; Haryana; Himachal Pradesh — South; Jammu and Kashmir; Jharkhand; Junagadh and Manavadar; Karnataka; Kerala; Ladakh; Madhya Pradesh; Maharashtra; Manipur; Meghalaya; Mizoram; Nagaland; Near Om Parvat; Odisha; Puducherry; Punjab — South; Rajasthan; Siachen Glacier; Sikkim; Tamil Nadu; Telangana; Tripura; Uttarakhand — South; Uttarakhand — Tirpani Valleys; West Bengal.

MD reference: Uttarakhand; Jammu and Kashmir; Himachal; Eastern Punjab; Haryana; East Rajasthan; East Gujarat; West Madhya Pradesh; Braj; Awadh; Purvanchal; Bihar; Jharkhand; West Bengal; Gorkhaland; South Odisha; Telangana; South Chhattisgarh; South Andhra Pradesh; Rayalaseema; Tamil Nadu; Kongu Nadu; Kerala; South Karnataka; Maharashtra; Vidarbha; Mumbai; Assam; Arunachal Pradesh; Nagaland; Manipur; Mizoram; Andaman and Nicobar; Meghalya; Tripura; Sikkim; West Rajasthan; South Madhya Pradesh; East Madhya Pradesh; West Gujarat; North Karnataka; North Odisha; North Andhra Pradesh; North Chhattisgarh; Ladakh.

### Republic of China

Review Taipei, Hsinchu, Taichung, Tainan, Kaohsiung and Hualien as inhabited mainland subdivisions, with Lienchiang considered from existing geography. Do not recreate Pratas or other reef-only states.

Current: Central Taiwan; Eastern Taiwan; Kinmen; Northern Taiwan; Penghu; Southern Taiwan.

MD reference: Pratas Islands; Lienchiang; Hsinchu; Taichung; Tainan; Penghu; Kinmen; Taiping Island; Taipei; Kaohsiung; Hualian.

Keep Pratas/Spratly consolidations; add useful inhabited subdivisions instead of recreating reef states.

### Morocco

Review Fes-Meknes, Rabat-Sale-Kenitra, Tanger-Tetouan-Al Hoceima, Marrakesh-Safi and Draa-Tafilalet. Current slash-separated unions need geographic validation before naming or division.

Current: Casablanca-Settat; Guelmim-Es Semara; Guelmim-Es Semara / Laâyoune-Boujdour-Sakia El Hamra; Meknès-Tafilalet / Rabat-Salé-Zemmour-Zaër; Oriental / Taza-Al Hoceïma-Taounate; Suss-Massa-Draa; W. Sahara.

MD reference: Oriental; Fes-Meknes; Rabat-Sale-Kenitra; Beni Mellal-Khenifra; Guelmim-Oued Noun; West-Sahara; Tanger-Tetouan-Al Hoceima; Marrakesh-Safi; Draa-Tafilalet; Casablanca-Settat; Souss-Massa.

### Pakistan

Review Malakand, northern/central/southern Punjab and the Pashto-speaking Balochistan region. Check tribal-area overlaps to avoid duplicates.

Current: Azad Kashmir; Balochistan; Gilgit-Baltistan; Islamabad Capital Territory; Khyber Pakhtunkhwa — South; Pashto Tribal Areas; Punjab — South; Sindh.

MD reference: Malakand; Balochistan; Pashto Balochistan; Khyber Pakhtunkhwa; Pashto Tribal Areas; Azad Kashmir; Gilgit-Baltistan; Northern Punjab; Sindh; Central Punjab; Southern Punjab; Tribal Areas.

### Colombia

Review Pacifico, Caribe, Antioquia, Santander and Amazonia against current mixed departmental unions; retain removed island states as removed.

Current: Amazonas / Cauca; Cundinamarca; Magdalena / Santander; Orinoquía; Tolima / Antioquia.

MD reference: Pacifico; Caribe; Colombian Andes; Amazonia; Cundinamarca; Antioquia; Santander; Orinoquía.

### Georgia

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Eastern Georgia; Western Georgia.

MD reference: Djavakheti; Adjara; Western Georgia; Eastern Georgia.

### Somaliland

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Somaliland.

MD reference: Somaliland; Awdal; Khatumo.

### United States

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Alabama; Alaska; American Samoa; Arizona; Arkansas; California; Colorado; Connecticut; Delaware; Diego Garcia; Florida; Georgia; Guam; Guantanamo Bay; Hawaii; Hawally; Idaho; Illinois; Indiana; Iowa; Kansas; Kentucky; Kiribati / Hawaii; Louisiana; Maine; Mariana Islands; Maryland; Massachusetts; Michigan; Minnesota; Mississippi; Missouri; Montana; NSA Bahrain; Nebraska; Nevada; New Hampshire; New Jersey; New Mexico; New York; North Carolina; North Dakota; Ohio; Oklahoma; Oregon; Pennsylvania; Puerto Rico; Rhode Island; South Carolina; South Dakota; Tennessee; Texas; United States Virgin Islands; Utah; Vermont; Virginia; Wake Island; Washington; Washington, D.C.; West Virginia; Wisconsin; Wyoming.

MD reference: Attu Island; Delaware; Rhode Island; Washington, D.C.; United States Virgin Islands; Guantanamo Bay; Kuwait Naval Base; NSA Bahrain; Maine; New Hampshire; Vermont; Massachusetts; Connecticut; New York; New Jersey; Pennsylvania; Maryland; Virginia; West Virginia; Ohio; Indiana; Michigan; Illinois; Wisconsin; Minnesota; Iowa; Kentucky; Missouri; Kansas; Nebraska; South Dakota; North Dakota; Montana; Wyoming; North Carolina; South Carolina; Georgia; Tennessee; Alabama; Florida; Mississippi; Louisiana; Arkansas; Oklahoma; Texas; New Mexico; Colorado; Utah; Arizona; Nevada; Idaho; Washington; Oregon; California; Alaska; Puerto Rico; Hawaii; Mariana Islands; Midway Atoll; Wake Island; Diego Garcia; Johnston Atoll; American Samoa; Okinawa Base.

Keep Rota/Saipan/Tinian in Mariana Islands, Midway/Johnston in Hawaii, and Navassa removed. Any additional states must represent meaningful inhabited regions.

### Afghanistan

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Badakhshan / Takhar; Ghazni / Baghlan.

MD reference: Nuristan; Kunar; Badakhshan.

### Angola

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Bié / Cuanza Sul; Cabinda.

MD reference: Cabinda; Luanda; Benguela.

### Argentina

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Cuyo; Gran Chaco; Noroeste; Pampas; Patagonia; Santa Fe / Córdoba; Tierra del Fuego.

MD reference: Cuyo; Noroeste; Mesopotamia; Gran Chaco; Cordoba; Pampas; Patagonia; Tierra del Fuego.

### Azerbaijan

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Ganja; Lerik / Baku; Lezgistan; Nakhchivan.

MD reference: Shirvan; Lezgistan; Nakhchivan; Ganja; Baku.

### Bhutan

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Bhutan.

MD reference: Bhutan; Drangme.

### Bosnia

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Brčko District; Federation — Bosnia; Federation — Herzegovina; Federation — Posavina; Republika Srpska.

MD reference: Unsko-sanski; Hercegovina; Brcko; West Srpska; Bosnia; East Srpska.

### Chile

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Antofagasta / Tarapacá; Atacama; Central Chile — South; Isla de Pascua; Southern Chile.

MD reference: Southern Chile; Central Chile; Atacama; Isla de Pascua; Tarapaca; Arica.

### Comoros

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Comoros.

MD reference: Anjouan; Comoros.

### Costa Rica

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Costa Rica.

MD reference: Puntarenas-San José; Northern Costa Rica.

### El Salvador

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: El Salvador.

MD reference: San Salvador; East Salvador.

### Germany

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Baden-Württemberg; Bayern; Berlin; Brandenburg; Franken; Hamburg; Hesse; Lower Saxony; Mecklenburg-Western Pomerania; North Rhine-Westphalia; Rhineland-Palatinate; Saarland; Saxony; Saxony-Anhalt; Schleswig-Holstein; Thuringia.

MD reference: Brandenburg; Hamburg; Schleswig-Holstein; Niedersachsen; Nordrhein-Westfalen; Rheinland-Pfalz; Hessen; Baden-Württemberg; Bayern; Sachsen; Berlin; Mecklenburg-Vorpommern; Thüringen; Franken; Koln-Bonn; Saarland; Sachsen-Anhalt.

Keep Free Hanseatic Bremen integrated as requested.

### Greenland

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Northeast Greenland National Park; Qaasuitsup / Pituffik; Sermersooq / Qeqqata.

MD reference: Central Plateau; Kitaa; Tunu; Southern Interior.

Keep Hans Island integrated and earlier user-approved Greenland unions.

### Indonesia

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Bangka Belitung Islands; Central Sulawesi / South Sulawesi; Central Sumatra; Central–South Kalimantan; East Java / Central Java; East Kalimantan; East Nusa Tenggara / Viqueque; Maluku; North Maluku; North Sumatra; Riau Islands; South Sumatra–Lampung; West Kalimantan; West Nusa Tenggara; West Papua; Western Java.

MD reference: Banten; Central Java; West Timor; Timor Leste; Northern Sumatra; Riau Islands; Southern Sumatra; Western Java; Eastern Java; Lesser Sunda Islands; Moluccas; North Moluccas; West Papua; Sulawesi; Kalimantan; Loro Munu; Natuna Islands.

### Madagascar

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Antananarivo / Antananarivo; Mahajanga — South; Toliara.

MD reference: Mahajanga; Antananarivo; Toliara; Toamasina.

### Moldova

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Chișinău–Bălți; Gagauzia.

MD reference: Chisinau; Balti; Gagauzia.

### New Zealand

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Niue / Tokelau; North Island; Rarotonga / Cook Islands; South Island.

MD reference: Tokelau; Niue; Cook Islands; North Island; South Island.

Keep one South Island state and the approved island unions.

### Papua New Guinea

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Bismarck Archipelago; Bougainville; Northern Papua; Southern Papua.

MD reference: South Papua; Papuan Highlands; North Papua; Bismarck Archipelago; Bougainville.

User explicitly requires FOUR states after mainland mergers: Southern Papua, Northern Papua, Bismarck Archipelago and Bougainville.

### Serbia

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Central Serbia; Eastern Serbia; South Bačka / Central Banat.

MD reference: Vojvodina; Central Serbia; Eastern Serbia; Western Banat.

### Solomon Islands

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Solomon Islands.

MD reference: Guadalcanal; Solomon Islands.

### Spain

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Andalusia; Aragon; Asturias; Balearic Islands; Basque Country; Canary Islands; Cantabria; Castile and León; Castilla-La Mancha; Catalonia; Ceuta; Extremadura; Galicia; La Rioja; Madrid; Melilla; Murcia; Navarre; Valencia.

MD reference: Cantabria; Navarre; La Rioja; Ceuta; Melilla; Catalunya; Aragon; Basque; Asturias; Castilla; Madrid; Valencia; Andalusia; Baleares; Galicia; Canary Islands; Extremadura; Murcia; Castilla-La Mancha; León.

Keep approved tiny enclave/island unions; consider meaningful mainland regions.

### United Kingdom

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Akrotiri; Anguilla; Ascension; Bermuda; British Indian Ocean Territory; British Virgin Islands; Cayman Islands; Channel Islands; Devon and Cornwall; East Anglia; East Midlands; Eastern Scotland; Falkland Islands; Gibraltar; Greater London; Montserrat; Northeast England; Northeast Scotland; Northern Ireland; Northwest England; Orkney Islands; Outer Hebrides; Pitcairn Islands; Saint Helena; Scottish Highlands; Shetland Islands; South Georgia and the South Sandwich Islands; Southeast England; Southwest England; Southwest Scotland; Turks and Caicos; Wales; West Midlands; Yorkshire.

MD reference: Yorkshire; Cayman Islands; Turks and Caicos; Greater Manchester; Orkney; East Midlands; North Wales; Northern England; Scottish Borders; Aberdeenshire; Outer Hebrides; Channel Islands; West Midlands; Montserrat; British Virgin Islands; Tristan Da Cunha; Greater London; East of England; Southern England; South Wales; Ulster; Pitcairn Islands; Gibraltar; Bermuda; South Georgia Islands; Anguilla; Saint Helena; Ascension; Falkland Islands; Highlands; Shetland; RAF Akrotiri; Central Belt; Isle of Man; Cornwall.

Keep Rockall integrated as requested.

### Wa State

Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.

Current: Shan State / Chiang Mai.

MD reference: Wa; South Wa.

Keep the approved Yunnan/Wa State consolidation.

## Naming review

225 names are flagged for review. A directional name is not automatically wrong. These are proposals for a separate geography/name pass; no blanket automatic renaming was applied.

| Country | State ID | Current name | Review reason |
| --- | ---: | --- | --- |
| Afghanistan | 3 | Badakhshan / Takhar | joined names; review for a coherent regional label |
| Afghanistan | 5 | Ghazni / Baghlan | joined names; review for a coherent regional label |
| Albania | 12 | Northern Albania | directional regional name; acceptable when the footprint is broad |
| Albania | 11 | Southern Albania | directional regional name; acceptable when the footprint is broad |
| Angola | 9 | Bié / Cuanza Sul | joined names; review for a coherent regional label |
| Argentina | 32 | Santa Fe / Córdoba | joined names; review for a coherent regional label |
| Artsakh | 739 | Kalbajar / Khojavend | joined names; review for a coherent regional label |
| Austria | 1772 | Western Austria | directional regional name; acceptable when the footprint is broad |
| Azerbaijan | 56 | Lerik / Baku | joined names; review for a coherent regional label |
| Bangladesh | 63 | Northern Bangladesh | directional regional name; acceptable when the footprint is broad |
| Benin | 70 | Northern Benin | directional regional name; acceptable when the footprint is broad |
| Botswana | 99 | Central Botswana | directional regional name; acceptable when the footprint is broad |
| Brazil | 120 | Espírito Santo — North | directional regional name; acceptable when the footprint is broad |
| Brazil | 114 | Rio Grande do Norte — South | directional regional name; acceptable when the footprint is broad |
| Bulgaria | 1429 | Northern Bulgaria | directional regional name; acceptable when the footprint is broad |
| Bulgaria | 1428 | South Dobruja | directional regional name; acceptable when the footprint is broad |
| Bulgaria | 1426 | Southern Bulgaria | directional regional name; acceptable when the footprint is broad |
| Bulgaria | 1427 | Western Bulgaria | directional regional name; acceptable when the footprint is broad |
| Burundi | 143 | Gitega / Kirundo | joined names; review for a coherent regional label |
| Cambodia | 165 | Eastern Cambodia | directional regional name; acceptable when the footprint is broad |
| Cambodia | 167 | Northern Khmer | directional regional name; acceptable when the footprint is broad |
| Cambodia | 168 | Southern Khmer | directional regional name; acceptable when the footprint is broad |
| Cameroon | 144 | Northern Cameroon | directional regional name; acceptable when the footprint is broad |
| Cameroon | 146 | Southeastern Cameroon | directional regional name; acceptable when the footprint is broad |
| Canada | 155 | Nunavut — North | directional regional name; acceptable when the footprint is broad |
| Chile | 225 | Antofagasta / Tarapacá | joined names; review for a coherent regional label |
| Chile | 228 | Central Chile — South | directional regional name; acceptable when the footprint is broad |
| Chile | 229 | Southern Chile | directional regional name; acceptable when the footprint is broad |
| China | 187 | Guangdong — North | directional regional name; acceptable when the footprint is broad |
| Colombia | 234 | Amazonas / Cauca | joined names; review for a coherent regional label |
| Colombia | 236 | Magdalena / Santander | joined names; review for a coherent regional label |
| Colombia | 240 | Tolima / Antioquia | joined names; review for a coherent regional label |
| Congo DR | 269 | Bandundu / Lunda Norte | joined names; review for a coherent regional label |
| Croatia | 1774 | Northern Croatia | directional regional name; acceptable when the footprint is broad |
| Cuba | 1433 | Central Cuba | directional regional name; acceptable when the footprint is broad |
| Cuba | 1432 | Eastern Cuba | directional regional name; acceptable when the footprint is broad |
| Cuba | 1434 | Western Cuba | directional regional name; acceptable when the footprint is broad |
| Czech Republic | 258 | Central Bohemia–Vysočina | directional regional name; acceptable when the footprint is broad |
| Czech Republic | 256 | Northeastern Bohemia | directional regional name; acceptable when the footprint is broad |
| Czech Republic | 255 | Western and Southern Bohemia | directional regional name; acceptable when the footprint is broad |
| Egypt | 1446 | Eastern Delta | directional regional name; acceptable when the footprint is broad |
| Egypt | 1447 | Western Delta | directional regional name; acceptable when the footprint is broad |
| Equatorial Guinea | 284 | Centro Sur / Wele-Nzas | joined names; review for a coherent regional label |
| Eritrea | 1491 | Eastern Eritrea | directional regional name; acceptable when the footprint is broad |
| Eritrea | 1492 | Western Eritrea | directional regional name; acceptable when the footprint is broad |
| Estonia | 347 | Eastern Estonia | directional regional name; acceptable when the footprint is broad |
| Estonia | 345 | Southern Estonia | directional regional name; acceptable when the footprint is broad |
| Ethiopia | 356 | Oromia / Addis Ababa | joined names; review for a coherent regional label |
| Ethiopia | 350 | Somali / Dire Dawa | joined names; review for a coherent regional label |
| Finland | 361 | Kainuu–Northern Ostrobothnia | directional regional name; acceptable when the footprint is broad |
| Finland | 1826 | Southwest Finland | directional regional name; acceptable when the footprint is broad |
| Gabon | 1536 | Eastern Gabon | directional regional name; acceptable when the footprint is broad |
| Gabon | 1537 | Western Gabon | directional regional name; acceptable when the footprint is broad |
| Georgia | 1786 | Eastern Georgia | directional regional name; acceptable when the footprint is broad |
| Georgia | 1785 | Western Georgia | directional regional name; acceptable when the footprint is broad |
| Greece | 436 | Centre Macedonia / Mount Athos | joined names; review for a coherent regional label |
| Greenland | 447 | Qaasuitsup / Pituffik | joined names; review for a coherent regional label |
| Greenland | 445 | Sermersooq / Qeqqata | joined names; review for a coherent regional label |
| Guatemala | 1538 | Southern Guatemala | directional regional name; acceptable when the footprint is broad |
| Guyana | 457 | West of Essequibo River | directional regional name; acceptable when the footprint is broad |
| Hezbollah | 461 | South Lebanon | directional regional name; acceptable when the footprint is broad |
| Honduras | 1547 | Eastern Honduras | directional regional name; acceptable when the footprint is broad |
| Honduras | 1546 | Western Honduras | directional regional name; acceptable when the footprint is broad |
| Hungary | 475 | Northern Great Plain | directional regional name; acceptable when the footprint is broad |
| Hungary | 476 | Northern Hungary | directional regional name; acceptable when the footprint is broad |
| Hungary | 474 | Southern Great Plain | directional regional name; acceptable when the footprint is broad |
| India | 923 | Arunachal Pradesh — Arunachal Pradesh | repeated administrative name |
| India | 880 | Arunachal Pradesh — South | directional regional name; acceptable when the footprint is broad |
| India | 883 | Assam — South | directional regional name; acceptable when the footprint is broad |
| India | 894 | Himachal Pradesh — South | directional regional name; acceptable when the footprint is broad |
| India | 925 | Near Om Parvat | descriptive placeholder; verify local toponym |
| India | 891 | Punjab — South | directional regional name; acceptable when the footprint is broad |
| India | 884 | Uttarakhand — South | directional regional name; acceptable when the footprint is broad |
| Indonesia | 484 | Central Sulawesi / South Sulawesi | directional regional name; acceptable when the footprint is broad; joined names; review for a coherent regional label |
| Indonesia | 486 | Central Sumatra | directional regional name; acceptable when the footprint is broad |
| Indonesia | 1807 | Central–South Kalimantan | directional regional name; acceptable when the footprint is broad |
| Indonesia | 481 | East Java / Central Java | directional regional name; acceptable when the footprint is broad; joined names; review for a coherent regional label |
| Indonesia | 479 | East Nusa Tenggara / Viqueque | directional regional name; acceptable when the footprint is broad; joined names; review for a coherent regional label |
| Indonesia | 1813 | North Sumatra | directional regional name; acceptable when the footprint is broad |
| Indonesia | 487 | South Sumatra–Lampung | directional regional name; acceptable when the footprint is broad |
| Indonesia | 1827 | Western Java | directional regional name; acceptable when the footprint is broad |
| Iran | 788 | Khoy — North | directional regional name; acceptable when the footprint is broad |
| Iran | 787 | Khoy — South | directional regional name; acceptable when the footprint is broad |
| Iran | 798 | Sistan and Baluchestan / Nimruz | joined names; review for a coherent regional label |
| Islamic Emirate of Afghanistan | 1189 | Paktika / Ghazni | joined names; review for a coherent regional label |
| Italy | 538 | Sardinia — North | directional regional name; acceptable when the footprint is broad |
| Italy | 539 | Sardinia — South | directional regional name; acceptable when the footprint is broad |
| Italy | 536 | Sicilia — North | directional regional name; acceptable when the footprint is broad |
| Italy | 537 | Sicilia — South | directional regional name; acceptable when the footprint is broad |
| Italy | 535 | Toscana — North | directional regional name; acceptable when the footprint is broad |
| Italy | 544 | Toscana — South | directional regional name; acceptable when the footprint is broad |
| Japan | 1555 | Northern Kyushu | directional regional name; acceptable when the footprint is broad |
| Japan | 1562 | Northern Tohoku | directional regional name; acceptable when the footprint is broad |
| Japan | 1554 | Southern Kyushu | directional regional name; acceptable when the footprint is broad |
| Japan | 1561 | Southern Tohoku | directional regional name; acceptable when the footprint is broad |
| Kazakhstan | 571 | Akmola–Kostanay–North Kazakhstan | directional regional name; acceptable when the footprint is broad |
| Kenya | 578 | Eastern Kenya | directional regional name; acceptable when the footprint is broad |
| Kenya | 576 | Rift Valley / Central | directional regional name; acceptable when the footprint is broad; joined names; review for a coherent regional label |
| Kyrgyzstan | 594 | Naryn / Issyk-Kul | joined names; review for a coherent regional label |
| Laos | 599 | Northern Laos | directional regional name; acceptable when the footprint is broad |
| Laos | 598 | Southern Laos | directional regional name; acceptable when the footprint is broad |
| Lebanon | 622 | Beqaa / Nabatieh | joined names; review for a coherent regional label |
| Liberia | 626 | Eastern Liberia | directional regional name; acceptable when the footprint is broad |
| Macedonia | 404 | Eastern Macedonia | directional regional name; acceptable when the footprint is broad |
| Macedonia | 405 | Western Macedonia | directional regional name; acceptable when the footprint is broad |
| Madagascar | 636 | Antananarivo / Antananarivo | joined names; review for a coherent regional label |
| Madagascar | 634 | Mahajanga — South | directional regional name; acceptable when the footprint is broad |
| Malawi | 688 | North Malawi | directional regional name; acceptable when the footprint is broad |
| Malawi | 689 | South Malawi | directional regional name; acceptable when the footprint is broad |
| Malaysia | 656 | Eastern Malaya | directional regional name; acceptable when the footprint is broad |
| Malaysia | 657 | North Borneo | directional regional name; acceptable when the footprint is broad |
| Malaysia | 651 | Sabah / Labuan | joined names; review for a coherent regional label |
| Malaysia | 654 | Selangor / Kuala Lumpur | joined names; review for a coherent regional label |
| Malaysia | 652 | Western Malaya | directional regional name; acceptable when the footprint is broad |
| Maoist Nepal | 742 | Western Nepal | directional regional name; acceptable when the footprint is broad |
| Mexico | 668 | Oaxaca / Hidalgo | joined names; review for a coherent regional label |
| Mexico | 663 | Yucatan — South | directional regional name; acceptable when the footprint is broad |
| Mongolia | 691 | Eastern Mongolia | directional regional name; acceptable when the footprint is broad |
| Mongolia | 692 | Western Mongolia | directional regional name; acceptable when the footprint is broad |
| Morocco | 693 | Guelmim-Es Semara / Laâyoune-Boujdour-Sakia El Hamra | joined names; review for a coherent regional label |
| Morocco | 695 | Meknès-Tafilalet / Rabat-Salé-Zemmour-Zaër | joined names; review for a coherent regional label |
| Morocco | 694 | Oriental / Taza-Al Hoceïma-Taounate | joined names; review for a coherent regional label |
| Mozambique | 711 | East Niassa | directional regional name; acceptable when the footprint is broad |
| Myanmar | 132 | North Shan | directional regional name; acceptable when the footprint is broad |
| Nepal | 717 | Eastern Nepal | directional regional name; acceptable when the footprint is broad |
| Netherlands | 1541 | Eastern Netherlands | directional regional name; acceptable when the footprint is broad |
| Netherlands | 1540 | Northern Netherlands | directional regional name; acceptable when the footprint is broad |
| Netherlands | 1542 | Southern Netherlands | directional regional name; acceptable when the footprint is broad |
| Netherlands | 1543 | Western Netherlands | directional regional name; acceptable when the footprint is broad |
| New Zealand | 751 | Niue / Tokelau | joined names; review for a coherent regional label |
| New Zealand | 750 | Rarotonga / Cook Islands | joined names; review for a coherent regional label |
| Norway | 1595 | Eastern Norway | directional regional name; acceptable when the footprint is broad |
| Norway | 1592 | Northern Norway | directional regional name; acceptable when the footprint is broad |
| Norway | 1596 | Southern Norway | directional regional name; acceptable when the footprint is broad |
| Norway | 1597 | Western Norway | directional regional name; acceptable when the footprint is broad |
| Pakistan | 761 | Khyber Pakhtunkhwa — South | directional regional name; acceptable when the footprint is broad |
| Pakistan | 764 | Punjab — South | directional regional name; acceptable when the footprint is broad |
| Papua New Guinea | 1602 | Northern Papua | directional regional name; acceptable when the footprint is broad |
| Papua New Guinea | 1603 | Southern Papua | directional regional name; acceptable when the footprint is broad |
| Peru | 873 | Coastal Peru — North | directional regional name; acceptable when the footprint is broad |
| Peru | 872 | Coastal Peru — South | directional regional name; acceptable when the footprint is broad |
| Peru | 869 | Northern Peru | directional regional name; acceptable when the footprint is broad |
| Philippines | 1792 | Central Luzon | directional regional name; acceptable when the footprint is broad |
| Philippines | 1791 | Eastern Visayas | directional regional name; acceptable when the footprint is broad |
| Philippines | 1794 | Northern Luzon | directional regional name; acceptable when the footprint is broad |
| Philippines | 1790 | Northern Mindanao | directional regional name; acceptable when the footprint is broad |
| Philippines | 1793 | Southern Luzon | directional regional name; acceptable when the footprint is broad |
| Philippines | 1788 | Southern Mindanao | directional regional name; acceptable when the footprint is broad |
| Philippines | 1795 | Western Visayas | directional regional name; acceptable when the footprint is broad |
| Portugal | 865 | Madeira — North | directional regional name; acceptable when the footprint is broad |
| Republic of China | 1648 | Central Taiwan | directional regional name; acceptable when the footprint is broad |
| Republic of China | 1650 | Eastern Taiwan | directional regional name; acceptable when the footprint is broad |
| Republic of China | 1647 | Northern Taiwan | directional regional name; acceptable when the footprint is broad |
| Republic of China | 1649 | Southern Taiwan | directional regional name; acceptable when the footprint is broad |
| Romania | 1607 | Northern Transylvania | directional regional name; acceptable when the footprint is broad |
| Romania | 1613 | Southern Transylvania | directional regional name; acceptable when the footprint is broad |
| Russia | 1824 | North Kuril Islands | directional regional name; acceptable when the footprint is broad |
| Russia | 1086 | South Kuril Islands | directional regional name; acceptable when the footprint is broad |
| Senegal | 967 | Fatick / Thiès | joined names; review for a coherent regional label |
| Serbia | 970 | Central Serbia | directional regional name; acceptable when the footprint is broad |
| Serbia | 969 | Eastern Serbia | directional regional name; acceptable when the footprint is broad |
| Serbia | 971 | South Bačka / Central Banat | directional regional name; acceptable when the footprint is broad; joined names; review for a coherent regional label |
| Somali National Alliance | 991 | Dhobley — North | directional regional name; acceptable when the footprint is broad |
| Somali National Alliance | 992 | Dhobley — South | directional regional name; acceptable when the footprint is broad |
| Somali National Alliance | 993 | Lower Shebelle / Bay | joined names; review for a coherent regional label |
| Somalia | 997 | Central Somalia | directional regional name; acceptable when the footprint is broad |
| South Shan State | 975 | South Shan | directional regional name; acceptable when the footprint is broad |
| Southwestern State of Somalia | 1151 | South West State | directional regional name; acceptable when the footprint is broad |
| Sri Lanka | 1112 | Central Sri Lanka | directional regional name; acceptable when the footprint is broad |
| Sudan | 1133 | Abyei — Abyei | repeated administrative name |
| Sudan | 1131 | Abyei — North | directional regional name; acceptable when the footprint is broad |
| Switzerland | 1148 | Zürich–Eastern Switzerland | directional regional name; acceptable when the footprint is broad |
| Syria | 1798 | Central Syria | directional regional name; acceptable when the footprint is broad |
| Syria | 1803 | Northern Syria | directional regional name; acceptable when the footprint is broad |
| Syria | 1797 | Southern Syria | directional regional name; acceptable when the footprint is broad |
| Tanzania | 1205 | Central Tanzania | directional regional name; acceptable when the footprint is broad |
| Tanzania | 1207 | Kilimanjaro — North | directional regional name; acceptable when the footprint is broad |
| Tanzania | 1200 | Kilimanjaro — South | directional regional name; acceptable when the footprint is broad |
| Tanzania | 1208 | Northwest Tanzania | directional regional name; acceptable when the footprint is broad |
| Tanzania | 1206 | Western Tanzania | directional regional name; acceptable when the footprint is broad |
| Thailand | 978 | Central Thailand | directional regional name; acceptable when the footprint is broad |
| Thailand | 977 | Northern Thailand — North | directional regional name; acceptable when the footprint is broad |
| Thailand | 981 | Northern Thailand — South | directional regional name; acceptable when the footprint is broad |
| Thailand | 979 | Southern Thailand | directional regional name; acceptable when the footprint is broad |
| Togo | 1209 | Northern Togo | directional regional name; acceptable when the footprint is broad |
| Tunisia | 1217 | Central Tunisia | directional regional name; acceptable when the footprint is broad |
| Turkey | 1668 | South Aegean | directional regional name; acceptable when the footprint is broad |
| UNITA | 1279 | Moxico / Cuando Cubango | joined names; review for a coherent regional label |
| Uganda | 1242 | Apac / Kaabong | joined names; review for a coherent regional label |
| Uganda | 1244 | Central Uganda | directional regional name; acceptable when the footprint is broad |
| Uganda | 1245 | Eastern Uganda | directional regional name; acceptable when the footprint is broad |
| Uganda | 1243 | Western Uganda | directional regional name; acceptable when the footprint is broad |
| Ukraine | 1261 | Northern Donetsk | directional regional name; acceptable when the footprint is broad |
| Ukraine | 1260 | Northern Luhansk | directional regional name; acceptable when the footprint is broad |
| Ukraine | 1276 | Southern Donetsk | directional regional name; acceptable when the footprint is broad |
| Ukraine | 1274 | Southern Luhansk | directional regional name; acceptable when the footprint is broad |
| United Kingdom | 1463 | East Anglia | directional regional name; acceptable when the footprint is broad |
| United Kingdom | 1462 | East Midlands | directional regional name; acceptable when the footprint is broad |
| United Kingdom | 1458 | Eastern Scotland | directional regional name; acceptable when the footprint is broad |
| United Kingdom | 1459 | Northeast England | directional regional name; acceptable when the footprint is broad |
| United Kingdom | 1468 | Northeast Scotland | directional regional name; acceptable when the footprint is broad |
| United Kingdom | 1453 | Northern Ireland | directional regional name; acceptable when the footprint is broad |
| United Kingdom | 1455 | Northwest England | directional regional name; acceptable when the footprint is broad |
| United Kingdom | 1487 | South Georgia and the South Sandwich Islands | directional regional name; acceptable when the footprint is broad |
| United Kingdom | 1464 | Southeast England | directional regional name; acceptable when the footprint is broad |
| United Kingdom | 1457 | Southwest England | directional regional name; acceptable when the footprint is broad |
| United Kingdom | 1460 | Southwest Scotland | directional regional name; acceptable when the footprint is broad |
| United Kingdom | 1456 | West Midlands | directional regional name; acceptable when the footprint is broad |
| United States | 1727 | Kiribati / Hawaii | joined names; review for a coherent regional label |
| Uruguay | 1777 | Northern Uruguay | directional regional name; acceptable when the footprint is broad |
| Uruguay | 1778 | Southern Uruguay | directional regional name; acceptable when the footprint is broad |
| Uzbekistan | 1363 | Navoiy / Bukhara | joined names; review for a coherent regional label |
| Venezuela | 1783 | Central Venezuela | directional regional name; acceptable when the footprint is broad |
| Venezuela | 1779 | Eastern Venezuela | directional regional name; acceptable when the footprint is broad |
| Venezuela | 1782 | Western Venezuela | directional regional name; acceptable when the footprint is broad |
| Vietnam | 1375 | Central Vietnam | directional regional name; acceptable when the footprint is broad |
| Vietnam | 1377 | Northern Vietnam | directional regional name; acceptable when the footprint is broad |
| Vietnam | 1374 | Northwest Vietnam | directional regional name; acceptable when the footprint is broad |
| Vietnam | 1379 | Southern Vietnam | directional regional name; acceptable when the footprint is broad |
| Vietnam | 1376 | Vietnamese Highlands — North | directional regional name; acceptable when the footprint is broad |
| Vietnam | 1381 | Vietnamese Highlands — South | directional regional name; acceptable when the footprint is broad |
| Vietnam | 1378 | Western Spratlys | directional regional name; acceptable when the footprint is broad |
| Wa State | 1383 | Shan State / Chiang Mai | joined names; review for a coherent regional label |
| Zambia | 1399 | Eastern Zambia | directional regional name; acceptable when the footprint is broad |
| Zambia | 1401 | Western Zambia | directional regional name; acceptable when the footprint is broad |
