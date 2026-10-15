# Bunny World 0.2.0.3

Windows 10/11 x64 standalone. Extract the complete ZIP into a fresh folder and run **BunnyWorld_0_2_0_3.exe**. The game is embedded in that executable; no editor, installer or separate PCK is needed. The main menu/window identify 0.2.0.3. Start a fresh campaign.

Start and Play now open Physical Earth. Hover over land for the country flag/name and, up close, its province population estimate. Map modes and same-version save/load remain available. Old-version save migration is intentionally unsupported.

This patch refines geography, province density, physical-map borders, terrain repetition, river width/banks, city ground scale and province population accounting. See RELEASE_NOTES.md for the complete changes and known approximations. TEST_RESULTS.md distinguishes automated Linux/Godot checks from native Windows testing.

Graphics quality selects a fixed 2048 (Light) or 4096 (Balanced/High) material library at the next launch. Camera travel reuses resident textures and prepared meshes. Initial loading prepares scenery and graphics; smooth travel takes priority over short startup.

Source users: open project.godot with Godot 4.5.1 stable, GL Compatibility. Prepared runtime assets are included. External raw geographic downloads and the user-supplied mod are required only for full regeneration. Read DEVELOPMENT.md.
