# Bunny World 0.2.0.3

## Geography and province density

Replaced rectangular State stretching in the affected areas with one settlement-anchored registration of the supplied Millennium Dawn bitmap. The registration has 1,171 accepted settlement/reference anchors; ambiguous place-name matches are rejected. Original source province IDs remain traceable. Province fragments on the same connected State land mass are separated when substantial; offshore archipelago groups are retained. This is a game-scale registration, not an exact reproduction of every source pixel.

Corrected State geography in Egypt; Transnistria/Moldova; South Shan and neighboring Burma; Somaliland, Somali National Alliance, Jubaland and the other Somali controllers; Niger; Basque/Castilla; the requested Chinese areas; southern Vietnam; Saudi Arabia/Rub' al Khali; and Indonesia. Southern India and eastern Congo required correcting misplaced State footprints as well as their provinces, so their State registration was repaired jointly. Existing State controllers, source identities, rights and country account totals remain authoritative; territorial outlines now follow the registered reference more closely.

Targeted province work also covers South Korea/Changwon, Ituri/Nord-Kivu, Köln-Bonn/Bayern, Lappi/Västerbotten, southern India, Rio de la Plata/Pampas, Natuna/Kalimantan/Banten and West Papua/Timor. West Timor and Timor Leste are now on Timor rather than occupying parts of Papua. Hong Kong and Macau have city markers, population groups and prepared scenery. Their accepted starting political status is retained.

Åland uses the retained GSHHG shoreline locally. Because several channels are narrower than a game pixel, a least-land water route retains a minimum separation through physical-mask downsampling. Some tiny skerries/channels are deliberately adapted to the game's resolution. Åland is no longer physically joined to Finland.

Eastern Quebec, Western Quebec and Ungava are merged into one Quebec State, including population, buildings and territorial rights. Canada’s aggregate is unchanged.

Adjacent provinces averaging under approximately one resident/km² are eligible for consolidation in Greenland, Australian interiors, Sahara/Arabian deserts and Amazon interiors. Known settlement provinces remain detailed; merges stay inside States. There are 239 merges, including Kitaa 14→3 and Tunu 10→2. Large empty regions receive larger provinces while populated corridors retain smaller ones. The final map has **13,481 provinces, 1,233 States and 223 countries**.

## Physical map, rivers and cities

- Removed the general country-colour wash from physical-map interiors. Stronger finite bands fade inward at international borders and ocean coasts. Lake shores do not create country-colour bands. Bands narrow on small islands and thin country components to retain natural interiors. Political fill and selection highlights remain separate.
- Added fixed-world material offsets, quarter-turn patch variation, continuous coordinate warping and explicit mip gradients. This reduces both tile repetition and conspicuous repeated source features without enlarging the global image or streaming imagery during travel. Unneeded secondary/rock samples are skipped. Natural material sources remain representative and some repetition can still be visible.
- Rivers now combine an estimated geographic channel width with a zoom-sensitive minimum screen width, plus distinct banks and darker centres. Widths are based on river importance, not a surveyed global width dataset. The 350 named rivers and existing canal/strait connections remain.
- Trial shallow broad channels are baked into selected lowland Nile and Amazon reaches. Depression is capped at 48 displayed metres and 20% of local raised terrain, with smooth profiles limited by the prepared relief grid. CPU picking, terrain, borders and scenery share the same field. This is not worldwide riverbed/bathymetric modelling.
- Replaced undersized city ground detail with broader streets, yards and parks projected at the displayed buildings’ scale. Rebuilt street blocks against the corrected geography and increased river clearance. The scene contains **114,191 buildings, 2,233 cached clusters and eight landmarks**; counts reflect geographic capacity and clearance, rather than forcing overlaps. Nearby caps remain 2,048 buildings / 96 clusters.
- Added actual cached flag images before country names in hover tooltips. Start and new campaigns open Physical Earth; loading a same-version save restores its saved mode.

## Population

Every province now has an individual year-2000 population estimate from the prepared resident grid, reconciled to its State total. Rural provinces no longer display a shared pool. City/metropolitan groups sum member provinces and never add a second population. All accepted country populations and building totals are conserved; world population remains **6,144,737,528**. States remain the demographic simulation unit, and allocations are cached.

There is no population growth, annual scenery expansion, old-save migration or new naval-access simulation in this patch. Native Windows performance requires the user's test; automated rendering uses Linux/Mesa.
