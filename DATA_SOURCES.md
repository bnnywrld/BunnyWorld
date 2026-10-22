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

## 0.2.0.6 geographic replacement

State boundaries use the bundled Natural Earth 1:10m geographic subdivisions, grouped through larger named regions and adjacent small-unit unions. https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/ . Natural Earth is public-domain geographic reference data; its contemporary administrative organization is not an exact January-2000 administrative atlas. The accepted 0.2.0.5 country-control mask remains authoritative.

Province generation is independent of the MD province bitmap. Existing Natural Earth rivers, NOAA ETOPO relief, ESA CCI land classification and settlement reference points guide offline growth on local Lambert azimuthal equal-area grids. Kilometre distances and spherical areas replace uncorrected flat texture distances. Prepared shapes are gameplay approximations, not municipal or census districts.

Local demographic refinement is explicitly deferred. Existing national totals are preserved, with temporary overlap/area allocations solely to maintain runtime contracts. Existing population source notices remain historical attribution, not a claim that GHSL was newly aggregated over this map.


## Organization foundation (0.2.1.7)

The supplied `Bunny_World_Organizations_Design.md` defines the eight types, statuses, headquarters, integration ladder and future mechanics. Starting membership arrays are inherited unchanged from clean-globe commit 2678dae238b99d0c75a4fb98d71cd53b23451c08, not newly claimed as historically audited. The document says: “Ask me to review member lists as a table before importing; do not silently guess.” No additional lists or status assignments were imported in this patch. This is why UN, cultural communities, movements and other missing groups remain inactive directory entries.

| Existing organization | Scenario members retained |
| --- | ---: |
| EU | 15 |
| NATO | 19 |
| ASEAN | 10 |
| ECOWAS | 15 |
| WTO | 130 |
| G7 | 7 |
| CSTO | 6 |
| OAU | 53 |
| ARAB | 22 |
| GCC | 6 |
| CIS | 12 |
| APEC | 21 |
| OECD | 29 |
| OPEC | 11 |
| MERCOSUR | 4 |
| NAFTA | 3 |
| OSCE | 49 |
| IMF | 178 |
| IBRD | 178 |

Additional definitions below are **not active memberships**. The candidate lists are only those explicitly provided in the design; blank/unspecified lists still require historical verification and review, including the game's representation of missing territories. They cannot be enabled by clicking the directory.

| Definition awaiting membership review | Candidate or unresolved starting list |
| --- | --- |
| Benelux | Belgium, Netherlands, Luxembourg |
| SADC | Historical January-2000 roster to verify |
| Andean Community | Bolivia, Colombia, Ecuador, Peru, Venezuela |
| CARICOM | Historical roster and associate statuses to verify |
| Union State | Russia and Belarus; treaty activation and integration interpretation to review |
| Eurasian Economic Community | Later-2000 founding roster to verify; absent at scenario start |
| OAS | Historical roster and suspension statuses to verify |
| Shanghai Five | China, Kazakhstan, Kyrgyzstan, Russia, Tajikistan; modeled as a forum definition, not an exclusive faction; succession to SCO pending |
| UN | January-2000 membership and game-tag coverage to verify; Security Council roles pending |
| IAEA | Historical roster to verify |
| G20 | Historical participating countries and institutional representation to verify |
| G77 | Historical roster to verify |
| Paris Club | Historical creditor membership to verify |
| Commonwealth | Historical roster to verify; Pakistan's 1999 suspension must be represented |
| Francophonie | Full/associate/observer statuses to verify |
| Organisation of the Islamic Conference | January-2000 roster to verify |
| CPLP | January-2000 roster to verify |
| Non-Aligned Movement | Historical roster and observer statuses to verify; South Africa chair in 2000, no HQ |
| NPT | Parties/statuses to verify; India, Pakistan and Israel outside in the design |
| CWC | Parties and ratifications to verify |
| Ottawa Treaty | Parties and ratifications to verify; USA, Russia, China outside in the design |
| CTBT | Signed versus ratified statuses must remain distinct; not in force |
| Kyoto Protocol | Later entry into force; no automatic activation or member import |
| Rome Statute / ICC | Later entry into force; no automatic activation or member import |
| UNCLOS | Parties and ratifications to verify |

MERCOSUR associate memberships (Chile/Bolivia), NATO partnerships and CIS founding-participant distinctions also need review before changing the inherited full statuses. Real founding membership dates are not fabricated where the supplied metadata is incomplete. Headquarters follow the supplied design, plus existing organization context (OSCE Vienna and World Bank Washington). NAFTA has national sections rather than a single HQ; the Union State's multiple institutions are left without a single point pending review.

Dated display-name references: [AU launch on 9 July 2002, South African Government](https://www.gcis.gov.za/content/newsroom/media-releases/media-releases/african-union-summit-kicks-durban); [CSTO Charter of 7 October 2002](https://en.odkb-csto.org/documents/documents/ustav_organizatsii_dogovora_o_kollektivnoy_bezopasnosti_/); [OIC name change at the June 2011 ministerial meeting, Türkiye MFA](https://www.mfa.gov.tr/OIC.en.mfa). OIC is an inactive definition. Display names do not change membership, leaders, treaties or integration levels.

No numerical political-power, opinion, approval, host-country, economic or military modifiers have been invented. The existing systems continue unchanged until values and associated rules are agreed.


## Construction source (0.2.1.8)

The user-supplied bunnyversion.zip contains `common/buildings/00_buildings.txt`, including its monetary pricing table and actual `base_cost` / `per_level_extra_cost` construction-point fields. `00_money_system.txt` supplies GDP base coefficients and direct energy/network output. `MD_defines.lua` sets civilian construction speed to 4 and infrastructure coefficient .75; `00_on_actions.txt` sets productivity_center to 1000. `data/construction.json` records building/money source hashes. No contemporary MD release is substituted for this supplied version.

The source has not been executed as HOI4 scripts: this scaffold uses neutral sector productivity modifiers and full staffing, scaled by each game's imported overall_productivity. Starting national GDP remains the imported baseline; only new completed buildings add output. MD's resource, workforce, healthcare, tax, law, energy and global dynamic-modifier systems are not newly simulated. The infrastructure speed scaling and logarithmic slot formula are explicit BunnyWorld balancing adaptations approved in the construction discussion.

Railroads use the supplied MD rail_terminal definition as the current state-network proxy, with ten separate levels. This is not a claim that MD's province railway routes or their per-province prices were implemented. The geometric coast eligibility list is derived from the game's existing land/sea masks, excluding inland-water records; it changes no geography.
