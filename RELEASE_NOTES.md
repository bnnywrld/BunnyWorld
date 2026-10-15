# BunnyWorld 0.2.0.5 — compact top controls and demographic drawers

Complete 0.2.0.4 baseline plus the agreed UI improvements:

1. Foreign territory drawers open on the left of diplomacy; own-country territory remains on the right of country control.
2. Territory is 300 pixels wide and occupies the lower half of the viewport. Independent scrolling keeps all province information accessible.
3. An attached arrow replaces the territory close button. The drawer slides behind its parent panel and leaves a visible, reversed arrow handle; clicking reopens the same territory. Parent close/organization changes remove stale handles.
4. Clock and session controls align with the stats at the top edge in their own compact box.
5. Map mode and magnifying-glass search share a compact box below the right-hand controls. Contextual organization/relation selectors remain beside them.
6. Top boxes wrap their actual controls. The globe renders behind them and uses the entire remaining window; there is no full-width opaque header.
7. Expand aspect handling fills wide/maximized windows instead of keeping fixed-aspect side bars. Resize-aware control anchors follow the window edges.
8. One State demographics pie in the territory drawer, with Age / Religion / Education / Activity selectors. National information uses one national-only pie with the same selectors.
9. Outlook is above the national demographics selectors. The working header demographics shortcut opens the inline national profile.
10. Budget is renamed Economy; National projects becomes Construction.
11. Added disabled Production, Diplomacy, Trade, Military, Intelligence and Space Exploration buttons with Planned tooltips. New icons are small native SVG assets.
12. Shortened large header values such as 38.6M and $16.2K, retaining exact figures on hover. Compact chart legends truncate long category names with full-value tooltips.

Geography, shaders, relief, populations, scenery and simulation stay on the accepted baseline. Application/EXE version is 0.2.0.5; unchanged world scenario is bunny_world_2000_0_2_0_3, save schema 10. No old-save migration or new simulation systems.

Demographic denominators are preserved: age/religion use all residents; education uses adults 25+; economic activity uses working-age residents. Unknown data stays unknown. State charts are estimates derived from the existing demographic profiles, not new State census data. Charts retain all categories; the five largest appear in the compact legend, with other segments inspectable by hover.
