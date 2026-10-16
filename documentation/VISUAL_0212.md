# BunnyWorld 0.2.0.12 — map display and command bar

Changed-files source patch for the working 0.2.0.11 project. No Windows executable is included.

## Install

1. Close Godot and the running game. Keep the working 0.2.0.11 folder as your comparison copy.
2. Extract this ZIP beside project.godot, replacing the included files.
3. Run Prepare_BunnyWorld.bat. Expected versions: application 0.2.0.12, geography bundle 0.2.0.10, display bundle 0.2.0.12.
4. Open project.godot in Godot 4.5.1 Standard, wait for imports, and start a fresh campaign.

The prepared visual assets are included. Preparation uses ordinary Python 3 and does not require scientific/geographic Python packages. Those packages are only used by the optional offline display-asset builder.

## Country names and performance

Country names now occupy fixed curved geometry on the globe. Country shape, area and name length determine the layout once; zoom changes the apparent size naturally through perspective. There is no screen-font-size fitting loop during camera movement. Very small text fades out, and names fade away at province zoom.

All glyphs use one small atlas and one combined mesh. The GPU rotates/projects the glyphs with the globe. A small visibility mask is refreshed at most ten times per second when the view or panel coverage changes. It handles the back hemisphere, screen/panel clipping and crowded labels. Aa still toggles names and persists that preference.

Ownership changes, loading different ownership or changing country names refresh the prepared layout. Colour or map-mode changes alone do not rebuild it. Main connected land components determine placement; authored paths help Japan, Indonesia, Norway and the United Kingdom. Some crowded/tiny labels are intentionally hidden.

Unchanged camera poses, city-label views and HUD layouts are also cached. Physical Earth skips the four redundant province/region/palette lookup chains that previously reconstructed its land coverage; it now uses the prepared coast field. Existing city-building culling, batching and limits are retained. The Light graphics option remains available; this update does not lower the existing terrain texture quality.

The included CPU benchmark compares the 0.2.0.11 fitting loop with the new update and explicitly forced visibility work along the same camera path. The separate frame benchmark alternates names off/on along identical paths. Linux software-rendering timings are evidence about the implementation, not a Windows/NVIDIA FPS guarantee. Raw results are in validation_0212.

## Smooth displayed fills

The previous patch smoothed border strokes but left stepped coverage beneath them. This patch adds prepared signed-distance coverage for coasts and selected states/provinces. The display paths use the same native contours and smoothing family as the existing ribbons. Pixel-center rasterization prevents outward polygon-fill ledges. Selection and physical border washes follow the same coast coverage. Border vertices also interpolate elevation on the same detail grid as the globe surface, removing the height mismatch that exposed ledges at close zoom.

The coast field occupies 32 MiB of GPU memory. A compact 16 MiB bit map preserves real tiny land components using their original categorical coverage. Higher-resolution local coast windows are also prepared for coastal selections, blended into the global coast field. Selection/coast windows are streamed only when selection changes, with a bounded cache of twelve tiles. Camera movement does not decompress or upload them. The glyph atlas is approximately 5.3 MiB including mipmaps. This is a deliberate, bounded display-memory tradeoff rather than enlarging every map texture.

Small or very thin selected areas have a minimum rounded highlight footprint so their selection remains visible. Display smoothing can differ slightly from exact categorical picking near an edge. Extreme close zoom and tiny islands still have source/resolution limits; this patch does not add surveyed geographic detail.

Every original map asset, province/state record, ownership declaration, population record, sea region and generation input remains unchanged. Exact ID maps continue to drive picking and simulation. New display data has its own checksummed bundle; mixed or missing display files fail preparation early.

## Command bar and panels

The larger flag and the two content rows now share one compact frame at the top: important stats above, category buttons below. Clock/session controls remain in their own right-hand frame. The layout is reviewed at 1440×900 and 1100×700.

Country flags, names and close buttons stay pinned while the information below scrolls. The demographic shortcut shows its active state when the national profile is open. Tooltips use the briefing palette, and organization logos share a consistent outside frame while retaining light plates where artwork needs contrast.

The territory drawer has a country → state → province breadcrumb. Click the country or state level to return to that inspection level. The current province is identified at the end. The half-height sliding drawer and blocked map input over UI remain intact.

## Test order

1. Europe and North America, Political map: rotate and zoom with Aa on/off. Names should keep their world placement and scale naturally, without repeated text resizing.
2. Japan, Physical Earth: inspect Tokai, Province 9 (Izu peninsula), then Kanto/Tokyo. Compare the filled coast and selected-area edges with 0.2.0.11.
3. Sweden/Åland, Norway and islands: check ownership colours, coast coverage and label placement at multiple zoom levels.
4. Open your country and another country. Scroll to the bottom; the entity heading should stay visible. Expand/collapse Population profile and observe the demographic toolbar highlight.
5. Select a province, click its state breadcrumb, then its country breadcrumb. Collapse/reopen the drawer.
6. At 1100×700 and your normal resolution, check all top stats, the clock, map controls and panel scrolling. Wheel input on UI must not zoom the map; the exposed globe should remain interactive.

Report the map mode, country/location, resolution, graphics setting and whether Aa changes any remaining slowdown. Native Windows/GPU performance and the older unreproduced 32 debugger entries remain separate local checks.
