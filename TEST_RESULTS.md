# BunnyWorld 0.2.1 verification

99 Godot 4.5.1 integration checks pass at a 1100×700 window: compact country-stat order, own/foreign parliament actions, property buttons/modal choices, every valid property option, exact 100 PP charges, same-option/invalid/foreign rejection, insufficient/exact balances, affordability refresh, pause/midnight/multiple-day income, all four game speeds, positive/negative modifier totals and colored tooltips, new-schema save/load, invalid political-save rejection and fresh-campaign reset.

Political actions leave map/state data untouched. JSON save round trips preserve workforce rates within 1e-10 (the existing JSON serializer rounds floating point values). Prepared assets, geography/display bundles and map build contract verify unchanged. Linux GL Compatibility visuals inspected for Government, property window, country control, diplomacy and PP tooltip. Native Windows performance/visuals remain untested.

## Short player test

1. Pull main, run Prepare_BunnyWorld.bat and start a fresh campaign. Application is 0.2.1, geography/display .29.
2. Open your country: portraits and parliament precede the smaller stats; there is no PP tile. Click parliament to open Government.
3. Open a property card and choose a different setting. PP drops by exactly 100. Reopening shows the current choice; if PP is below 100, other choices are unavailable. Cancel costs nothing.
4. Inspect a foreign country: the compact political summary is present and its parliament does not open Government.
5. Resume and cross midnight: PP increases by 1. Hover the top-bar PP cell: base gain and daily total are green +1.00. No other growth modifier is active by default.
6. Save/load within 0.2.1: chosen settings and PP balance are retained. Start a new campaign to reset them. Older saves are unsupported.
