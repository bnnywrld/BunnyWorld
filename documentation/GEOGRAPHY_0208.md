# BunnyWorld 0.2.0.8 — authored geography corrections

This source patch applies the user's complete October 15 geography checklist to
commit f9de969716ff5430aaad8eecadae70ba357aba77 (0.2.0.7).
It requires a fresh campaign. It includes no Windows executable export.

## Corrections

| Area | Result |
|---|---|
| France | MD-scale mainland regions selected by department identity; Andorra and Monaco retained as separate scenario states. Overseas territories have an independent allocation. Mayotte, New Caledonia, French Guiana, French Polynesia, Wallis and Futuna and Saint Pierre and Miquelon consolidated by territory. Lawa Headwaters integrated into French Guiana. Scattered Islands grouped. |
| Netherlands | Four mainland regions; Aruba/Curaçao/Bonaire combined; Caribbean dependencies separate from the mainland allocation. |
| Japan | Kanto includes Tokyo, Kanagawa, Gunma and Saitama. Kansai/Chugoku/Kyushu corrected by prefecture identity. Chubu divided into Hokuriku, Koshinetsu and Tokai; Tohoku and Kyushu have northern/southern subdivisions. Hiroshima/Yamaguchi belong to Chugoku. Okinawa duplicates consolidated; Senkaku retained separately. |
| Denmark | North, Central and Southern Denmark, Zealand and Capital Region have their native boundaries. Bornholm is a separate island state. |
| United States | All 50 native states plus Washington DC retained separately, including Rhode Island, Connecticut, Massachusetts, Maryland and Delaware. US Virgin Islands consolidated. Duplicate records within other overseas territories consolidated. |
| Australia | All eleven Natural Earth Australian states/territories retained, including ACT, Jervis Bay, Macquarie and Lord Howe; external territories retain their own identities. Queensland, NSW, South Australia and Victoria separated. |
| Timor-Leste | Entire Natural Earth map-unit footprint, including Oecusse, reserved as one state under the existing Indonesian scenario controller. No independence event added. |
| Turkey | Thrace is European; Gallipoli follows an authored Dardanelles divider. Asian Canakkale remains in Balikesir. Izmir includes Izmir. Other regional names assigned by explicit province membership. |
| South Ossetia | Natural Earth territorial shell unified under South Ossetia; Georgian-sector cartographic enclaves removed. This is an explicit map controller correction. |
| Ukraine | Later-conflict boundaries retained with neutral Northern/Southern Donetsk and Luhansk names. Kyiv City/Oblast and tiny boundary strips distinguished. |
| Bosnia | Republika Srpska, the Federation and Brčko boundaries reserved. Federation grouped into geographic regions while preserving its Posavina exclave. Entity geometry takes precedence over overlapping Natural Earth canton polygons. |
| Norway | Six mainland regions plus Svalbard and Bouvet. Existing land-province density retained. |
| UK | Greater London restricted to London boroughs; Kent/Dover in Southeast England. Wales excludes Herefordshire. Scilly integrated into Cornwall. Duplicate overseas territory entries consolidated, including Falklands and South Georgia. Erroneous Southern England label in the Indian Ocean replaced. |
| Spain | Autonomous-community boundaries reconstructed from native provinces, including Basque Country and La Rioja. Genuine source enclaves retained. |
| Romania | Northern/Southern Transylvania, Banat-Crișana, Moldavia, Oltenia, Wallachia and Dobruja grouped explicitly; Bacau/Vrancea no longer assigned to northern Transylvania. |
| Bulgaria | Southern Dobruja restricted to Dobrich/Silistra; Varna and Burgas are outside that state. |
| Israel | Six native districts retained, with separate Golan, East Jerusalem, Latrun and Shebaa footprints where present in accepted control. |
| Egypt | One Sinai state; canal/mainland regions separated. Cairo, Giza, Delta and Nile Valley names/membership corrected. Halayib and Tiran/Sanafir remain separately represented. |
| Central America | Belize and El Salvador each one state. Costa Rica one state. Guatemala split into Petén/south; Honduras into meaningful east/west mainland regions. |
| Cuba | Western, Central and Eastern Cuba; Guantanamo scenario-control sectors retained. |
| Libya | Fifteen geographic states, down from eighteen. |
| Eritrea / Gabon | Two meaningful mainland states each; tiny islands no longer consume their mainland allocation. |
| Somaliland / Puntland | Somaliland shell assigned to Somaliland, including the section incorrectly labelled Somaliland under Puntland. Tiny Somaliland fragments consolidated. Puntland remains outside this shell. This is an explicit controller correction. |
| Comoros / Bhutan | One state per country, overriding the generic protected-area subdivision rule. |
| Syria | Native governorates and one UNDOF state replace overlapping protected-zone fragments and duplicated labels. |
| South Korea | Seven mainland regions, Jeju and separate DMZ/island footprints. Seoul/Incheon grouped with Gyeonggi; Gangwon and the Jeolla/Gyeongsang subdivisions retained. |
| Taiwan | Four main-island regions plus Kinmen and Penghu, down from thirteen states. |
| Papua New Guinea | Five mainland regions; Bismarck islands grouped; Bougainville separate. |
| Russia | Northern Khabarovsk/Okhotsk separated from the Lower Amur area; a Karelian Isthmus state split from Leningrad. Original Karelia local provinces 3, 8, 13, 14 and 24 transferred to Arkhangelsk. Moscow City/Oblast and Altai Republic/Krai names distinguished. |

