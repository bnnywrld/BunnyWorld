# 0.2.0 data sources and attribution

## Economy and quality calibration (0.2.1.14)

The supplied Economy Design is a design reference; the user selected Phase 1 plus basic automatic trade, retained full upfront construction payments, enabled next-month budgets and gradual quality effects, and explicitly deferred electricity. `tools/build_economy_rules.py` reproduces `data/economy_rules.json` from existing checked-in/restored inputs. It retains construction, province-ID and terrain checksums. Initial GDP, population, inventories and employment rates are kept; no historical GDP/production dataset is replaced with fabricated observations.

Baseline agricultural potential uses area-weighted cropland-family coverage in the existing ESA CCI Land Cover 2000 preparation, plus MD-derived staffed Agriculture District capacity. Prepared renderer classes/resolution and mixed land-cover pixels make this an approximate potential layer, not measured crop yields, exact cultivated hectares or actual year-2000 national food self-sufficiency. Baseline farms include unrepresented agriculture; districts add capacity above their starting staffed amount. Global starting output calibrates to demand plus 8% headroom. This avoids treating deserts and ice as equally productive farmland; it does not assert deposit/farm-level accuracy. No cartography input, map or packed asset changes.

MU prices/output factors, tax-income shares, budget percentages, hiring adjustment, private purchasing envelope, GDP productivity/input effects, CPI, interest response and all quality formulas are tunable gameplay coefficients. RU stays an MD resource-capacity point; it is not a tonne, and a market bundle is not a physical reserve conversion. Food is one person-month basket; its initial $12 benchmark is a game-affordability assumption, not a measured international retail price. Other goods are standardized bundles calibrated to aggregate demand and source capacity. Imports/exports conserve units and value, use one global price, and do not deposit gross export revenue into Treasury.

The supplied MD `00_money_system.txt` calculates aggregate building employment, resource/other sector work and subsistence agriculture; its civilian-industry worker comment explicitly includes dependent retail/services/food-industry jobs. BunnyWorld retains its existing MD staffing coefficients and initial demographic employment, then permits gradual unemployment adjustment. Unrepresented employment is retained rather than forcing the whole economy into mapped buildings. No individual business, commuter or worker is simulated.

Initial education/healthcare quality scores provisionally map MD spending-tier ideas (`edu_XX`, `health_XX`) with a bounded GDP/person fallback. They are not empirical cross-country quality indices. Active funding moves qualities slowly; quality caps, maintenance costs, research multipliers, productivity contribution and healthcare/food growth modifiers are gameplay balance. Births/deaths, aging, migration and approval remain separate future systems. Electricity, computing/AI and deeper diplomacy/organization mechanics remain inactive despite metadata hooks.

## Original game baseline
0.1.12 revision 2 map, territorial rights and country population totals are retained. Historical 2000 GHSL-derived local estimates remain as documented by that release.

## World Bank
World Development Indicators API: https://api.worldbank.org/v2/ . Cached responses retain exact URLs and dates. Age distributions use year-2000 population estimates; sexes are combined during preprocessing and no gender simulation is introduced. Employment uses ILO-modeled participation/unemployment estimates for 2000. Adult education uses cumulative completed attainment observations in 1995–2005 where consistent. Public data license reference: https://datacatalog.worldbank.org/public-licenses#cc-by . Indicator metadata identify underlying UN/ILO/UNESCO sources.

## Barro-Lee
Barro, Robert and Jong-Wha Lee, 2013, “A New Data Set of Educational Attainment in the World, 1950-2010.” Journal of Development Economics, vol. 104, pp. 184–198. Authors' dataset v2.2, combined population aged 25+, year 2000. https://barrolee.github.io/BarroLeeDataSet/Data.html . Source CSV: https://raw.githubusercontent.com/barrolee/BarroLeeDataSet/master/BLData/BL2013_MF2599_v2.2.csv . Incomplete schooling at the next level is assigned to the highest completed preceding level, using lpc/lsc/lhc completion shares.

## Religion and supplementary age estimates
United States Central Intelligence Agency, The World Factbook 2000, public-domain government reference republished by Project Gutenberg: https://www.gutenberg.org/ebooks/3672 . Cached text: https://www.gutenberg.org/cache/epub/3672/pg3672.txt . Only numerical entries are imported; partial residuals are unspecified, overlapping affiliations are not double counted, and embedded observation years are retained. Missing or unquantified affiliations remain unknown. Broad age bands supplement two missing WDI profiles with explicitly modeled interpolation.

## State resources, staffing, rights and diplomacy (0.2.1.13)

