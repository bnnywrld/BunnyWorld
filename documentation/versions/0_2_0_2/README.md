# BunnyWorld 0.2.0.2

Extract the Windows ZIP into a new folder and run **BunnyWorld_0_2_0_2.exe**. The current game is embedded in that executable; no editor, installation or external PCK is needed. Start a fresh campaign. Same-version saves work; older campaigns are not migrated.

This patch adds sharper close-up terrain, stronger mountain relief, smoother physical shore coverage, Antarctic ice and terrain, more and wider rivers, and a new irregular province layout adapted from Millennium Dawn. Cities have approximately twice as many representative buildings, laid out in spaced street blocks with clear grounds around landmarks. Landmark labels stay hidden.

Right-drag rotates the globe; the wheel zooms. The camera tilts at close range. Click to inspect, click your top-left flag for country controls, and use Ctrl+F to find places. Space pauses, 1–4 changes speed, and F11 toggles fullscreen.

The game menu offers graphics, frame-limit, sound and city-scenery settings. Balanced/High use the sharper 4096-square materials; Light uses 2048-square materials. **Changing terrain texture quality takes effect after restarting the game.** Anti-aliasing changes immediately. All selected terrain materials and city meshes load behind the startup progress screen and remain cached during travel.

The year-2000 scenario retains 223 countries, 1,235 States and 6,144,737,528 residents. There are now 13,204 land provinces, 117,367 representative buildings and 350 named river entries. City provinces include surrounding countryside; other provinces share their State's remaining population pool. Population growth remains postponed.

The 0.2 foundation—demographics, finances, country controls, rights, World Ledger and tension baseline—remains. Read RELEASE_NOTES.md and TEST_RESULTS.md for details. Automated validation uses Godot 4.5.1 on Linux/Mesa; performance on your Windows hardware still needs testing.

For source development, open project.godot in Godot 4.5.1 Compatibility. All prepared runtime assets are included; DEVELOPMENT.md explains rebuilding them.
