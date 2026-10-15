# BunnyWorld 0.2.0.5 verification

All final automated checks pass. The Windows executable itself has not been launched on native Windows. Its exact embedded game was loaded and rendered with the matching Linux Godot 4.5.1 runtime under Xvfb/Mesa. This verifies pack/UI behavior, not native Windows hardware performance.

- Source UI suite: 56 checks, zero failures; source full interaction smoke passes. Final exported UI suite: 58 checks, zero failures; the combined exact-pack UI + full smoke run exits 0.
- Full-window globe and independent top-edge boxes: pass. Stats/clock share the top line; the map selector stays next to search; top groups fit the minimum 1100×700 canvas. Shortened population/GDP-per-capita values retain exact hover figures.
- Navigation: Economy and Construction captions verified, six new sections present and disabled with Planned tooltips; existing national demographics shortcut remains active and opens the inline profile.
- Demographics: national chart uses national population; territory uses only the selected State. All four selectors work on one chart. Outlook precedes the national chart. Existing data/allocation denominators stay unchanged. Detailed diagnostic dialog/Foundation UI tests also pass.
- Territory: 300-pixel width, lower-half placement, foreign drawer left of diplomacy and own drawer right of country control. Both collapse directions, arrow reversal, persistent handle, reopening and stale-handle removal pass. Scrollbars expose lower province details.
- Resize/side bars: verified through managed Window resize at 1920×1080 and 2560×1080, not merely by changing the canvas size. Root and globe viewport fill the expanded aspect; controls stay at the right edge. Normal 1440×900 and minimum 1100×700 layouts are visually reviewed. The project uses expand aspect handling.
- Full interaction smoke covers menu/campaign transitions, flags, opinions, organizations, clock, place search, camera/picking, same-version named save/load, invalid saves, settings, scenery caps and province population information.
- Model, relations, territorial rights, urban population, place catalog, foundation, resource-load and foundation-UI suites pass.
- Export: application identity 0.2.0.5; unchanged geographical scenario bunny_world_2000_0_2_0_3. PE pack/footer agree. All 265 packed MD5 digests and 54 raw source/runtime comparisons pass.
- Baseline preservation: 135 original data/asset files match 0.2.0.4. World-state, demographic model, pie renderer, terrain shaders, resident terrain, relief and scenery scripts are byte-identical. New assets are four small navigation SVGs. No geography or camera-driven resource rebuilding was added.

Final source/embedded runs contain no script, shader or resource errors. Mesa warns that V-Sync changes are unsupported; Xvfb can emit keyboard-symbol warnings. Internal captures support visual QA. Text reports are included under validation_0205; BUILD_INFO.json records exact executable identity. ZIP CRCs and executable/archive hashes are verified during packaging.

Start fresh across releases. No old-save migration or new economy/military/etc. simulation is included.
