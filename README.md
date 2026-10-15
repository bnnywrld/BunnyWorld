# BunnyWorld 0.2.0.6 — Geographic States and Provinces

Windows 10/11 x64 standalone. Extract the entire ZIP into a fresh folder and run **BunnyWorld_0_2_0_6.exe**. No editor, installer or separate pack is needed. Start a fresh campaign.

This release replaces distorted MD-derived subdivisions with real geographic administrative boundaries grouped into **2,107 States** and **9,194 independently generated provinces**. All **223 existing countries** retain their accepted scenario territory.

Small neighboring administrative units and island groups are consolidated. US states, German federal States and Polish voivodeships remain recognizable. Provinces use local equal-area calculations, administrative boundaries, settlements, relief and rivers. Sparse desert and polar interiors have much larger provinces. The political map remains the clearest testing mode.

Local demographics have not been refined. National totals are retained for the running game; local allocations are temporary. Modern administrative data supplies geographic reference shapes; existing year-2000 country control remains authoritative. This is not an exact historical administrative atlas for January 2000.

The 0.2.0.5 interface is retained: compact controls attached to the top, a half-height territory drawer with an attached collapse arrow, inline demographic selectors and wide-window support. Terrain artwork and rendering architecture are unchanged.

Controls: right-drag rotate; wheel zoom; left click inspect; Space pause/resume; 1–4 speed; Ctrl+F/search icon find places; F focus; F5/F9 save/load; F11 fullscreen; Escape menu. Click your flag for country control.

Source checkout: run `python tools/restore_repository_assets.py`, then open `project.godot` in Godot 4.5.1 stable. All prepared resources are included through lossless repository parts. See DEVELOPMENT.md and TEST_RESULTS.md.
