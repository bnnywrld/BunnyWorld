# BunnyWorld 0.2.0.4 — interface refinement

Based on the complete verified 0.2.0.3 source. World, provinces, population accounting, terrain, waterways and scenery resources retain that baseline.

- Removed the country name from the campaign header; the flag tooltip identifies your country and clicking it opens country control.
- Enlarged national navigation buttons to 46×46 and aligned them with the flag.
- Moved eight national stats above the flag/navigation row, in individual compact boxes with centered icons and values. Detailed stat explanations remain on hover.
- Reduced header margins, row spacing and button padding to give the globe more room.
- Removed the bottom status bar, playing-as text and redundant physical/political-map footer. Other map legends sit over the viewport.
- Country hover tooltips shrink to fit short names and wrap longer province descriptions to a bounded width. Existing cached flags remain.
- Moved selected State/province population, area, cities, estimate notes, connections, infrastructure, cores and claims into a 260-pixel scrollable territory drawer. It slides out to the right of diplomacy or alongside own-country control. Each panel has a close button; closing/changing the parent clears stale territory details.
- Replaced Find place text with a vector magnifying-glass icon. Ctrl+F and search behavior remain available.
- Compact play/pause icons, speed selector and menu controls; text buttons retain their full labels.
- Capital labels begin at camera distance 1.65 instead of 2.5. Ordinary cities retain their closer 1.35 threshold and capital priority.
- Campaign stats/navigation hide correctly when returning to country selection. Same-version save/load remains available.

Known limits: national government/research/construction simulation is still planned. The retained 0.2.0.3 scenario ID describes unchanged geographical data; application and executable version are 0.2.0.4. This patch adds no old-save compatibility or migration. Native Windows testing remains for the user; automated checks use Linux/Godot and Mesa.
