# Bunny World 0.2.0.15

State corrections and worldwide audit. Overlay on 0.2.0.14, run Prepare_BunnyWorld.bat, then start a fresh campaign. See [patch notes and audit scope](documentation/PATCH_0215.md).

# Bunny World 0.2.0.14

Rebuilt patch over 0.2.0.13. See [patch notes](documentation/PATCH_0214.md) for installation, changes and test checklist. A fresh campaign is required.

# BunnyWorld 0.2.0.13

Latest source patch: label transparency, country-edge colouring and the wider territory drawer.
Apply over 0.2.0.12; see [patch guide](documentation/VISUAL_0213.md).


Godot 4.5.1 **Standard**, GL Compatibility; Windows 10/11 x64. The current development baseline is `main`.

This visual ZIP applies over working 0.2.0.12. See [visual changes, installation and test order](documentation/VISUAL_0213.md). Country names stay enabled; demographic charts are under Population profile.

## Update and run

1. Close Godot and the running game.
2. Extract the changed-files ZIP over your working 0.2.0.12 project, beside `project.godot`, replacing the included files.
3. In the project folder, double-click **Prepare_BunnyWorld.bat**. Wait for successful preparation: application **0.2.0.13**, geography bundle **0.2.0.10** and display bundle **0.2.0.13** are the expected pairing.
4. Open `project.godot` in Godot, let imports finish, and press F5. Start a **fresh campaign**.

The preparation helper uses installed Python 3, restores prepared resources, refreshes known older border files automatically, and verifies the matching map/data/border bundle. It stops on unknown custom resource edits or mixed versions. Alternative: `python tools/restore_repository_assets.py`. Export templates are not needed to run the project in the editor.

## Current geography

223 retained starting country owners, **1,360 States**, **13,594 land provinces**. The original MD archive has 1,250 States and 13,221 real land provinces (dummy ID zero, sea zones and lakes excluded). Natural Earth supplies the geographic boundaries; MD supplies country budgets, regional naming hints and province density guidance. [Country comparison](GEOGRAPHY_COUNTRY_COUNTS.md).

All 99 Natural Earth disputed/breakaway source identities map to protected State coverage. Nested claims and neighboring disputed islands can share a protected State as documented in the comparison. Future-dispute boundaries retain January-2000 scenario owners and existing starting cores/claims; reserving the geometry does not activate a later dispute.

National population/building totals are retained. New local demographic refinement and old-save migration remain deferred. Map data and prepared geography assets are unchanged by 0.2.0.13; border shaders, country names and information panels are updated. No Windows executable is built for this source update.

## Test order

1. Political map: Egypt, Algeria and Nigeria. Check State counts/shapes and aligned black borders.
2. Close zoom: South Korea/Japan, then Europe, India, eastern China and the US. Compare useful province density.
3. Zoom out over the Sahara, Siberia and Greenland; sparse areas should have larger cells.
4. Inspect Crimea and the Donetsk/Luhansk reserved territories (Ukraine at startup), then Golan Heights, Aksai Chin, Transnistria and Northern Cyprus.
5. Select States/provinces, search for places, rotate/zoom, and collapse/reopen the territory drawer. Report a country/place, screenshot, zoom/map mode and any slowdown or error.

Controls: right-drag rotate; wheel zoom; left click inspect; Space pause; 1–4 speed; Ctrl+F search; F focus; F5/F9 same-version save/load; F11 fullscreen; Escape menu. F5 in the **editor** starts the project.

Technical checks and limits are in TEST_RESULTS.md. Native Windows visual/performance testing belongs to the user.

The full geography correction list and test order are in [documentation/GEOGRAPHY_0209.md](documentation/GEOGRAPHY_0209.md). The Russian historical cuts remain approximations at game scale.
