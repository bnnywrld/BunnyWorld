# BunnyWorld 0.2.0.12

Source patch for working 0.2.0.11.

- Fixed curved country-name geometry, one shared glyph atlas/mesh, cached visibility, and refresh only when country layout changes.
- Prepared coast and selection coverage; smoother filled edges beneath the existing border strokes.
- Larger flag and a unified command frame: stats above category buttons, clock on the right.
- Pinned entity headings, active demographic shortcut, consistent logo frames, briefing tooltips and selection breadcrumbs.
- Cached unchanged camera, city-label and HUD-layout updates.
- Separate display-bundle verification and export inclusion for the new prepared assets.

Original geography and simulation data are unchanged. New display assets are included; no regeneration is needed. No Windows executable is included.

Installation, limits and test order: documentation/VISUAL_0212.md. Validation and measured performance: TEST_RESULTS.md and validation_0212.
