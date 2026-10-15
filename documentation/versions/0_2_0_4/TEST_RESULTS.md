# BunnyWorld 0.2.0.4 verification

All final automated checks pass. The native Windows executable has not been launched on Windows in this environment. Its exact embedded game was loaded and rendered by the matching Linux Godot 4.5.1 runtime under Xvfb/Mesa; this does not establish Windows hardware performance.

- Source UI regression suite: passes. Verifies removed header name/footer, stat ordering and individual boxes, centered stat icons/values, 46×46 navigation aligned with the flag, compact search/clock controls, later capital labels, territory/diplomacy separation, adjacency, close/reopen lifecycle, country-change clearing, working search and return to selection.
- Rendered layout: reviewed at normal 1440×900 canvas and minimum 1100×700 canvas. Globe viewport is 743 pixels high at normal size. Territory drawer is 260 pixels wide; diplomacy is 330 pixels wide and moves beside the drawer without overlap. Scrollbars expose lower information.
- Source full UI smoke: passes. Exercises menu/selection/campaign, country/organization interaction, opinions, flags, clock, search/camera/picking, same-version named save/load, invalid saves, cursor clipping and panel suppression, settings, urban scenery bounds and province population inspection.
- Foundation UI: passes; four demographic charts, State scope, pause/resume, World Ledger sorting/search and tension dialog remain working.
- Model, relations, territorial rights, urban population, place catalog, foundation and resource-load suites: pass.
- Exact exported executable: correct 0.2.0.4 application identity and retained 0.2.0.3 world scenario; embedded UI regression + full interaction smoke exits 0 and supplies all five layout captures. Its PE embedded section/footer agree. All 260 packed file MD5 digests pass and 54 raw source/runtime matches pass.
- Baseline preservation: all 134 original non-import data/asset files match 0.2.0.3; terrain shaders, resident terrain, urban scenery, relief and world-state scripts are byte-identical. No camera texture uploads, geography rebuilds or simulation changes were introduced by this patch.

The Mesa driver warns that V-Sync changes are unsupported; Xvfb can emit keyboard-symbol warnings. Final source and embedded scene checks contain no script/shader/resource errors. Screenshots are internal visual QA and are not needed to run the game.

BUILD_INFO.json records the final EXE digest and size. Companion checksums identify both ZIPs. Archive CRCs are checked during packaging. Start fresh when testing a new release; no save migration has been added.
