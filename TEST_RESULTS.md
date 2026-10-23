# BunnyWorld 0.2.1.14 validation

## Economy and public services (23 October 2026)

Godot 4.5.1 on Windows, fresh campaign/save schema 29. Native GL Compatibility / NVIDIA GeForce 940MX plus headless validation. Logs, temporary saves and UI captures remain outside the checkout.

- `economy_tests.gd`: **9,930 checks, zero failures**. Covers all 224 countries, preserved starting GDP and fiscal metadata, ten goods, domestic allocation, conserved bilateral quantities/values, bounded prices, automatic supplier matching, cropland food calibration, next-month budgets, gradual service quality, research multipliers and diminishing research-funding returns, food-driven population decline, deficits/interest, full upfront construction payments without a second charge, gradual employment and unchanged inactivity. Strict save/load rejects nine checksum-valid corruptions atomically, preserves GDP, and reproduces subsequent market settlement. Twelve batched months match sequential updates. A ten-year simulation remains finite and loadable; the final measured decade took approximately 82 seconds, not a gameplay frame-rate benchmark.
- `economy_ui_tests.gd`: **26 checks, zero failures** in native GL. Verifies four Economy sections, nine budget controls and next-month submission, inactive Energy, live Research quality, the visible Manufactured Goods card, ten Trade goods and MU labels, green/red population modifiers, healthcare display and smaller-screen budget bounds. Overview, Budget, Trade, construction manufacturing, population tooltip and Society captures were visually inspected.
- Regression passes: model dates/ownership/saves/conservation; research model **2,483**, research UI **1,117**; construction model **2,547**, construction UI **21** native GL; political UI **6,933**; Society model **19,480**, Society UI **44**; state economy model **13,655**, state economy UI **212**; clean globe stability **116**. User-data test paths were redirected only in external temporary copies. Society's long growth check now covers a decade alongside the live monthly economy.
- `build_economy_rules.py` reproduces byte-identical JSON: ten market goods, 23 building definitions and agricultural potential derived from existing prepared terrain/province inputs. These are gameplay coefficients and standardized market bundles, not measured production or tonnes. Electricity and computing remain inactive; deeper effects have reserved connections.
- Repository hygiene: **82 active parts verified, zero unused parts**. No cartography inputs or packed assets changed. `git diff --check` passes. Final feature runs have no script errors; the existing Windows certificate-store warning occurs at startup.

## Agenda, trade and progress (23 October 2026)

Godot 4.5.1 on Windows, fresh campaign/save schema 28. Native GL Compatibility / NVIDIA GeForce 940MX plus headless validation. Logs, rendered screenshots and temporary saves remain outside the checkout.

- `agenda_trade_tests.gd`: **277 checks, zero failures**. Covers deferred law/affiliation application, base and quadratic durations, sequential head-only progress, pause/midnight integration, single upfront PP charge, duplicate/foreign proposal rejection, completion events, active agenda save/load and seven checksum-valid corruptions rejected atomically. Also verifies California's conserved named pool, RU formatting/icons, correct named offices and empty unavailable roles, explicit ruling/coalition IDs, missing political leader fallback, Data Center payment/slot/staffing/completion and building save/load.
- `agenda_trade_ui_tests.gd`: **34 checks, zero failures** in native GL. Verifies full-card research fill below opaque text, tab switching tween/target, Data Center picker, eight resource tabs/read-only ledger, correct offices/government labels, Agenda placement/button timer/fill/opening, completion popups and real-time expiry while paused, research notice expiry, 1024×768 resource selector bounds, sea Escape and reduced urban scales. Research, Government, Agenda, Trade, smaller Trade and completion captures were visually inspected.
- Regression passes: model dates/ownership/saves/corruption/conservation; research model **2,483**, research UI **1,117**; construction model **2,547**, construction UI **21** native GL; political UI **6,933**; Society model **19,480**, Society UI **44**; state economy model **13,655**, state economy UI **212**; compact UI **135**; clean globe stability **116**. Legacy immediate-law assertions now explicitly finish their proposed agendas. Existing user-data test paths were redirected only in external temporary copies.
- Construction, state-economy and leader importers reproduce byte-identical JSON. They retain 22 MD buildings plus one custom Data Center, 13 MD staffing coefficients plus its custom coefficient, all conserved resource totals (800 states with capacity), and starting political leaders in 223 countries. The supplied archive contains no portrait images; 226 matching portraits are imported from a pinned official MD revision, with all runtime PNGs successfully loaded by Godot. The portrait manifest and all 226 PNGs also reproduce byte-identically. Source/output hashes and the full upstream license are retained. Lossless PNG conversion avoids source DDS height warnings. Unsupported conditions and missing leaders are recorded in the import report.
- Repository hygiene: **82 active parts verified, zero unused parts**. No map inputs or packed assets changed; `git diff --check` passes. Final feature/regression runs have no script errors. Existing environment warnings concern Windows's certificate store and saving global editor preferences during headless import.

