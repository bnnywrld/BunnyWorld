# BunnyWorld 0.2.0.11 visual patch

Apply this source patch over the working GitHub 0.2.0.10 project. It contains changed files only. There is no Windows executable.

## Install

1. Close Godot and the game. Extract the ZIP beside `project.godot`, replacing the included files.
2. Run `Prepare_BunnyWorld.bat`. Application **0.2.0.11** uses the verified **0.2.0.10 geography bundle**; this pairing is intentional.
3. Open `project.godot`, wait for imports, and start a fresh campaign. Keep a copy of the working 0.2.0.10 project for comparison.

## Rendering before and after

Borders were already generated **geometry ribbons**, drawn over the globe; they were not extracted from the ID raster on every frame. The categorical raster remains authoritative for ownership, fills and picking. This patch reuses every existing border mesh and map asset.

The ribbons now have a screen-pixel width, a dark outer casing, a lighter inner stroke and derivative-based `smoothstep` antialiasing. Country widths grow from roughly 1.5 pixels at distant views to 3.2 pixels nearby; states use about 2 pixels, and provinces about 1.2 pixels. States fade at distant views and provinces appear only at close zoom. National lines have a solid core, state lines are translucent and province lines faint. Water boundaries remain subdued.

The thick yellow selection becomes a thin ivory/gold edge with a restrained pulsing halo. Only the halo pulses. Country hover adds a faint fill tint. Physical mode retains a softer inward country-colour wash. Coast fills use the existing four categorical samples with a screen-footprint antialiasing band; picking stays discrete.

Country names follow curved paths projected onto the globe, with restrained tracking and dark outlines. Main connected land areas determine placement; Japan, Indonesia and Norway have authored visual paths. Names hide behind the globe, under panels, at close province zoom, or when they overlap or cannot fit. The **Aa** button beside map mode toggles them and is saved in interface settings.

Panels now use inset frames, restrained brass rules, consistent section captions and subtle shadows. The compact top bar stays in place. Country panels lead with six summary cards; exact numbers are available in tooltips. Population charts sit under the **Population profile** disclosure. The demographic toolbar shortcut opens it directly. State drawers lead with population, area and province information, with the demographic profile further down.

## Performance and limits

No map data, province shapes, ownership, sea regions, map generation or prepared assets change. No new distance-field texture or geography regeneration is required. Border zoom needs one changed scalar uniform; camera movement does not decode geography or rebuild border meshes. Country paths are prepared once and cached; camera movement projects those points and performs label fitting/collision checks only when the view changes.

Shader antialiasing smooths the displayed edge. It cannot recover missing coastline detail: some corners remain at extreme close zoom. Labels deliberately omit tiny or crowded countries at some views. Broader label-placement polish and higher-detail coastline sources are separate work.

Validated with Godot 4.5.1, Linux Compatibility rendering and Mesa software OpenGL. Native Windows/GPU performance needs a local playtest. The earlier report of 32 debugger entries remains unreproduced; this patch does not claim to resolve an unknown log.

## Before/after playtest checklist

1. Political mode, United States and Europe: compare national lines while zooming. Check country names, text collisions, globe rotation and the Aa toggle.
2. Japan: select country, state and province. Compare the old yellow outline with the thinner edge, subtle halo and hover tint.
3. Tokyo and Norway, Physical Earth: inspect coastline edges at several zoom levels. Check line stability and note remaining source corners at maximum zoom.
4. Zoom away from Tokyo: provinces disappear first; distant state lines recede while country lines remain readable.
5. Open your country and another country's panel. Check summary cards first, expand Population profile, switch all four chart tabs and collapse it again.
6. At 1100×700 and your normal resolution, scroll inside each panel. The content should scroll while the map stays still. Zoom and drag on the exposed globe should still work.

Raw automated results and selected screenshots are in `validation_0211`. `TEST_RESULTS.md` records the checks run for this patch.
