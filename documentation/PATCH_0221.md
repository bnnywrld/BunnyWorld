# BunnyWorld 0.2.0.21 — renderer performance and Vatican cleanup

Changed-files source/prepared-resource patch over **0.2.0.20**. No Windows executable is included. Close Godot and the game, extract beside project.godot replacing files, run **Prepare_BunnyWorld.bat**, reopen the project, press F5 and start a **fresh campaign**. Application, geography and display versions should all be 0.2.0.21.

## Changes

- The sphere, land/province borders, sea boundaries and rivers have offline spatial batches. Native frustum culling and conservative horizon checks skip off-screen geometry. All source triangles and curve detail are retained; there is no mesh simplification or texture downscaling. A coarse 8×4 grid limits draw-call overhead on weaker CPUs. Extremely distant views retain the original batches.
- Province identity textures upload exact R/G ID bytes as RG8, eliminating an unused channel and saving 128 MiB before other renderer allocations. Verified RGB source images remain the picking authority.
- The small runtime province lookup now holds State ID in R/G and live owner index in B/A. Boundary reconstruction obtains both from one sample. Ownership events refresh this lookup and the palette; camera movement does neither.
- Camera movement loads no new resources and generates no geometry. Resource creation happens offline or at startup. Prepared batch resources are saved atomically, loaded back for validation and stored in checksum-verified compressed repository parts. Atlas NPZ outputs are also written atomically.
- Vatican country HLS, State 464 and province 4478 are removed. Their population and footprint join Lazio State 534 and Rome Province 4934. The subpixel enclave override, separate outline and country-search entry are gone. Vatican City remains a city in Italy.
- There are now **225 active countries, 1,251 States and 13,310 land provinces**. Global population and land coverage are preserved; no demographic redistribution or province-density redesign is included.

## Controlled renderer comparison

Godot 4.5.1 GL Compatibility on Linux llvmpipe software rendering, 960×600 viewport. Same camera itinerary and 10 measured stationary plus 10 moving frames per view. These results are not native Windows FPS.

| View | Before moving, ms | After moving, ms | Moving frame-time reduction |
| --- | ---: | ---: | ---: |
| minsk political | 155.0 | 86.7 | 44.0% |
| israel political | 161.4 | 82.8 | 48.7% |
| sumatra physical | 174.2 | 75.6 | 56.6% |
| alps physical | 194.2 | 143.7 | 26.0% |
| rome political | 169.9 | 71.7 | 57.8% |
| asia political | 299.0 | 260.1 | 13.0% |
| europe medium | 287.8 | 227.3 | 21.0% |
| globe political | 288.7 | 201.9 | 30.1% |

Both stationary and moving medians improved in all eight views. Engine-reported texture/buffer memory fell by **76.3 MiB net**, including the spatial resources. CPU camera/culling/detail-uniform updates measured 0.041 ms median and 0.069 ms at p95 on this host; this excludes rendering, UI and simulation.

## Verification

33 full-application checks passed, including GPU ownership refresh, State transfer/restoration, physical borders, runtime membership changes, labels, sea selection, sustained camera movement without geometry generation, and former Vatican picking as Rome. Twelve geography checks pass, including a derived-State-atlas comparison with canonical membership.

All batch triangle counts match their source geometry. Eight-view image comparisons pass: mean absolute channel differences stay below 0.031/255, with under 0.16% of pixels differing by more than 8/255 in any capture. Small differences include line-overlap ordering, animated highlights and the intentional Vatican removal; the border curves and terrain detail are retained. Native Windows/NVIDIA 940MX tests remain with the user.

## Test order

1. Keep the same graphics preset and frame-limit setting as 0.2.0.20. In political mode, rotate and zoom over Europe and East Asia; check both distant and close views, including the transitions between them.
2. Switch to physical mode over Sumatra and the Alps. Check coastlines, rivers, mountains and selected-State borders for missing segments or popping.
3. Search Vatican City and inspect its location: it should belong to Italy, Lazio and Rome Province 1 (internal province ID 4934). Vatican must not appear as a selectable country, State or separate province.
4. Console transfer test: `owner 1277 SOV`, then `owner 1277 UKR`. Check political colour and physical national borders update immediately.
5. If a slowdown remains, report location, map mode, zoom, graphics preset, and whether the camera is moving or stationary.

Demographic corrections and population-informed province regeneration remain the next separate stages.
