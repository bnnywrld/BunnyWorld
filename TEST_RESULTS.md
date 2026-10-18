# BunnyWorld 0.2.0.30 verification

46 Government UI integration checks pass in Godot 4.5.1 headless: all five menus and choices, clearing choices, closing/reopening, retaining player-country scope, unchanged country/state data, returning other panels to normal width, save/load compatibility, and clearing UI state for a new campaign and successful load. New scripts compile with Godot 4.5.1. Integration ran at 1100×700; Linux GL Compatibility rendering was visually inspected for silhouettes, the centered 100-seat layout and the option popup. All five controls fit inside the panel. Prepared resource checks and map contract verification pass.

The UI patch retains .29 geography/display resources. No map data, demographic data or simulation systems are changed. Native Windows visuals/performance are untested.

Manual: start a fresh campaign, open Government, change each property, close/reopen, inspect a foreign country and reopen Government, then return to the country panel. Check at 1100×700 and your normal resolution. No real leaders, party allocations, election dates or costs are expected.
