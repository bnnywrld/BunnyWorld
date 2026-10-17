# BunnyWorld 0.2.0.21 handoff

Current patch baseline: confirmed/tested 0.2.0.20, GitHub main d6cc3d76084eca40582adc858cf8e5d9d76c161b. This session delivers the next changed-files ZIP for user testing. Do not infer that GitHub main was updated from a local commit or a ZIP delivery.

Godot 4.5.1 Standard, GL Compatibility. Close Godot before extracting/pulling changes; run Prepare_BunnyWorld.bat and start a fresh campaign. Export a Windows executable when requested. No save-compatibility retrofits.

Current geography: 225 active countries, 1,251 States, 13,310 land provinces. The user confirmed the 55-item consolidation in 0.2.0.20. In .21 Vatican HLS/State 464/province 4478 join Italy/Lazio 534/Rome 4934; global population and land coverage remain unchanged. Old generic State-budget/dispute-protection rules are superseded by these explicit user-approved consolidations.

Canonical footprints are four lossless province-ID PNGs; data/provinces.json assigns provinces to States; world.json owns State/country records. Run tools/build_map.py --godot <Godot executable> after authoring geography. It derives adjacency, border resources, coastal/shared curve fields and render batches together. Never repair ownership changes with per-country masks. A State ownership change needs no geography rebuild.

Runtime MapRendering uploads canonical ID channels as RG8 (CPU picking keeps verified RGB). Its province_texture is RGBA8: State ID in R/G, current owner index in B/A. It is distinct from the offline compatibility province_index.png, whose blue byte remains the local province index. Update the owner lookup only on ownership changes, and membership only on membership changes. Shared smoothed province-pair curves resolve all close-view colours, highlights and lines.

SpatialMapLayers loads offline exact-triangle MeshLibraries for sphere, land/province borders, sea borders and rivers. An 8x4 partition, native frustum culling and conservative horizon culling skip off-screen work. Geometry is not generated on camera motion. Original batches remain available at extreme distance. Chunk resources are losslessly restored from versioned repository parts; their writer saves atomically and loads back every resource.

The .21 comparison improves moving renderer frame times by 13–58% across eight Linux software-rendered views and reduces engine-reported net GPU memory by about 76 MiB. Twelve geography and 33 full-application checks pass. Native Windows/NVIDIA 940MX performance still needs user testing. Source limits and actual checks are in BUILD_INFO.json, TEST_RESULTS.md and documentation/PATCH_0221.md.

Next requested phases, separate from this performance patch: reconcile population to the new States; complete State-specific age/religion/education/economic-activity profiles using regional evidence and reasonable estimates where needed; then test population-informed province allocation before global regeneration. The user accepts a modest province-count increase. Do not leave States without demographics or copy one national profile identically into every State.
