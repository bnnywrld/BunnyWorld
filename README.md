> **Git checkout:** see [SOURCE_CONTROL.md](SOURCE_CONTROL.md) to restore the external map/texture assets before opening Godot. Normal Windows ZIP testing needs no setup.

# Bunny World 0.2.0.4

Windows 10/11 x64 standalone. Extract the complete ZIP into a fresh folder and run **BunnyWorld_0_2_0_4.exe**. The complete game is embedded; no editor or installer is needed. Start a fresh campaign.

This release refines the interface on the complete 0.2.0.3 terrain/world baseline. National stats have individual boxes above the flag and larger aligned navigation buttons. The name/playing-as text and bottom bar are removed. State and province details open in a narrow drawer to the right of diplomacy (or beside your own country panel). Close it with ×. Hover tooltips fit their text, search uses a magnifying glass, clock controls are compact, and capital labels appear at a closer zoom.

Controls: right-drag to rotate; mouse wheel to zoom; left click to inspect; Space to pause/resume; 1–4 for speed; Ctrl+F or the magnifying glass to find places; F to focus; F5/F9 to save/load; F11 fullscreen; Escape menu. Click your flag for country control. Planned national mechanics remain disabled as before.

Graphics quality selects a fixed Light 2048 or Balanced/High 4096 material library at launch. Travel reuses resident textures and prepared scenery. Initial loading can take time. No old-save migration is provided.

See RELEASE_NOTES.md and TEST_RESULTS.md. Source users: open project.godot with Godot 4.5.1 stable, GL Compatibility. Prepared runtime assets are included; full geographic regeneration remains documented in documentation/versions/0_2_0_3/DEVELOPMENT.md.
