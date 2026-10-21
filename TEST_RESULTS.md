# BunnyWorld 0.2.1.4 validation

Validated with Godot 4.5.1 on Linux, including GL Compatibility rendering under Mesa llvmpipe.

- Model tests: dates, clock, ownership transfers, overlapping organizations, save/load, corruption rejection and population conservation passed.
- Political UI/runtime: **99 checks, zero failures**, after the final map preparation. Government costs, daily PP, panels and save/load preserved.
- Clean globe stability: **52 checks, zero failures**, headless and GL Compatibility. All eight map modes, zoom uniforms, sea selection, live ownership uploads and independent midnight simulation passed.
- Idle test: **100 map draw requests in 600 application frames at 60 Hz**. Zero additional camera recomputations, view-uniform updates, horizon scans, coverage uploads or terrain uploads while stationary.
- GL render probe: distant political, distant physical and close physical views rendered; zero shader errors. Political, distant physical and close physical screenshots inspected. Software rendering is not a target-laptop FPS benchmark.
- Preparation verification, strict map-build contract and repository hygiene passed. All 82 active packed asset parts verified; no unused packed parts.
- Capital cleanup: **2 tests passed**, including repeat-run safety, current/national-capital and original-city preservation, tiny former capitals sharing a current capital province, and current marker/scenery links.
- Cleanup audit against 0.2.1.3: 42 markers, 42 synthetic clusters and 190 decorative buildings removed. All retained building instances and eight landmarks are unchanged; 2,298 markers and 2,745 clusters remain.
- Province/sea PNGs, world/province JSON, urban population accounting and national/state demographic files are byte-identical to 0.2.1.3. No added textures or mesh geometry.

Removed boundary texture payload: 3072×1536×(1+4+2) = **33,030,144 bytes (31.5 MiB)**, excluding driver overhead. Also removed the invisible 55,296-triangle detail mesh and unused sphere UV2 attributes. Prepared boundaries were regenerated to match shipped generators; canonical geography is unchanged.

Commands: `python tests/obsolete_capitals_tests.py`; `Godot --headless --path . --script res://tests/model_tests.gd`; likewise `tests/political_ui_tests.gd` and `tests/clean_globe_stability.gd`. Run the latter without `--headless` for a rendering-backed check. Then `python tools/restore_repository_assets.py --verify-only`, `python tools/build_map.py --check`, `python tools/repository_hygiene.py`.

Native Windows execution and target-laptop FPS are untested. The fixed sphere remains coarser than the CPU relief sampler at extreme zoom; terrain geometry/picking has not been redesigned in this patch. Earlier version-specific geography tests describe older maps and are not validation evidence for this release.
