# Bunny World 0.2.1

Compact Government and country interfaces, with political power spending and daily income.

- Government is 600px wide. Click a property card to open its small choice window; changing a setting costs **100 PP**. The current setting cannot be charged again and unaffordable choices are disabled.
- Country control and diplomacy show smaller portrait placeholders and a neutral 100-seat parliament above a compact stats grid. Click your own parliament to open Government; foreign parliaments are read-only.
- Political power remains in the top bar. Every completed day gives **+1 PP**. Hover to see the daily total and its actual sources, with positive values green and negative values red.
- Chosen government settings and PP balances persist in saves. Leaders, real party allocations and election dates remain placeholders. Government choices currently affect only the selected setting and the one-time PP cost.

## Apply and run

1. Close Godot/game and pull **main** into the existing checkout.
2. Run **Prepare_BunnyWorld.bat**. Application reports **0.2.1**; unchanged geography/display report **0.2.0.29**.
3. Open with **Godot 4.5.1 Standard**, allow imports and start a **fresh campaign**. This release uses save schema 18; older saves are unsupported.

See [validation and test order](TEST_RESULTS.md), [source-control rules](SOURCE_CONTROL.md), and [Windows export instructions](documentation/EXPORT_WINDOWS.md). No EXE or new binary map assets are included. Map remains 224 countries, 1,261 states, 13,198 land provinces and 120 sea regions.

Controls: right-drag rotate; wheel zoom; left click inspect; Space pause; 1–4 speed; Ctrl+F search; F focus; F5/F9 same-version save/load; F11 fullscreen; Escape menu.
