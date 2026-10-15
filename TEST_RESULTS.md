# BunnyWorld 0.2.0.6 verification

## Passed

- Whole-world geography validation: **34,010 checks, zero failures**. Every land pixel belongs to a province in its State; all 223 country-control footprints match the accepted baseline; all referenced IDs exist; State/province focus points, capitals, neighbor symmetry and native identity textures agree. No substantial disconnected province pieces remain on the same landmass. Geographic reference probes and small-country State limits pass.
- Source game: **66 geography integration checks**, zero failures. Fresh campaign; new State/province inspection; picking at representative State focus points in 18 countries including Vatican City; territory drawer; search; same-version save/load.
- Source game: **58 interface regression checks**, zero failures. Compact controls, State and national selectors, own/foreign drawer positioning and collapse, normal/wide/ultrawide/minimum window layouts, search and selection.
- Matching Linux runtime loading the actual exported Windows EXE: the same **66 integration and 58 interface checks**, zero failures. Embedded project version/scenario/resources validated.
- Model, foundation, territorial-rights and resource-load suites passed: clock/calendar, ownership transfers, country totals, organizations, current-version persistence, invalid-save rejection and prepared resources.
- Exact categorical atlas reviewed in regional and orthographic diagnostic images. Native-grid repair reassigned 12,334 sampling-fragment pixels, split 15 disconnected pieces and absorbed 12 tiny provinces. Final counts: 223 countries, 2,107 States, 9,194 provinces.
- Official Godot 4.5.1 x64 Windows template; embedded PCK footer, PE section location and directory validated. Build identity and hashes are recorded in BUILD_INFO.json.

## Limits

Engine interaction/layout tests ran with the headless display server. Atlas diagnostics are offline visual reviews, not screenshots of the Windows renderer. Native Windows launch, hardware graphics and frame-time performance have not been tested in this environment.

The country-control mask is preserved from the accepted game scenario; this patch does not independently audit every international boundary. Natural Earth administrative shapes are contemporary geographic references, not an exact year-2000 administrative atlas. Local demographic accuracy is deferred; retained national totals and temporary local bookkeeping keep the game running. Test with a fresh campaign.
