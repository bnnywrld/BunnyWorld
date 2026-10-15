# BunnyWorld 0.1.12 revision 2 validation

- Place catalog checks pass for cities, states, countries, metropolitan groups, landmarks, accents and country-qualified queries.
- Actual scene checks pass for modal search, camera navigation, pause restoration, camera/picking agreement, and preserving the player country.
- Urban and shared-pool tooltips explain their population scope. Menu suppression and tooltip bounds pass. Search and the settings menu fit the minimum supported window size.
- The scenery toggle clears nearby buildings, landmarks and landmark labels. It preserves city labels and population information. Preferences survive sound changes and a subsequent app launch; the final restart screenshot confirms the disabled toggle.
- Refined CPU/GPU relief channels agree. The accepted coast/lake mask is retained; land lift is about 80 metres with a smooth inland taper and four-times mountain exaggeration. Finite atlas resolution can still produce visible coast steps.
- The Vatican coarse patch is restored to Italy around an approximate 60-vertex reference polygon. Identity count, focus, graph adjacency, surface fill and picking checks pass. Vatican remains selectable; the Colosseum selects Italy. The nominal official 0.44 km² area is distinct from the approximate 0.512 km² reference geometry.
- All-state and all-group population accounting passes. Urban province residents include their countryside; non-city provinces share a state pool. All country totals and the global total of 6,144,737,528 remain unchanged. There are 2,220 urban provinces, 1,557 groups and 1,735 linked city markers.
- Ownership transfers, debug edits, save/load, reset, corruption rejection, model, relations, territorial rights and terrain cache checks pass. Province IDs, territorial rights and state infrastructure are retained.
- The exact final Windows PCK passes UI smoke plus search, small-window search, urban tooltip, rural tooltip, small-window settings, Vatican, Rome, Sydney, scenery-off and restart views. No shader/script/resource errors were logged; the software driver reports unsupported V-Sync. Screenshots were inspected.
- The earlier 0.1.12 landmark-model checks are retained in verification_022. Updated evidence is in verification_022r2. Windows executable and PCK together remain below 400 MB; final ZIP CRC and SHA-256 checks run during packaging.

The native Windows executable and performance on the user's hardware remain untested. Population values are year-2000 GHSL-based estimates reconciled to supplied national totals, not exact census district boundaries. The Vatican reference is approximate rather than cadastral. Start a fresh campaign; old-save migration is not included.

Population growth, migration, demographic categories and politics remain planned for 0.2.
