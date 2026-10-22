# BunnyWorld 0.2.1.7 validation

Godot 4.5.1 on Linux; fresh campaigns/save schema 22.

- `organizations_tests.gd`: **132 checks, zero failures**, including actual card pointer input; default player-only cards; all eight types/44 definitions; 19 unchanged member arrays; status/opt-out queries; exclusive alliance validation; metadata/status/save round-trip; dated names; member/features tabs; inactive-directory isolation; HQ-only markers; no fake seat for rotating forums; nonmember HQ hosts; city-marker restoration; no national-city scan in HQ mode; tab cleanup; and 1024×768 bounds.
- GL Compatibility/Mesa llvmpipe rendered and visually inspected the membership cards, Features tab and EU headquarters marker at 1024×768. Capitals/city labels are absent in organization mode. This is software-renderer validation, not laptop FPS measurement.
- `model_tests.gd`: passed dates, clock, ownership, memberships, save/load, corruption rejection and population conservation.
- `political_ui_tests.gd`: **6,918 checks, zero failures**.
- `research_ui_tests.gd`: **1,110 checks, zero failures**.
- `clean_globe_stability.gd`: **52 checks, zero failures**, including exactly 100 idle map draws across ten simulated seconds and no stationary camera/uniform/coverage work.
- `tools/repository_hygiene.py`: **82 active parts verified, zero unused parts**.
- Canonical map/geography, membership arrays, populations, laws and research mechanics unchanged. No organization PP/opinion/economic/military effects activated; all unbuilt actions are marked Planned.

Native Windows execution, Windows export and target-laptop FPS remain untested. No EXE is included.

## Previous research UI validation (0.2.1.6)

Godot 4.5.1 on Linux. Research and law-window UI only; save schema remains 21.

- `research_ui_tests.gd`: **1,110 checks, zero failures**. Actual pointer events open/switch law pickers and open university trees; Escape/close buttons, tab-toggle cleanup, one-window lifecycle, deterministic 2–6 institution slots for all 224 countries, and smaller viewport bounds passed.
- `political_ui_tests.gd`: **6,918 checks, zero failures**. All law choices, 100 PP costs, insufficient funds, no-effect behavior, daily PP, country defaults and save/load validation remain covered.
- `model_tests.gd`: passed dates, clock, ownership, memberships, save/load, corruption rejection and conservation.
- GL Compatibility / Mesa llvmpipe: law picker, direct replacement, institution list and empty tree rendered and inspected at 1440×900 and 1024×768. Compact law-window and tree dimensions also pass checks after layout settles.
- Repository hygiene: 82 active packed parts verified, zero unused parts.
- No map assets, demographics, saved research state or simulation rules changed. Research trees are empty and have no effects or timers.

Native Windows execution and target-laptop FPS remain untested.

## Previous Constitution & Laws validation (0.2.1.5)

Validated with Godot 4.5.1 on Linux. Fresh campaigns; save schema 21.

- Political UI/runtime: **6,918 checks, zero failures**. All 224 countries have 28 valid starting laws; six compact categories, derived government title, option selection, 100 PP deductions, repeated/current-choice rejection, insufficient funds and foreign-country protection passed.
- Every law popup opens, fits the viewport and shows its choices. All available options are accepted by the shared purchase path. Non-PP starting stats, daily modifiers, map ownership and population stay unchanged.
- Daily PP and multi-day increments, pause behavior, live affordability, save/load round trips and transactional rejection of corrupted political data passed.
- Model suite passed: dates, clock, ownership transfers, organization memberships, save/load, corruption rejection and population conservation.
- GL Compatibility / Mesa llvmpipe: Government top, scrolled lower categories, choice popups and 1024×768 layout rendered and visually inspected; default 1440×900 also inspected. This is software-rendered layout validation, not target-laptop FPS measurement.
- No map assets, packed resources or demographic data changed in this patch. No Windows EXE exported or native Windows execution performed.

Commands: `Godot --headless --path . --script res://tests/model_tests.gd`; `Godot --headless --path . --script res://tests/political_ui_tests.gd`; `python tools/repository_hygiene.py`.

The starting policy data uses broad scenario abstractions; it has not received a comprehensive country-by-country historical legal audit.

## Previous map validation (0.2.1.4)

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