## State economy and parliament (23 October 2026)

Godot 4.5.1 on Windows, fresh campaign/save schema 27. Native GL Compatibility / NVIDIA GeForce 940MX and headless validation; logs, screenshots and saves remain in an external QA directory.

- `state_economy_tests.gd`: **13,655 checks, zero failures**. Validates all state MD core/claim seeds and country-name references, conserved resource totals/no duplicated source pools, shared inspector/construction slot counts, bounded worker assignments, exact employed conservation, unchanged unemployment/inactivity, MD coefficients, all inactive actions, monthly capacity growth, preserved headroom offsets for inventory-heavy states, staffing-limited construction/output, no output from unstaffed new buildings, save/load reconstruction and atomic invalid-output rejection. Default first-year growth opens an additional slot in **78 states**.
- `state_economy_ui_tests.gd`: **212 checks, zero failures**, native GL. Full visible currency name; restored large Government parliament and 20 Oct 2000 Japanese election date; exact party wedge counts; whole-party hover and union outlines enclosing every belonging seat and excluding others; 83 disabled diplomatic actions with category filtering, scrolling and collapse; MD core/claim flags with country-name tooltips; staffing/resource figures and smaller-window bounds. Overview, highlighted parliament, diplomacy and state screenshots were visually inspected. Rendering review caught and corrected internal polygon seams and a level-counter grid width mismatch.
- Regression passes: model dates/ownership/saves/corruption/conservation; construction model **2,547**, construction UI **21** native GL; political UI **6,932**; compact UI **135** headless; Society model **19,479**, Society UI **43**; research model **2,483**, research UI **1,117**; clean globe stability **116**. The construction GDP assertions now expect current staffing fulfillment. Legacy user-data test paths were redirected only in temporary external copies.
- The state-economy importer reproduced byte-identical data: **1,252 states**, **979 with nonzero mapped resources**, **13 staffing coefficients**, **83 inactive actions**, no omitted resource pools or unresolved rights tags. MD's missing-from-registry Palau record is supplied as inactive metadata. Source quantities use MD game units; no physical reserve/production equivalence or deposit-level accuracy is claimed.
- Repository hygiene passes: **82 active parts, zero unused parts**; no geographic baselines, generated map textures or packed assets changed. `git diff --check` passes. Final model/UI runs have no script errors. The existing Windows certificate-store warning remains; editor import also reports the sandbox's inability to save global editor preferences.

## Society, population and parties (23 October 2026)

Godot 4.5.1 on Windows; fresh campaign/save schema 26. Native GL Compatibility / NVIDIA GeForce 940MX and headless tests. QA files remain outside the checkout.

- `society_tests.gd`: **19,479 checks, zero failures**. All countries share +1% annual growth; paused/same-month calls do not grow population; crossed months compound correctly with fractional residents retained. Counts conserve each chart denominator. Tiny-state growth runs through 2100 and preserves remainders through ownership transfer. Uniform rules, every imported party/outlook, MD Japan names/support, excluded support gaps, exact 1% eligibility, no invented seats, canonical religion aliases/colors, explicit faith selection, one quadratic PP charge, no unfinished effects, save/load and atomic corruption rejection pass. Floating remainders use a 1e-10 round-trip tolerance; seat/population integers remain exact. Century processing was about 6–8 seconds in concurrent QA runs, not a frame-rate benchmark.
- `society_ui_tests.gd`: **43 checks, zero failures**, both headless and native GL. Dedicated toolbar tab, four clickable sections, simultaneous chart grid, compact readable statistic rows, disabled planned controls, monthly refresh, source party details, shared Government/country seats, seat hover, religion selection/single charge, owner-popup cleanup and 1024×768 bounds. Population, attitudes, support, religion-law and smaller-view captures were visually inspected. A collapsed statistic-value width found during review was corrected and covered by layout assertions. Party rows use neutral text with colored markers for readability.
- Regression suites pass: model save/date/territory/conservation; political UI **6,932** checks; research model **2,483**, research UI **1,117**; construction model **2,547**; organizations **132**; compact UI **135** headless assertions; clean globe stability **116**. Legacy test save paths were redirected only in external temporary copies. Tests that directly jump the clock explicitly synchronize monthly population before saving.
- Both importers reproduced byte-identical output: **38 religion source labels / 32 canonical categories**, **224 countries / 4,928 supported party slots**. The archive contains no referenced logo images. Ten unsupported party-history conditions and generic-name/logo fallbacks are recorded in source reports, not silently filled with random support.
- Repository hygiene passes: **82 active parts, zero unused parts**; no packed assets or geographic baselines changed. `git diff --check` passes. The existing environment certificate-store warning occurs at engine startup; final Society model/UI runs have no script errors or leaked world-reference resources.

