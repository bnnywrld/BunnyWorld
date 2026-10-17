# Export BunnyWorld as a Windows release EXE

Use the corrected project and matching **Godot 4.5.1 Standard** export templates.
This project uses GDScript; a .NET/C# editor is unnecessary.

1. Close the game, apply the full patch, and run **Prepare_BunnyWorld.bat**.
2. Open `project.godot`. In Godot choose **Editor → Manage Export Templates**.
3. Download/install the templates matching your editor version (4.5.1 for this project).
   This is a one-time setup for that Godot version.
4. Choose **Project → Export** and select the existing **Windows Desktop** preset.
   If it is absent, use **Add → Windows Desktop**. Keep x86_64 and GL Compatibility.
5. Click **Export Project**. Choose an empty folder outside the source project,
   for example `Desktop/BunnyWorld_Test/BunnyWorld.exe`.
6. **Untick Export With Debug**, then save/export. Use Export Project to make the EXE;
   Export PCK/ZIP produces game data without a playable executable.
7. Close Godot completely and double-click the exported EXE. Confirm **0.2.0.28**
   on the main menu. Start a fresh campaign.

The included preset embeds the game pack. If you deliberately change to an external
pack, keep the resulting `.pck` beside the EXE.

## Compare performance fairly

Use the same resolution, graphics preset, frame limit, map mode, zoom and region.
Compare dragging/zooming after startup has completed. Record the map mode, GPU load
and how the movement feels. If using frame-time diagnostics, retain their report.

Running through the editor includes debugging/editor overhead. A release export
removes those components and is the appropriate baseline for performance testing.
Its exact improvement on the 940MX remains unmeasured here; the terrain shader's
underlying GPU cost still needs renderer work. Low overall CPU use and high GPU
use make GPU rendering the leading current hypothesis, without proving that every
individual stutter has the same cause.

Accepted project priority: **smooth in-game interaction ahead of startup speed**.
More offline/boot preparation and CPU-side caching are acceptable. Keep GPU-resident
data bounded rather than loading unlimited detail into the 2 GB graphics memory.

## Optional command-line export

For an installed editor/template setup, the existing helper exports a release build
and validates its embedded version and scenario:

```bat
py -3 tools\build_windows.py --godot "C:\Path\Godot_v4.5.1-stable_win64.exe" --output "C:\Path\BunnyWorld_Test\BunnyWorld.exe" --embed-pck
```

Run this from the project folder. The validator now uses the source version/scenario
instead of the obsolete hard-coded 0.2.0.6 values. No Windows EXE is supplied in the source patch.

Official references:

- https://docs.godotengine.org/en/4.5/tutorials/export/exporting_for_windows.html
- https://docs.godotengine.org/en/4.5/tutorials/export/exporting_projects.html
