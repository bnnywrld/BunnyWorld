# BunnyWorld 0.2.0.20 — State consolidation and map performance

This ZIP is a combined changed-files patch. Apply directly over **0.2.0.18 or 0.2.0.19**. Close Godot/the game, extract beside project.godot replacing included files, run **Prepare_BunnyWorld.bat**, reopen the project, press F5 and start a **fresh campaign**. No new Windows executable is included. Application/display version 0.2.0.20 and geography version 0.2.0.19 are the intended pairing.

All 55 State requests are included; [the complete merge/rename list](PATCH_0219.md) documents the destinations. There are 1,252 States, 13,311 land provinces and 226 active countries. Global population and land coverage are preserved.

## Rendering changes

- Close views skip the full global land/province border meshes whenever their existing shaders make them entirely invisible. A separate 120-triangle enclave ribbon preserves the Vatican boundary. Meshes are prepared once; camera travel changes visibility only.
- Political land reuses the colour already computed by the universal shared boundary field, avoiding four legacy reconstructions whose result was immediately overwritten. Information map modes retain their interpolation.
- The central province ID is decoded once. Empty boundary cells skip unused neighboring pair reads.
- Junction reconstruction retains its exact categorical/curve calculations with smaller temporary shader storage. Colours, highlights and live ownership use the same boundary curves as before.
- The automatic map builder produces the enclave mesh and versioned contracts for future geography changes; the unchanged sea mesh no longer requires its absent authoring binary.

## Controlled comparison

Production map renderer at 960×600, Godot 4.5.1 GL Compatibility, Linux llvmpipe software rendering. Same geography, viewport, cameras and 12 measured frames per view. These are renderer frame times on this host, **not native Windows FPS**.

| View | Before, ms | After, ms | Median frame-time reduction |
| --- | ---: | ---: | ---: |
| minsk political | 310.9 | 145.7 | 53.1% |
| israel political | 326.9 | 160.3 | 51.0% |
| sumatra physical | 387.6 | 151.0 | 61.0% |
| vatican political | 247.9 | 145.1 | 41.5% |
| asia political | 369.6 | 285.2 | 22.8% |

Close-view submitted primitives fall from 2,208,168 to about 844,810, a 61.7% reduction. Same-camera image comparisons show no pixels changing by more than 8/255 in four views; the Vatican capture has three such pixels. Small differences are confined to the animated highlight. Border coverage and smoothing are retained.

## Test order

1. Start a fresh campaign; check the title says 0.2.0.20. Use political mode, zoom and rotate over Europe, Israel, Korea and Indonesia. Compare responsiveness with 0.2.0.18.
2. Switch to physical mode over Sumatra/Cyprus and check selected-State edges and coastlines.
3. Check Minsk, Crimea, Swiss Zürich/Eastern Switzerland, Bremen, Monaco/France, Sinai Province 14, Duhok/Sulaymaniyah/Herat/Chechnya, Wa State and Mindanao.
4. Check South Island/North Island, the Caribbean/Brazilian fragments and remote island destinations listed in PATCH_0219.md.
5. Open country/territory panels, switch States/provinces and rotate with country names enabled. If lag remains, report map mode, zoom and whether it happens with the camera stationary or moving.

Native Windows/NVIDIA 940MX performance remains unmeasured. The five-view comparison isolates map rendering; full-game performance also depends on UI, scenery and the simulation.
