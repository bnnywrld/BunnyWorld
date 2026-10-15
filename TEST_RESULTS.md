# BunnyWorld 0.2.0.10 validation

- 38,846 geography checks, zero failures; 84 independent coordinate probes.
- 134 headless and 134 graphical interface checks, zero failures.
- Actual GUI event dispatch verifies panel scrolling, blocked globe zoom, exposed-map zoom and drag suppression. Owner palette values match Sweden and Finland's state owners.
- All 13,594 province IDs retained. No uncovered land, invalid state parents or substantial disconnected province pieces on the same state landmass.
- Tasman Sea and West Polynesia each form one component across the date line. Every prior land/lake mask is retained.
- State/province population accounting, buildings, city/scenery references and symmetric adjacency pass.
- Prepared-resource restore regressions, resource loading, editor import and bundle checksums pass.
- Six globe projections and 18 regional views reviewed; Pacific water boundaries inspected separately.
- Graphical Godot 4.5.1 test: Linux, Compatibility, Mesa software OpenGL. No game errors. One environment warning reports unavailable V-Sync switching in the virtual display.
- The user's 32 debugger entries were not reproduced and are not claimed fixed. Native Windows/NVIDIA behavior and performance are not verified. Capture_Debug_Log.bat is supplied for follow-up.
- ZIP overlay tested against a clean archive of GitHub 0.2.0.9: every delivered hash matched; preparation, clean editor import and resource loading passed.
- No Windows executable export or old-save migration.

Raw regression results and selected offline map review images are in validation_0210.
