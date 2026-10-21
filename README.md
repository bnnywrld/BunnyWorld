# Bunny World 0.2.1.3 — clean globe stabilization

Use branch **clean-globe**. The new globe is connected to the existing country panels, politics, demographics, eight map modes and save system. Current map: **6144×3072**, **224 countries, 1,252 states, 13,074 provinces and 784 sea regions**.

This patch removes the invisible legacy detail mesh, unused boundary texture uploads (31.5 MiB), unused local coast selection uploads and repeated camera/view-uniform work while stationary. Coastal shading skips ocean-neighbor texture taps outside the bands that use them. Idle map drawing remains 10 Hz; movement/selection responds immediately and simulation runs independently.

Close Godot/game, pull **clean-globe**, run **Prepare_BunnyWorld.bat**, then open **project.godot** in **Godot 4.5.1 Standard**. Application version: **0.2.1.3**; geography/display bundle: **0.2.1.2**. Use a fresh campaign for testing. No EXE is included.

Prepared boundary resources have been rebuilt from the existing canonical map with the checked-in tools to repair stale build provenance. Province/sea PNGs, ownership, population, state/province IDs and demographics are unchanged. Packed assets are required; preparation verifies them before opening the game.

See [validation](TEST_RESULTS.md), [development](DEVELOPMENT.md), and [Windows export instructions](documentation/EXPORT_WINDOWS.md). Windows/laptop FPS remains unmeasured.

Controls: right-drag rotate; wheel zoom; left click inspect; Space pause; 1–4 speed; Ctrl+F search; F focus; F5/F9 save/load; F11 fullscreen; Escape menu.