## Compact UI and map views (23 October 2026)

Godot 4.5.1 on Windows, GL Compatibility / NVIDIA GeForce 940MX. Fresh campaign/save schema 25. Logs, images and temporary saves remain in an external QA directory.

- `ui_improvements_tests.gd`: **137 checks, zero failures**. Covers grouped sequential construction, retained head progress, one ten-factory allocation, completion/reservations, cash and borrowing refunds, grouped save/load and invalid payments/duplicate-group rejection; adjacent/quadratic/nominal law costs and removed Semi-Presidential choices; compact numbers and 224 currency names; readable law tiles, dynamic government titles, compact header opinions with colored tooltips, expanded overview and collapsible owner-scoped actions; larger research window/smaller cards and shrinking to a smaller viewport; compact queue rows and network-level palette/legend; every organization type including empty lists, selector/toolbar separation on smaller screens, all-alliance leader colors, visible alliance labels at geographic centroids, country area-centroid placement, and saved organization filters.
- Rendered screenshots of Government, the country inspector/actions, Research, Construction, the network map and the alliance overview were visually inspected. The network palette assertion permits one 8-bit channel level for texture quantization.
- Existing suites passed: research model **2,483** checks; research UI **1,117**; political UI **6,928**; construction model **2,547**; construction UI **21** with GL; organizations **132**; clean globe stability **116**. `model_tests.gd` passed its date/ownership/save/corruption/conservation checks. Existing test save paths were redirected only in temporary external test copies. Political and construction assertions were updated for the requested layout and grouping semantics.
- `repository_hygiene.py`: **82 active parts verified, zero unused parts**. `git diff --check` passed. Geography, source ownership/population, map contracts and packed assets are unchanged. Godot continues to emit the existing environment certificate-store warning.

Currency names are display metadata, and data centers remain unimplemented with a zero count in the overview breakdown. Diplomatic actions stay disabled. No new economic, demographic, diplomatic or technology effects were added.

## Research (23 October 2026)

Godot 4.5.1 on Windows; fresh campaign/save schema 24. Logs, rendered screenshots and temporary saves are outside the checkout.

- `research_tests.gd`: **2,483 checks, zero failures**. Validates the imported catalog/descending dependency graph, Japan's actual starting unlocks, country differences, prerequisites, university/player identity, duplicate-project rejection, paused/midnight simulation, declining ahead-of-time penalties, independent concurrent projects, preserved work when switching/resuming, completion/unlocks/notifications without pausing or economic effects, save/load of active and unassigned work, and atomic invalid-save rejection.
- `research_ui_tests.gd`: **1,117 checks, zero failures**, including GL Compatibility on NVIDIA GeForce 940MX. Actual pointer clicks switch categories and select a technology after scrolling; the tree closes and assigns the selected university. Also verifies populated categories, chronological node placement, 1440×900 and smaller-viewport bounds, Escape/×/tab cleanup, inherited styling, completion notification/dismissal and freed university slots. Industry, aircraft, selection and notification screenshots were visually inspected.
- Existing `model_tests.gd` passed; `political_ui_tests.gd`: **6,918 checks, zero failures**; `construction_tests.gd`: **2,550 checks, zero failures**; `construction_ui_tests.gd`: **21 checks, zero failures** with GL Compatibility; `clean_globe_stability.gd`: **116 checks, zero failures**. The construction UI's two texture-readback assertions fail with the dummy headless renderer and pass with GL. Legacy test save paths were redirected only in external temporary test copies.
- The importer reproduced byte-identical `data/research.json` on a second run: **1,230 technologies, 11 categories, 224 countries**. Twelve unsupported history conditions are counted and skipped; none contain technology grants. Imported scripts are parsed as data, never executed. See DATA_SOURCES.md for the modern-DLC selection and deliberately inactive special-project gates/effects.
- Repository hygiene: **82 active parts verified, zero unused parts**. No map or packed asset changes. The existing Windows certificate-store warning occurs during Godot startup; no research script errors remain.

## Ocean shader performance (22 October 2026)

