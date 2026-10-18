# Bunny World 0.2.1.2

One **8192×4096 province PNG** replaces the four-quadrant land map. Large shared border/coast lookup fields are also smaller. All 224 countries, 1,259 states, 13,197 provinces and 120 seas remain. Five tiny states are enlarged for visibility; inhabited islands are protected. Residents, demographics, physical areas, ownership and government/PP behaviour are unchanged.

Nominal province/border/coast/tiny-island GPU texture payload: **560 → 140 MiB**. This is a buffer-size calculation; target-laptop FPS is unmeasured. Terrain texture resolution is retained.

Close Godot/game, pull main (or apply the changed-files patch over **0.2.1.1**), run **Prepare_BunnyWorld.bat**, then open **project.godot** in **Godot 4.5.1 Standard** and start a **fresh campaign**. All preparation versions should be **0.2.1.2**. Save schema 20; old saves unsupported.

See [changes, small places and comparison steps](documentation/MAP_EDITS.md), [validation](TEST_RESULTS.md), and [Windows export instructions](documentation/EXPORT_WINDOWS.md). No EXE is included. New editable maps are three full-size PNGs rather than nine files.

Controls: right-drag rotate; wheel zoom; left click inspect; Space pause; 1–4 speed; Ctrl+F search; F focus; F5/F9 save/load; F11 fullscreen; Escape menu.
