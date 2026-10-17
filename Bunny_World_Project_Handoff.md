# BunnyWorld 0.2.0.24 handoff

Changed-files source patch over GitHub main c74c3c6 (0.2.0.23). App, geography and display are .24. See documentation/PATCH_0224.md. Delivery is a ZIP for native user testing; this does not imply main was pushed.

Current totals: 224 countries, 1,239 states, 13,308 land provinces; population 6,144,737,528. Mariana Islands absorbs Saipan/Tinian; Hawaii absorbs Midway/Johnston; Micronesia becomes a single state including former Palau. PAU is removed from active and releasable countries. Malpelo and Navassa states/provinces/land are removed (five native pixels). Other province footprints remain exact. Statistical allocations from deleted islands stay in their original countries; Palau population joins Micronesia.

UI: 370px shared country/diplomacy inspector; supplied static Moon/Earth image for loading/menu; country flag breadcrumb centers camera and opens state browser; temporary state-list hover presentation without selection/owner changes; all planned top-toolbar sections open empty titled inspectors with close/toggle behavior.

The user runs Windows and checks native layout, interactions and graphics. Automated checks cover data/reference integrity, exact raster delta, application behavior and prepared-resource contracts. No new FPS claim and no renderer redesign in this patch. The proposed experimental renderer branch remains deferred.

Authoring: tools/consolidate_islands_0224.py is one-shot, followed by tools/build_map.py --godot <Godot>. The shared pipeline now also refreshes tiny_land_bits on topology changes to remove physical-mode ghost islands. Prepared geography/display bundles and restore parts must ship together.

Prior foundation follows (historical counts/versions below are superseded):

# BunnyWorld 0.2.0.23 handoff

0.2.0.23 is the next performance patch over the user-confirmed 0.2.0.22 (local source snapshot c4750c7). App/display advance to .23; geography remains .21. See documentation/PATCH_0223.md. GitHub main is not implied to have changed by a local commit or ZIP delivery.

Current renderer: no duplicate whole-world border/river buffers; the exact spatial batches remain, with a 256×128 far sphere beyond distance 4.5 and original 512×256 sphere batches nearby. planet.gdshader and planet_physical.gdshader compile shared planet_surface.gdshaderinc with separate physical shading. The physical far path blends to a 4096×2048 mipmapped normal/snow cache from distance 2.0–2.4. It retains dynamic world lighting; close relief/picking stays original. Cache data is independent of ownership.

Mouse hover is coalesced to one latest-position query per application frame; clicks stay immediate. Conservative point buckets accelerate only decorative city/building visibility, preserving complete-scan results. Stationary scenery reuses visibility. The WorldState loop remains global and continues when map draws are disabled. The previous 10 Hz idle policy, live lookup textures and accurate relief-ray cache remain.

121 application checks pass, including off-screen ownership and clock advancement with redraws disabled. Minimal renderer counters show about 70 MiB less texture-plus-buffer payload than .22. Near images retain exact pixels apart from a one-level rounding difference in one Alps channel; distant filtered lighting and the small far sphere have documented minor differences. Native 940MX FPS is unmeasured here. The user confirmed .22 works with lower GPU usage.

The following is the retained .22/.21 foundation:

0.2.0.22 is a changed-files performance patch over GitHub main ca86fe36fd39ea7122c9836933fed091fc99c456 (0.2.0.21). Geography/data stay at 0.2.0.21; application/display advance to 0.2.0.22. See documentation/PATCH_0222.md for installation, tests and console diagnostics. A local change or ZIP delivery does not mean GitHub main was updated.

New rendering behavior: CPU picks share a cached accurate relief intersection, with live membership/ownership reads; GPU sea coverage is a prepared exact R8 mask and CPU sea selection retains IDs; far physical shader skips unused biome/urban reads; graphics quality replaces the existing material array immediately. MapFramePolicy requests full-rate draws on visual changes and a 10 Hz stationary heartbeat, without disabling the main process or WorldState.advance(). Ownership/membership updates explicitly invalidate drawing. Future simulation systems must preserve this separation.

The 0.2.0.22 native performance commands are `perf status`, `perf start [frames]`, `perf stop`, `perf continuous`, `perf auto`. They do not change simulation speed, pause state, frame limit or resolution. Native 940MX/release performance has not been measured here; software timing variance must not be presented as native FPS gains. Earlier review text claiming an unbounded selection cache was incorrect: the cache is capped at 12 entries.

The following describes the retained 0.2.0.21 geography and renderer foundation:

Current patch baseline: confirmed/tested 0.2.0.20, GitHub main d6cc3d76084eca40582adc858cf8e5d9d76c161b. This session delivers the next changed-files ZIP for user testing. Do not infer that GitHub main was updated from a local commit or a ZIP delivery.

Godot 4.5.1 Standard, GL Compatibility. Close Godot before extracting/pulling changes; run Prepare_BunnyWorld.bat and start a fresh campaign. Export a Windows executable when requested. No save-compatibility retrofits.

Current geography: 225 active countries, 1,251 States, 13,310 land provinces. The user confirmed the 55-item consolidation in 0.2.0.20. In .21 Vatican HLS/State 464/province 4478 join Italy/Lazio 534/Rome 4934; global population and land coverage remain unchanged. Old generic State-budget/dispute-protection rules are superseded by these explicit user-approved consolidations.

Canonical footprints are four lossless province-ID PNGs; data/provinces.json assigns provinces to States; world.json owns State/country records. Run tools/build_map.py --godot <Godot executable> after authoring geography. It derives adjacency, border resources, coastal/shared curve fields and render batches together. Never repair ownership changes with per-country masks. A State ownership change needs no geography rebuild.

Runtime MapRendering uploads canonical ID channels as RG8 (CPU picking keeps verified RGB). Its province_texture is RGBA8: State ID in R/G, current owner index in B/A. It is distinct from the offline compatibility province_index.png, whose blue byte remains the local province index. Update the owner lookup only on ownership changes, and membership only on membership changes. Shared smoothed province-pair curves resolve all close-view colours, highlights and lines.

SpatialMapLayers loads offline exact-triangle MeshLibraries for sphere, land/province borders, sea borders and rivers. An 8x4 partition, native frustum culling and conservative horizon culling skip off-screen work. Geometry is not generated on camera motion. Original batches remain available at extreme distance. Chunk resources are losslessly restored from versioned repository parts; their writer saves atomically and loads back every resource.

The .21 comparison improves moving renderer frame times by 13–58% across eight Linux software-rendered views and reduces engine-reported net GPU memory by about 76 MiB. Twelve geography and 33 full-application checks pass. Native Windows/NVIDIA 940MX performance still needs user testing. Source limits and actual checks are in BUILD_INFO.json, TEST_RESULTS.md and documentation/PATCH_0221.md.

Next requested phases, separate from this performance patch: reconcile population to the new States; complete State-specific age/religion/education/economic-activity profiles using regional evidence and reasonable estimates where needed; then test population-informed province allocation before global regeneration. The user accepts a modest province-count increase. Do not leave States without demographics or copy one national profile identically into every State.
