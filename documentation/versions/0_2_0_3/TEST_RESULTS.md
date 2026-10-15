# BunnyWorld 0.2.0.3 validation

Prepared 15 October 2026 (Warsaw). Automated tests use Godot 4.5.1 Compatibility on Linux/Mesa llvmpipe. The actual Windows EXE is loaded directly as a game pack. This does not execute Windows native code; testing on the user's PC is still required.

## Data and geography

- 223 countries, 1,233 States, 13,481 provinces; total population 6,144,737,528.
- Every country's population and building totals match the accepted 0.2.0.2 baseline. Quebec’s three former State accounts are merged exactly; other State population totals remain unchanged.
- All province atlas PNGs fully decode to the generated ID atlas; parent lookup matches the State raster. Every province belongs to one State and adjacency is reciprocal. Vatican’s subpixel override and host province remain consistent.
- Every province has a nonnegative integer estimate. Province sums equal State totals; city/metropolitan totals equal member sums, without adding a second population. Debug population edits, transfers, reset and same-version save/load pass.
- Timor and Papua coordinate fixtures have their intended State identities. Åland’s physical component is distinct from mainland Finland. Hong Kong and Macau both have city groups and nonempty prepared scenery.
- Sparse-area consolidation records 239 merges. Substantial same-land-mass fragments are split; source registration and tiny islands remain approximate.
- Displayed building footprints clear each other and monument grounds. An independent exact-segment river check confirms clearance beyond displayed building radii, separately from the generator's sampled tree. Anchors resolve to their intended provinces, including the Vatican host override.
- The 350 named rivers, reciprocal four passages, Black Sea reachability and exclusion of inland lakes pass. CPU packed relief bytes match GPU channels, including trial river depressions; water remains undisplaced.

## Engine, UI and exported content

Model, relations, territorial rights, province population, place catalogue, relief, foundation/finances/demographic denominators and resource-load tests pass when run against the final embedded executable. Full UI smoke passes: country controls, panels, searches, preferences, saves, selected provinces, metropolitan information, Vatican/Colosseum picking, scenery fading/caps and the existing foundation.

New-feature scene checks confirm physical mode on Start and Play, a real cached flag image before the country name, a compact tooltip atlas and reuse of the same hover texture. Rural tooltips display individual estimates. Existing four-chart demographics and compact layouts remain. Captures inspect corrected geography, Tokyo, Arizona, Nile rivers/banks, Åland, Hong Kong/Macau, Timor, southern India and the minimum-window demographic layout. Existing coast mesh/shoreline sampling artifacts can remain at extreme close-up; this patch does not supply a globally finer shoreline mesh.

The clean official Windows template SHA-256 is 78ccc576e8f8bffd7ef6ad6f36ebd72a41e609a1052225a55b3407c96ea84065. The exported PE pack/footer agree. All 255 embedded file MD5 values are verified; 54 source/runtime files match byte-for-byte, including world/province/city/population/flag data, material libraries, relief, boundary resources and shaders. The executable itself identifies 0.2.0.3. Exact final identity is in BUILD_INFO.json and the companion checksums.

## Travel and quality

Travel/revisit tests retain the same eight-layer material texture, one 27,985-vertex detail grid and all prepared scenery mesh handles. Nearby bounds stay at 2,048 buildings / 96 clusters. The final EXE passes cache/passage tests using the Light 2048 library; high-quality scene/travel checks load the expected 4096 library. There are no camera-triggered geographic image decodes/uploads or terrain/city rebuilds.

Representative whole-frame software-renderer comparison, milliseconds (not Windows FPS):

| Renderer | Median | 95th percentile | Maximum |
| --- | ---: | ---: | ---: |
| Accepted 0.2.0.2 | 388.830 | 455.818 | 482.477 |
| Optimized 0.2.0.3 rendering | 383.241 | 472.684 | 499.052 |

These measurements show comparable software-renderer behaviour, not a hardware performance guarantee. A provenance-description string was corrected before final packaging; rendering code/assets did not change after this comparison. The final executable separately passes full smoke, data/model and texture/cache checks.

The driver warns that V-Sync is unsupported; Xvfb can print keyboard-symbol warnings. Successful final runs contain no script, shader or resource errors. Native Windows performance, visual preferences and any remaining regional map defects require the user's new-campaign test.

Archive CRCs, SHA-256 values and saved-release roundtrip checks are recorded in the companion validation/checksum files. No old-save migration, demographic growth, annual scenery growth or naval-access simulation was added.