## Practical limits

The Karelian Isthmus and Uda/Stanovoy transition use authored geographic guide
lines at game scale. They are approximations, not digitizations of archival
treaty borders. Check both cuts visually before treating the geography as final.
The rest of the changes primarily follow the supplied Natural Earth geometry.

Existing province interiors are retained. Provinces crossed by corrected state
lines are split, and small new boundary shards are absorbed into adjacent
provinces of the same state. No whole-world terrain generation or demographic
revision is performed. World population and state-building totals are conserved;
country totals change only across the documented Somaliland/South Ossetia
controller corrections.

## Test order

1. Close Godot, pull the update, run `Prepare_BunnyWorld.bat`, and wait for
   `Geography bundle verified: 0.2.0.8`. Open `project.godot` and start fresh.
2. USA/Australia: verify all native states, Rhode Island, Maryland, DC, ACT,
   Queensland, NSW, South Australia and Victoria.
3. France/Netherlands/UK: check mainland density, single Mayotte/New Caledonia/
   French Guiana, Dutch mainland regions, London versus Dover, Wales versus
   Herefordshire, and Cornwall/Scilly.
4. Japan/Korea/Taiwan: check Tokyo/Kanagawa, Chugoku, Kansai and Kyushu;
   mainland Korean subdivision; four main-island Taiwanese regions.
5. Turkey/Romania/Bulgaria/Egypt: inspect Izmir, both sides of the Dardanelles,
   northern Transylvania, Dobruja and the entire Sinai peninsula.
6. Africa: inspect west/east Eritrea and Gabon, Libya, Somaliland/Puntland and
   Comoros. Inspect South Ossetia and Brčko/Republika Srpska as well.
7. Timor-Leste including Oecusse, Bhutan, PNG mainland/islands, Cuba and
   Central America. Confirm all are selectable and labelled correctly.
8. Inspect the two approximate Russian historical cuts and the Karelia to
   Arkhangelsk transfer. Finally test country search, province selection and
   switching map modes around corrected borders.

## Reproduction

Requires Python with NumPy, SciPy, Pillow, Rasterio, Shapely and Matplotlib,
plus Godot 4.5.1 for compiling the offline border meshes.

```
python tools/restore_repository_assets.py
python tools/fix_geography_0208.py
python tools/finalize_geography_0208.py
python tools/build_boundaries_021.py
godot --headless --path . --script tools/compile_boundaries.gd -- land
godot --headless --path . --script tools/compile_boundaries.gd -- province
python tools/package_repository_geography.py
python tests/geography_0208_tests.py
```

The correction script takes its baseline from the pinned 0.2.0.7 Git commit;
rerunning it does not accumulate additional geometry edits. Existing historical
0207 reports/atlases are retained as historical inputs, not current validation.

## Sources

Natural Earth ADM1/map units and the prior terrain-guided province atlas are
already bundled with the project. Bosnia's ADM1 entity correction comes from
the geoBoundaries gbOpen BIH ADM1 dataset (boundaryYear 2013, build 2024-02-21),
which records the source as Wikimedia Commons and license as Public Domain.
It is used for geographic entity lines, not to change the January 2000 political
status. The exact downloaded metadata is bundled alongside the GeoJSON.

- https://github.com/wmgeolab/geoBoundaries/tree/main/releaseData/gbOpen/BIH/ADM1
- https://www.ohr.int/ohr_archive/arbitral-tribunal-for-dispute-over-inter-entity-boundary-in-brcko-area-final-award/
- https://www.maanmittauslaitos.fi/en/e-services/karelian-maps
