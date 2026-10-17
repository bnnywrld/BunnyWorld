# BunnyWorld 0.2.0.23 verification

121 full-application checks pass with zero failures. Existing accurate picking, live owner/membership, off-screen transfer, disabled-redraw clock advancement and settings tests remain, with new mode-switching, decoration-index equivalence, stationary reuse, hover coalescing, and geometry/cache-residency checks.

Eight 960×600 production-renderer views were compared against the confirmed 0.2.0.22 source. Near political pixels match exactly; the close Alps image has a single channel differing by 1/255. Distant physical lighting uses filtered cached normals/snow and has a maximum mean difference below 0.30/255; the far sphere changes a small number of silhouette pixels. No country/state/province data or canonical footprints changed.

Engine texture-plus-buffer counters show a net 70.053 MiB reduction, including the 32 MiB mipmapped cache. City/scenery queries match full scans while testing fewer candidates; stationary scenery stops rescanning, and forty mouse-motion events yield one latest-position hover query.

GDScript parsing, Python compilation, prepared asset checks, geography/display and cache-source contracts pass. WorldState, world/province data, canonical province rasters and original relief data match the 0.2.0.22 baseline.

All graphical measurements used Godot 4.5.1 GL Compatibility on Linux llvmpipe. Wall timings varied; no target-GPU FPS gain is claimed. See validation_0223 and documentation/PATCH_0223.md. App/display .23, geography .21. No Windows executable was exported.
