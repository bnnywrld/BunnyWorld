# 0.2.0.7 technical verification

- **45,364 geography checks passed**, zero failures: country State budgets and authorized exceptions; exact country-controller/coast coverage; population/building conservation; province/state/texture IDs; capitals and cities; symmetric neighbor graph; no substantial disconnected province pieces on the same landmass; MD country density budgets; all 99 protected feature identities; future-dispute ownership probes.
- **66 Godot integration checks passed**, zero failures: startup/fresh campaign, selecting and picking rebuilt States/provinces across 18 countries, search, territory drawer and same-version persistence. Recorded in validation_0207/source/integration_results.json.
- **58 UI regression assertions passed**, zero failures. Recorded in validation_0207/source/ui_results.json.
- Model, foundation/population accounting, territorial-rights and resource-loading suites passed under Godot 4.5.1 headless.
- Preparation regression checks passed: known previous-version automatic refresh, verify-only, preservation of unknown custom resources, explicit force, and mismatched-bundle rejection. Current resource and geography-bundle hashes verified.
- Offline regional and orthographic views of the final categorical atlases were generated and inspected. These are map diagnostics, not screenshots from native Windows rendering.

Final data: 223 countries, 1,405 States, 13,261 land provinces versus MD's 13,221. National population remains 6,144,737,528. Local demographic estimates were not refined.

**No Windows executable was exported or run.** Native Windows visual correctness, practical zoom readability, GPU performance and subjective quality remain the user's Godot playtest.