- `map_shader_equivalence.gd`: **24 views, zero failures**, Godot 4.5.1 / GL Compatibility / NVIDIA GeForce 940MX at 1440×900. Compared the pre-performance surface shader with the retained ocean optimizations at a fixed animation phase. Covers distant/close political, information and physical maps; selected one-pixel islands; state/province selection and hover; sea highlights; Suez/Bosporus; organizations; construction stripes; deserts, forests, mountains and polar terrain.
- **23 images were byte-identical**. The remaining information-globe image differed in just three channels by one 8-bit level. All comparisons met the documented tolerance; selected one-pixel island images were byte-identical.
- Median of three alternating warmed 40-frame batches, viewport GPU times in milliseconds:

| View | Before | After |
| --- | ---: | ---: |
| Information globe | 11.400 | 11.053 |
| Pacific information | 13.611 | 13.015 |
| Japan coast, physical | 12.615 | 12.754 |
| Amazon, physical | 13.634 | 13.790 |
| Himalayas, physical | 14.993 | 14.658 |

The two ocean-heavy views used approximately 3–4% less GPU time; close terrain results were roughly unchanged, with small differences in both directions. These short, stationary samples do not establish universal FPS gains. A trial biome shortcut was dropped after it repeatedly slowed some terrain views; the original biome calculations remain. The retained changes add no textures/geometry and change no simulation/picking code.

- `clean_globe_stability.gd`: **116 checks, zero failures** during shader work. Repository hygiene: **82 active parts verified, zero unused parts**; `git diff --check` passed. Baseline source, logs, screenshots and detailed timing JSON are in the external QA folder. Environment certificate-store and shader-cache-write warnings occurred, with no shader compilation errors. Pre-existing asset-manifest mismatches listed below remain untouched.

## Source cleanup (22 October 2026)

- Godot 4.5.1 on Windows: `clean_globe_stability.gd` passed **116 checks, zero failures**, both headless and with GL Compatibility on NVIDIA GeForce 940MX. Covers map modes, idle redraws, live ownership, sea selection, immutable travel resources, scenery limits, water-passage picking and simulation independence. The GL run reported no shader errors; this was not a visual comparison or FPS benchmark.
- `model_tests.gd` passed with only its temporary save paths redirected to an external QA folder, because the sandbox cannot write to the normal Godot user-data folder.
- `repository_hygiene.py`: **82 active parts verified, zero unused parts**. `git diff --check` passed. The standalone sandbox, two historical patch packagers, four obsolete detail-patch test scripts and unused shader helpers were retired; useful travel/passage assertions now live in the stability suite.
- Full asset preparation verification remains blocked by pre-existing local generated-file mismatches: `assets/materials/terrain_materials.bwm` differs from its restore manifest and `assets/land_boundaries.res` differs from the map contract. These files were not modified by cleanup or forcibly restored. Godot also reports an environment root-certificate-store warning.

## Construction validation

Godot 4.5.1 on Linux; fresh campaign/save schema 23.

- `construction_tests.gd`: **2,550 checks, zero failures**. All states retain original building counts and receive capacity headroom. Verified MD costs, logarithmic capacity, cash-first/shortfall borrowing, factory allocation cap and Manufactured Goods count, daily progress, paused clock, full/shared slot restrictions, separate network reservations/caps, foreign-state rejection, proportional refunds, no repeated refunds/GDP, completion effects, saved buildings/queue/GDP and atomic invalid-save rejection.
- `construction_ui_tests.gd`: **21 checks, zero failures**. Private mode unavailable in the general picker, actual building-button input and globe-ray click enqueueing, no country-inspector replacement, full-state blue palette, stripe flag upload, state/province visibility, save/load exit, paused idle behavior, tab toggle/Escape/map-switch cleanup and 1024×768 bounds.
- GL Compatibility / Mesa llvmpipe renders visually inspected at **1440×900** and **1024×768**. Queue, factory controls, Treasury deductions, building picker, state fills and queued-state highlighting rendered correctly. Software rendering does not measure target-laptop FPS.
- Existing `model_tests.gd` passed dates, clock, transfers, membership, persistence, corruption rejection and conservation.
- Political UI: **6,918 checks, zero failures**. Research UI: **1,110**, zero failures. Organizations UI: **132**, zero failures.
- Clean globe stability: **52 checks, zero failures**; unchanged stationary-view work and exactly **100 map draws per ten simulated idle seconds**.
- Repository hygiene: **82 active parts, zero unused parts**. No geometry, ownership, state/province IDs, population or initial building counts changed. Only construction gameplay data and a small runtime overlay were added.

No AI construction, manufactured-goods stockpile/market, full employment/energy economy, interest or natural GDP growth is enabled. Native Windows execution and laptop performance remain untested. No Windows EXE exported.

## Previous Organizations validation (0.2.1.7)

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
