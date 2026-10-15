# BunnyWorld 0.2.0.4 handoff

Use bunny_world_v0_2_0_4_source_STANDALONE.zip for further implementation and bunny_world_v0_2_0_4_windows_STANDALONE.zip for Windows testing. Historical 0.1 attachments are not the development baseline.

This is the complete 0.2.0.3 game plus the requested compact UI refinement. Read RELEASE_NOTES.md, DEVELOPMENT.md, TEST_RESULTS.md and BUILD_INFO.json. UI tests are tests/ui_0204_tests.gd; full smoke remains in scripts/main.gd. A matching Linux runtime has rendered and tested the exact exported game; native Windows performance still requires the user's test.

Campaign layout: boxed national stats above flag/navigation; no country-name/playing-as/footer text; larger 46×46 national buttons aligned with the flag; compact icon clock/search controls. Capitals appear at distance 1.65 instead of 2.5. Territory State/province information is in a 260-pixel scrollable drawer to the right of diplomacy or beside own-country control. Closing/changing the parent hides the drawer. Tooltips measure current text and wrap long details to 280 pixels.

Application/EXE version is 0.2.0.4. The unchanged geographic scenario ID remains bunny_world_2000_0_2_0_3, save schema 10. Counts remain 223 countries, 1,233 States, 13,481 provinces, 6,144,737,528 residents. No old-save migration or compatibility work is authorized; the user tests fresh campaigns. No world-state or terrain scripts/resources were changed.

Standing constraints: smooth travel takes priority; longer startup is acceptable. Preserve the resident eight-layer material array, fixed terrain grid and cached scenery meshes. Do not add camera-triggered geographic image decoding, material uploads, grid rebuilding or scenery regeneration. Budget approximately 500 MB runtime; distinguish EXE/runtime, compressed ZIP and VRAM. No demographic growth/annual scenery growth until authorized. Keep all four demographic charts together and retain city-label priority.

Retained 0.2.0.3 limitations: approximate game-scale registration/coastline/elevation, reconciled province population estimates, representative scenery/materials, importance-based river widths and limited trial river channels. Prior geographical regeneration notes are under documentation/versions/0_2_0_3. Follow the user's next feedback; do not start unrelated simulation patches from older roadmaps.
