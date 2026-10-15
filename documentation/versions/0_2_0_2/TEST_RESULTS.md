# BunnyWorld 0.2.0.2 validation

Automated checks use Godot 4.5.1 Compatibility on Linux/Mesa llvmpipe. The Windows export is loaded directly as a game pack for executable-content checks; this does not run Windows native code. The user confirmed the accepted 0.2.0.1 Windows baseline; 0.2.0.2 performance on their hardware remains to be tested.

## Data/model checks

- Model, clock/dates, ownership, relations, territorial rights, national/State demographic denominators, finances, same-version save/load, corruption rejection and campaign reset pass.
- Exact comparison with the accepted baseline preserves all 223 country records and every non-province field of the 1,235 State records, including owners, cores, claims, building values and population. Total remains 6,144,737,528.
- Province conversion produces 13,204 nonzero land identities, compared with 13,221 usable reference land definitions. Every identity retains its source MD land ID. Parent lookups reproduce the accepted State raster exactly; all four atlas PNGs fully decode to the generated atlas. Adjacency is reciprocal. Vatican geometry/host references and province selection remain valid.
- Urban/rural partition and all group totals reconcile. There are 1,973 urban provinces, 1,446 groups, 2,237 scene clusters and 117,367 buildings. Every represented settlement links to a valid urban province. Urban provinces contain 3,714,533,502 residents; the shared State pools contain 2,430,204,026. No State population is reallocated.
- Displayed circumscribed building footprints clear each other by at least approximately .25 km. Enlarged landmark grounds are clear. An independent exact-segment check verifies buildings clear mapped river courses, separately from the generator's sampled course tree. Anchors remain in their intended land provinces and footprints stay within starting-country land.
- Both eight-layer material files have complete expected S3TC/mipmap layouts: 2048 Light (22,369,860 bytes) and 4096 Balanced/High (89,478,724 bytes). Sahara, Amazon and Greenland biome fixtures and the Compatibility sampler budget pass. No geographic image streaming path is present.
- GPU relief channels match the CPU binary. Exaggeration is 8 with a land lift below 100 m; maximum displacement is approximately .009199 globe radii. Water has zero displacement. Ray picking, oblique anchors and dateline wrap pass. Antarctic fixtures at longitude −45, 0 and 60 / latitude −80 have independent land coverage, ice and positive elevation.
- Waterway checks pass for 350 named rivers plus eight unnamed connecting features, reciprocal Suez/Panama/Bosporus/Dardanelles links and Black Sea reachability. Caspian, Lake Victoria and Lake Superior remain excluded from sea zones. Passage metadata has no duplicate ID/neighbour pairs.

## Scene checks

Source UI smoke and foundation UI tests pass: country controls, all focus targets, close-camera tilt and terrain anchoring, population panels/tooltips, metropolitan names, place search and aliases, pause restoration, preferences, saves, Vatican/Colosseum picking, scenery fade/caps, demographic scopes/denominators, finances, World Ledger and tension baseline.

Resource-load checks cover all province/lookup/relief/biome textures, three boundary meshes and river ribbons. No shader, script or resource errors appear in successful scene runs. The software driver reports unsupported V-Sync; Xvfb reports harmless keyboard-symbol warnings.

Source captures inspect Tokyo, Paris/Eiffel, Arizona, Himalayas, Antarctica, Korean province geography, minimum-window demographics and the three narrow waterway areas. City labels retain priority and demographic charts appear together without source paragraphs. Selection highlights are thicker than ordinary borders. Source-map and pixel-to-globe registration remain approximations, especially tiny/polar/coastal areas.

Travel/revisit checks preserve the same eight-layer texture handle, the single 27,985-vertex terrain grid and all prepared city meshes. Nearby bounds remain 2,048 buildings / 96 clusters. Both full-scene startup quality options load their expected library. Whole-frame observations are recorded in the validation logs; software-renderer timings are not a Windows FPS claim or a guarantee for other GPUs.

The final Windows executable and saved archives receive version/resource checks, full UI smoke and selected scene captures, embedded file MD5 verification, source-data byte comparison, ZIP CRC checks and SHA-256 checks. BUILD_INFO.json and the companion checksum file record the exact released bytes. Final delivery requires a saved-release roundtrip hash match.

Growth, exact census boundaries, detailed naval access/control and old-save migration remain deferred. Surface photos are representative materials; the generated forest master is resized offline, and regional dry colour is a rendering heuristic. Shore smoothing improves coverage without adding missing coastline surveys.
