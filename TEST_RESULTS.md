# BunnyWorld 0.2.0.22 verification

- 63 full-application checks pass, including existing ownership/selection regressions and new picking, sea-mask, quality-switching and diagnostics checks.
- The real main loop advances 60 game hours while viewport redraws are disabled. An ownership change on the hidden hemisphere updates the global owner lookup immediately, wakes rendering, and remains correct when rotating back.
- Every one of the 33,554,432 prepared sea-mask pixels matches the original GPU predicate. Nominal texture payload falls from 96 to 32 MiB. World/province data, canonical land footprints and WorldState code match the base commit byte for byte.
- A separate policy test requests 100 stationary map redraws across 600 application frames at 60 Hz, and all 60 moving frames. Visual changes wake it immediately.
- Eight before/after renderer images have a maximum mean channel difference below 0.027/255. Seven have no pixel changing by more than 8/255; the globe view has 89 such pixels out of 576,000, consistent with animated border glow. Primitive counts are unchanged.
- A focused old/new shader A/B test uses fixed resources and glow phase, covering distant physical terrain, close Alps and a political view. All four old/new shader images are byte-identical. Results and image comparisons are under validation_0222/shader.
- GDScript parsing, Python compilation, prepared resource restoration, geography/display bundles and map-build contracts pass.

All graphical tests use Godot 4.5.1 GL Compatibility on Linux llvmpipe. Separate-process wall timings varied and some were slower; they do not establish target-PC speed or a GPU bottleneck. Controlled shader timings are diagnostics, not Windows/NVIDIA FPS. Native 940MX testing remains necessary. The patch's confirmed benefits are memory payload, operation counts, immediate quality behavior and fewer idle draw requests.

See documentation/PATCH_0222.md for installation, test order and optional native timing capture. App/display: 0.2.0.22; unchanged geography: 0.2.0.21. No Windows executable was exported.