`tools/import_state_economy.py` reads the supplied `bunnyversion.zip` as data, with input hashes retained in `data/state_economy_2000.json`. MD state history is bounded to 2000-01-01. All resource-bearing source states map to current `source_states` references; named pools prefer an exact canonical state-name match, then unmatched/shared pools are area-apportioned once, preferring territory owned by the source owner. Mapped totals equal source totals: Fossil fuels 4,096; Light metals 2,344; Rubber 1,897; Technology metals 2,237; Steel 4,298; Precious metals 1,963. Microchips and Composites have no starting deposit quantity. These are resource units (RU), one RU per MD source capacity point, not reserves in tonnes or annual physical production. California retains MD state 811’s full 21 fuel / 2 precious-metal units; the earlier generic area split leaked its pool into neighboring states. Resource metadata appears in 800 canonical states; no unsupported deposit increases are invented. Geographic redistribution reflects the game's differing state boundaries and is not a claim of deposit-level accuracy.

Year-2000 cores and claims replace the old source snapshot, unioning every mapped source state's direct history additions/removals. No conditional territorial-rights assignments were found at the starting date. The new inactive `PAU` record uses MD's Palau name; its flag already exists in the atlas. This adds no country ownership, cores by assumption or diplomatic effects.

MD `common/scripted_effects/00_money_system.txt` supplies workers per level (million values converted to people): Civilian Industry 206,000; Military Industry/Dockyard 18,800; Offices 473,000; Agriculture 188,000; Chip/Composite plants 37,500; Refinery 184,000; Nuclear 115,000; Fossil power 7,500; Renewable power 22,500; Internet 12,000; Rail 15,000. The source explicitly includes dependent retail/services jobs in civilian-industry requirements. These are base game coefficients; automation, country/sector modifiers, MD's separate resource/subsistence sectors and public-service formulas remain outside this implementation. Existing demographic employment and unemployment rates remain authoritative.

Election display reads `last_election`, `election_frequency` and `elections_allowed` from starting country history. Diplomacy imports all `common/scripted_diplomatic_actions` definitions, influence actions from `01_influence_scripted_guis.txt` and standard inherited actions represented in the diplomacy interface. AI-only attaché aliases merge with ordinary attaché actions. The 83-row catalogue retains source IDs/paths; every action remains disabled. No imported script or effect is executed.

## Starting leaders and government metadata (0.2.1.13)

`tools/import_leaders.py` imports the supplied archive's country history through 2000-01-01, recruited `country_leader` characters, explicit monarch ideas/flags and localized names. It selects the declared ruling ideology/outlook, preserves portrait references, and places a sole parliamentary/constitutional-monarchy leader as head of government; presidential/absolute-monarchy leaders use head of state. An absent second office stays empty. Modern and legacy character declarations are supported. Invalid UTF-8 source files use Windows-1252 decoding, preserving names such as Gerhard Schröder. Ten unsupported history conditions are recorded and skipped. Starting leaders exist for 223 of 224 countries; Lebanon supplies only military commanders and stays unnamed. The source declares Putin at the scenario start; no external political timeline is substituted.

