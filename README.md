> **Git working baseline: 0.2.0.5.** After a fresh checkout, run `python tools/restore_repository_assets.py` once, then open `project.godot` in Godot 4.5.1. All prepared assets are included; see [SOURCE_CONTROL.md](SOURCE_CONTROL.md). Windows ZIP testing needs no setup.

# Bunny World 0.2.0.5

Windows 10/11 x64 standalone. Extract into a fresh folder and run **BunnyWorld_0_2_0_5.exe**. No editor, installer or separate game pack is required. Start a fresh campaign.

The globe now fills the window, including wide/maximized layouts. Compact control boxes remain attached to the top edge: national stats and navigation on the left; clock/session controls on the right; map mode and search together below. Large top-bar numbers are abbreviated; hover for exact values.

Country panels show outlook followed by one national demographics pie with Age / Religion / Education / Activity selectors. Selecting a State opens a wider, half-height territory drawer beside the country panel: right of your own panel, left of foreign diplomacy. Its chart covers the selected State. Click the attached arrow to slide it behind the country panel; click the remaining handle to reopen it. Scroll for province details, cores and claims.

Economy and Construction replace Budget and National projects. Production, Diplomacy, Trade, Military, Intelligence and Space Exploration appear as disabled Planned buttons; this patch does not add their simulation systems.

Controls: right-drag rotate; wheel zoom; left click inspect; Space pause/resume; 1–4 speed; Ctrl+F/search icon find places; F focus; F5/F9 save/load; F11 fullscreen; Escape menu. Click your flag for country control.

Initial loading prepares resident terrain and scenery. Graphics quality selects Light 2048 or Balanced/High 4096 material libraries at launch. Travel reuses prepared resources. See RELEASE_NOTES.md and TEST_RESULTS.md. Source users: Godot 4.5.1 stable, GL Compatibility; prepared runtime assets are included. No old-save migration has been added.
