# BunnyWorld 0.2.0.3 handoff

Continue from the prepared 0.2.0.3 source delivered with this document. The user tested and accepted most of 0.2.0.2, then approved the complete 0.2.0.3 map patch in this chat. Original project attachments labelled 0.1 are historical references.

The patch covers the agreed terrain repetition work; broader rivers/banks and limited lowland riverbed trials; narrow intense physical-map border/coast colouring; cached country flags in hover tooltips; physical mode on Start/new campaign; targeted State/province corrections from the user's list; sparse-interior province consolidation; city ground scale; Hong Kong/Macau cities; Quebec as one State; and individual province population estimates.

Read RELEASE_NOTES.md for every geographic target and deliberate adaptation, DEVELOPMENT.md for regeneration, TEST_RESULTS.md for actual checks and BUILD_INFO.json for release identity. Minimal immutable accepted-baseline data is under tools/cartography/baseline_0202. Corrected registration and geographic inputs are prepared. Rebuilding the full reference requires the user's bunnyversion.zip, not the original 0.1 standalone source.

User's standing rule: smooth travel/avoiding stutter takes priority. Longer startup is acceptable. Push back when requested visual quality would add avoidable runtime decoding, upload/rebuild costs or excessive memory/shader cost, and propose measured alternatives. Never silently pursue gigantic global textures simply because sharper graphics were requested.

Preserve the resident eight-layer material array, fixed terrain grid and cached city meshes. All province estimates are reconciled to States; city groups are aggregate views. States remain the demographic unit. Growth/annual expansion are postponed. No old-save compatibility or migration unless explicitly requested. Current save schema is 10, scenario bunny_world_2000_0_2_0_3; same-version save/load stays.

Year 2000, Windows 10/11 standalone ZIP, uniquely versioned embedded EXE. Budget approximately 500 MB runtime; distinguish runtime/download size from VRAM. Keep four demographic charts together, compact UI, rights/finances/controls/World Ledger/tension foundation and city label priority. Landmark labels remain absent; landmark search remains available.

Province IDs were rebuilt. There are 223 countries, 1,233 States and 13,481 provinces. Quebec merges three former States and their accounts. All national populations/buildings and the 6,144,737,528 world total are preserved. Targeted outlines/controllers follow the registered mod reference approximately. Åland has a deliberate minimum game-scale water gap. West Timor/Timor Leste are on Timor; no independent country or political status was invented. Hong Kong and Macau have city scenery.

Remaining limits: game-scale source registration and coastline/elevation sampling, estimated rather than census province populations, importance-based river widths, only two lowland trial-channel areas, representative materials/scenery and potential residual repetition. Never describe these as exact survey geometry or worldwide physical riverbeds. Automated render/performance checks use Linux/Mesa; native Windows performance requires the user's test.

The next task should follow the user's 0.2.0.3 test feedback. Do not start a different simulation patch just because old roadmaps mention one.