Explicit numeric `ruling_party` and `gov_coalition_array` IDs map directly to the previously imported party catalogue. Unsupported Salafist IDs remain excluded without appointing substitutes. Government metadata does not change support, parliament seats, coalitions, elections or leaders during play. The source archive contains no leader/party image files. For the 226 named offices, `tools/import_leader_portraits.py` obtains exact matching graphics from the official [Millennium Dawn repository](https://github.com/MillenniumDawn/Millennium-Dawn/tree/e231ce3935a558f1d7baaa3c9bf15ef888cd3f04/gfx/leaders), pinned to revision `e231ce3935a558f1d7baaa3c9bf15ef888cd3f04`. The committed `data/leader_portraits.json` records original paths, Git blob IDs, source/output SHA-256 hashes and matching names/references. Original DDS pixels are decoded and losslessly encoded as PNG without cropping/resizing; originals are cached outside the checkout. The source declares CC-BY-SA-4.0; attribution and full license are retained in `licenses/Leader_Portraits_NOTICE.txt` and `licenses/Millennium_Dawn_LICENSE.txt`. Missing offices stay empty; no leader or image is fabricated.

Data Center is a BunnyWorld balance addition, not imported MD data: $6B, 36,000 points, 10,000 workers, cap 20/shared, $8B base annual GDP before existing productivity/staffing. Resource amounts are not empirically calibrated across commodities, and no speculative deposit increases or conversion to physical reserves are made.

## Society, religion catalogue and parties (0.2.1.11)

The user-provided Demographics and Society Framework guides staged implementation. The uniform +1% annual growth default is a configurable gameplay assumption, not historical country growth data. Only this net growth runs; no birth/death decomposition, aging or migration is inferred.

`python tools/build_religion_catalog.py` deterministically reads the existing country/state profiles and writes `data/religion_catalog.json`: 38 source labels, 32 canonical categories, fixed colors and an unresolved-category report. Nonreligious → Atheist; Other / not stated → Other / unspecified; Tibetan Buddhist → Buddhist; Maronite/Greek Catholic → Catholic; Zaydi/Ismaili → Shia. All other source categories retain their identity, including Shinto / Buddhist, folk traditions and broad unspecified branches. These are gameplay aggregations; no branch shares are invented and source demographic files remain intact. Religion & State law seeds provisionally map Freedom of Religion/Restricted Religion to Secular State while preserving State Religion. Explicit Sunni/Shia/Orthodox source ideas seed affiliation where available; unresolved affiliation stays missing. The seed set is still a gameplay abstraction, not a verified legal history.

`python tools/import_society.py /path/to/bunnyversion.zip` produces `data/parties_2000.json` for all 224 active countries. It parses country history through 2000-01-01, declared `party_pop_array` shares, `set_popularities`, politics-view scripted localization and party-icon sprite references. The imported file records input hashes, missing country-specific names, missing logos and unsupported conditions. MD's declared outlook totals rescale the explicit party shares within each outlook; incomplete groups remain unrepresented rather than using MD's random startup fill. Ten unsupported history conditions are skipped; imported scripts are never executed. Country names fall back to MD generic names when no resolvable country label exists; these are marked in party metadata and UI tooltips. Names and support reflect this supplied MD build, not a verified historical election dataset.

MD array indices 0–3 map to Western Outlook, 4–9 Emerging to Multipolar Outlook, 12–19 to Non-Aligned Outlook and 20–23 to Nationalist Outlook. Indices 10–11 (Salafist) are excluded without reallocating their polling. The 4,928 supported party slots include zero-support source slots; UI lists positive support. The archive has references but none of the actual referenced party images. Sprite/path metadata is preserved; UI uses initials and colored markers. The importer can convert referenced images into manifest-free small PNG assets if a later supplied archive includes them.

## Currency names (0.2.1.10)

`data/currencies_2000.json` is display-only metadata for the 224 scenario countries. `tools/import_currency_names.py current.xml historical.xml` reproduces it from the SIX ISO 4217 [current](https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-one.xml) and [historical](https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-three.xml) lists; downloaded files stay outside the checkout and their hashes are recorded in the JSON. The script contains explicit scenario assignments for 2000-01-01, including withdrawn units such as the drachma, tolar, kroon and Turkish lira. Euro-country names use the accounting currency introduced in 1999. Transnistria and Somaliland use explicit local-unit names without invented ISO codes; other de facto entities use the selected local/parent unit. These assignments are scenario metadata, not a simulation of multi-currency circulation or automatic monetary transitions. MD's foreign reserve ideas are deliberately not substituted for domestic currencies. Treasury, debt and GDP remain in USD; no exchange rates or currency effects are enabled.

Removing Semi-Presidential from the law choices maps its 32 scenario entries to Presidential. Starting balances remain unchanged. Religion & State seed mappings are described below.

## Millennium Dawn research (0.2.1.9)

`tools/import_research.py` extracts `data/research.json` from the user-supplied `bunnyversion.zip`. It records SHA-256 hashes of the technology definitions, imported country histories and MD defines. The import contains 1,230 visible technologies in 11 categories and country-specific initial unlocks for all 224 scenario countries. English names resolve the archive's localization aliases; no descriptions, artwork or technology effects are imported.

The modern No Step Back / By Blood Alone / Gotterdammerung branches are selected consistently, including matching DLC-conditional country-history technologies. Parallel legacy armor, artillery/AA, aircraft/bomber and missile trees are omitted. Technologies with no visible folder (including hidden special-project grants and legacy doctrines) are outside the selectable tree. Category placement and branch coordinates come from source folders; path links and explicit dependencies define research order. A source self-loop on `nsb_drone_artillery_ammo_3` is omitted; other graph cycles fail import. Explicit year labels and research cost multipliers remain source values; special-project placeholder years at or below 1900 display as 2000.

The importer reads unconditional history and dated history through 2000-01-01, plus supported DLC, tag, date and boolean conditions. Twelve unsupported history conditions are skipped and counted; script effects and startup scripts are not executed. Missing country histories receive no invented technologies. National focus, special-project, doctrine, game-rule and equipment gates are not simulated: this stage imports names/order and basic research timing only. This deliberately permits researching the visible special-project technologies through universities. Base cost is the archive's 250 days times research_cost; its ahead-of-time factor is 1.0 per year, recalculated daily in the game with neutral national research speed.

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
