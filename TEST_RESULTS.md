# BunnyWorld 0.2.0.12 validation

- 172 headless interface checks and 173 graphical checks, zero failures. The graphical suite includes a real on/off pixel-difference check confirming the country names are visibly rendered.
- Fixed world-space sizes through zoom; no camera-triggered text-geometry rebuild or geographic reread. Ownership changes rebuild the name layout once.
- Summary cards, profile disclosures, all demographic tabs, pinned headings, active shortcut state, larger combined header and selection breadcrumbs pass.
- Actual GUI wheel/drag dispatch: UI scrolling stays within panels; the exposed map remains interactive. Sweden/Åland owner-palette checks retained.
- 55,782 prepared-display checks, zero failures. All 1,360 State and 13,594 province coverage records are valid and nonempty; declared centers have positive selection coverage. Local coast windows and the tiny-island bit map also validate.
- All 397 original geographic/simulation/generation/prepared-asset source files are byte-identical to the working 0.2.0.11 baseline.
- Resource restoration regression tests, mixed display/geography rejection, checksum verification and resource loading pass. Editor import passes.
- Reviewed GPU captures: North America, Europe, Japan command bar, Tokai Province 9 and 1100×700 layout.

## Performance evidence

The same camera-path CPU test measures the old 0.2.0.11 label fitting loop at **44.98 ms median** per update. The new explicitly forced visibility pass measures **0.444 ms median**, **0.795 ms p95**. Normal cached update calls have a 1 microsecond median in this environment. These are label-update CPU timings, not overall FPS.

An earlier integration-stage full-frame on/off sweep uses Linux Mesa llvmpipe software OpenGL at 1440×900. Its frame times vary widely, including between repeated names-off passes; no native-GPU frame-rate improvement is asserted from that sweep. Raw measurements are included for transparency. Windows/NVIDIA performance needs the user's local comparison with Aa enabled/disabled.

## Limits

Selection coverage is substantially smoother, but some fine coast/border alignment and tiny-island display artifacts remain at extreme zoom. The patch does not add surveyed geographic detail or change picking IDs. New display memory includes a 32 MiB coast field, a 16 MiB tiny-island bit map, approximately 5.3 MiB of glyph atlas/mipmaps and a bounded selection/coast cache.

No Windows executable export or old-save migration. The earlier report of 32 debugger entries remains unreproduced. Fresh overlay installation over a clean 0.2.0.11 source base passes preparation, import and resource loading; all delivered hashes match. Results are in validation_0212/install_results.json.

Guide and playtest order: documentation/VISUAL_0212.md.
