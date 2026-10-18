# Bunny World 0.2.0.29

User map edits integrated over **0.2.0.28**: **224 countries, 1,261 states, 13,198 land provinces, 120 sea regions**. State borders take priority; province IDs are preserved except two fully erased tiles. All cities remain. Sea borders, neighbours and highlights rebuild from current IDs. Population is state-only.

## Apply and run

1. Close Godot/game and pull **main** into your existing checkout.
2. Run **Prepare_BunnyWorld.bat**; application/geography/display must all report **0.2.0.29**.
3. Open with **Godot 4.5.1 Standard**, allow imports and start a **fresh campaign**.

For a new checkout with minimal Git history: `git clone --depth 1 --single-branch --branch main https://github.com/bnnywrld/BunnyWorld.git`.
See [source-control rules](SOURCE_CONTROL.md) before preparing updates.

101,898 data checks and 42,073 Godot headless checks pass. See [report and test order](documentation/MAP_EDITS_0229.md). Native Windows visuals/performance remain the user test. No EXE is included; see [export instructions](documentation/EXPORT_WINDOWS.md).

Controls: right-drag rotate; wheel zoom; left click inspect; Space pause; 1–4 speed; Ctrl+F search; F focus; F5/F9 same-version save/load; F11 fullscreen; Escape menu.
