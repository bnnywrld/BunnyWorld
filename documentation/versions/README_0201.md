# BunnyWorld 0.2.0.1

Private standalone geopolitical globe prototype for Windows 10/11, built with Godot 4.5.1 Compatibility.

Extract the Windows ZIP into a new folder and run BunnyWorld_0_2_0_1.exe. The startup screen and window title show 0.2.0.1. Start a fresh campaign; old-save migration is not supported.

This standalone package embeds the current 0.2.0.1 game in the executable. No external PCK is needed. The archive, folder and executable have distinct versioned names. Validation loads the game data from this actual executable, not a separate pack.

Right-drag to rotate, wheel to zoom, click to inspect. The camera tilts at close range. Click your top-left flag to open country controls. Ctrl+F finds places. Space pauses; 1–4 change speed; F11 toggles fullscreen. The game menu contains graphics, frame-limit, sound and city-scenery settings.

0.2.0.1 replaces streamed geographic image tiles with resident terrain materials and a reusable GPU-displaced close-up grid. Buildings and landmarks are three times their previous display size; cities contain more representative buildings. Landmark labels are removed. Demographics shows all four charts together. Major rivers, Suez/Panama canals and the Bosporus/Dardanelles passages are present; the Black Sea connects to the world ocean.

The 0.2.0 foundation remains: national and State demographic profiles, finances, icon controls, World Ledger and tension baseline. Urban province populations include surrounding countryside; other provinces share a State remainder pool. Growth and later political/economic simulation are still planned.

See RELEASE_NOTES.md, TEST_RESULTS.md, DATA_SOURCES.md and licenses for scope, validation and source details. Native Windows execution and performance on your hardware remain to be tested.

For source builds, open project.godot in Godot 4.5.1. Prepared runtime assets are included. See DEVELOPMENT.md for regeneration and Windows export.
