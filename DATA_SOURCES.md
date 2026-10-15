# 0.2.0 data sources and attribution

## Original game baseline
0.1.12 revision 2 map, territorial rights and country population totals are retained. Historical 2000 GHSL-derived local estimates remain as documented by that release.

## World Bank
World Development Indicators API: https://api.worldbank.org/v2/ . Cached responses retain exact URLs and dates. Age distributions use year-2000 population estimates; sexes are combined during preprocessing and no gender simulation is introduced. Employment uses ILO-modeled participation/unemployment estimates for 2000. Adult education uses cumulative completed attainment observations in 1995–2005 where consistent. Public data license reference: https://datacatalog.worldbank.org/public-licenses#cc-by . Indicator metadata identify underlying UN/ILO/UNESCO sources.

## Barro-Lee
Barro, Robert and Jong-Wha Lee, 2013, “A New Data Set of Educational Attainment in the World, 1950-2010.” Journal of Development Economics, vol. 104, pp. 184–198. Authors' dataset v2.2, combined population aged 25+, year 2000. https://barrolee.github.io/BarroLeeDataSet/Data.html . Source CSV: https://raw.githubusercontent.com/barrolee/BarroLeeDataSet/master/BLData/BL2013_MF2599_v2.2.csv . Incomplete schooling at the next level is assigned to the highest completed preceding level, using lpc/lsc/lhc completion shares.

## Religion and supplementary age estimates
United States Central Intelligence Agency, The World Factbook 2000, public-domain government reference republished by Project Gutenberg: https://www.gutenberg.org/ebooks/3672 . Cached text: https://www.gutenberg.org/cache/epub/3672/pg3672.txt . Only numerical entries are imported; partial residuals are unspecified, overlapping affiliations are not double counted, and embedded observation years are retained. Missing or unquantified affiliations remain unknown. Broad age bands supplement two missing WDI profiles with explicitly modeled interpolation.

## Millennium Dawn scenario finances
The supplied `bunnyversion.zip` was inspected, not assumed to execute as a full HOI4 save. `data/foundation_020_report.json` records source paths and supported declarations for each owner. `data/world.json` records the archive checksum and units. Unsupported conditional effects and missing declarations are not fabricated. Financial balances are static until economy implementation.

## Local and temporal limitations
State demographic shares are national/parent-country proxies. The start date is 1 January 2000; surveys may be earlier and estimated age/education data may be reconstructed retrospectively. Age within source bands is modeled. Retirement age 65 is the current game baseline, not an assertion about every country's actual law. No ethnic, gender, individual-person or population-growth simulation is implemented.


## 0.2.0.1 terrain and waterways

ESA CCI Land Cover v2.0.7, year 2000, via the official UCL/ESA viewer WMS. The 300 m source classification is sampled into an 8192 x 4096 prepared rendering mask, with eight merged material families. Source request metadata and the legend are bundled. Elevation continues to use the existing prepared NOAA ETOPO 2022 grid. Major rivers use Natural Earth 1:10m named river features, ranks 0–3. Narrow canals and straits use authored approximate centre lines with explicit sea-zone adjacency.

Original aerial material atlas: built-in Image Generation tool, 14 October 2026; woodland, desert, fields and rock. Prepared runtime images include periodic edge blending and selected material variants. See licenses/Terrain_Waterways_0201_NOTICE.txt for attribution and access details.

## 0.2.0.2 additions

Province topology derives from the user's supplied Millennium Dawn archive, SHA-256 555d5400e2a477088de24e2114284122442be37e38bf8cc5daea094c52852871. `New folder/map/provinces.bmp` is 5632×2048; land definitions and State membership register it to the accepted globe. Conversion diagnostics and original IDs are included. This imports geometry, not a different political scenario.

Detailed surface photographs: Poly Haven aerial_sand, aerial_grass_rock, rocky_terrain, snow_field_aerial, sparse_grass and brown_mud_dry. Native diffuse/colour images are 4096×4096. Poly Haven assets are CC0; source and redistribution terms: https://polyhaven.com/license . Asset metadata/download URLs and exact source MD5 values are data/material_sources_0202.json. Only asset images are used, not website logos, preview renders or other site content.

Forest master: built-in image generation, prompt for a full-frame seamless straight-down temperate woodland canopy, olive/sage tree crowns, conifers, small brown-soil clearings, diffuse light and no roads/buildings/text. Native output 1254×1254; offline edge blending/resizing prepares 4096 layers. Source master is included. Crop fields are an offline pattern over a native photographed material.

Population remains JRC GHSL R2023A year 2000, with the raster URL, DOI and SHA-256 in tools/cartography/population_022_source.json. Province shares now reconcile to every accepted State total. Antarctica uses the earlier accepted Antarctic land geometry plus existing NOAA ETOPO ice-surface heights. Physical shore coverage and regional arid tint are rendering preparations rather than independent geographic surveys.

River courses remain Natural Earth 1:10m public-domain data, now named River features of ranks 0–6 (lake centre lines excluded). The input GeoJSON and prepared diagnostics are bundled.

## 0.2.0.3 preparation

The same supplied province bitmap is registered with 1,171 matched settlement/reference anchors, with rejected ambiguous matches recorded. Targeted State corrections and density-assisted province consolidation are documented in geography_0203_report.json. JRC year-2000 residents now provide individual estimates for every province, reconciled to State totals. Original State/country account totals are preserved, with Quebec accounts combined. Local Åland coast adaptation uses the retained GSHHG source and a minimum game-scale water separation. Compact hover flags derive from the existing supplied flag pages. No new terrain photographs or larger global imagery were added.
