# Bunny World 0.2.0.30

Government interface added over **0.2.0.29**: two placeholder portraits flank a neutral 100-seat parliament. Click **Government** in the top toolbar (or **Open government** in your country panel). Five property menus let you preview constitutional form, executive system, political competition, selection rules and distribution of power. Values begin unset; changes are temporary UI choices, retained when reopening the panel and cleared on new/load. No political data, effects or costs are implemented.

Geography and prepared display assets remain **0.2.0.29**: 224 countries, 1,261 states, 13,198 land provinces and 120 sea regions.

## Apply and run

1. Close Godot/game and pull **main** into your existing checkout.
2. Run **Prepare_BunnyWorld.bat**; application must report **0.2.0.30**; geography/display remain **0.2.0.29**.
3. Open with **Godot 4.5.1 Standard**, allow imports and start a **fresh campaign**.

For a new checkout with minimal Git history: `git clone --depth 1 --single-branch --branch main https://github.com/bnnywrld/BunnyWorld.git`.
See [source-control rules](SOURCE_CONTROL.md) before preparing updates.

Government UI interaction checks pass in Godot 4.5.1. See [validation](TEST_RESULTS.md). Native Windows visuals/performance remain the user test. No EXE is included; see [export instructions](documentation/EXPORT_WINDOWS.md).

Controls: right-drag rotate; wheel zoom; left click inspect; Space pause; 1–4 speed; Ctrl+F search; F focus; F5/F9 same-version save/load; F11 fullscreen; Escape menu.
