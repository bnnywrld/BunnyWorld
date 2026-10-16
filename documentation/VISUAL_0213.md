# BunnyWorld 0.2.0.13 — labels, country shading and territory drawer

Apply this changed-files patch over 0.2.0.12. Close Godot, extract the archive
into the folder containing project.godot, replace files, run
Prepare_BunnyWorld.bat, then reopen project.godot and start a fresh campaign.
No Windows executable is included.

## Country names

Names remain enabled. Fixed geographic sizing and the cached single-mesh
renderer are retained. Glyph coverage is now uploaded once from a bundled
RGB data texture, with explicit coverage sampling and transparent-pixel
discard. This bypasses PNG importer alpha and stale imported textures.
No system font installation is needed. Collision checks use the actual baked
text footprint instead of the longer geographic fitting path.

The reported Windows-only white strips could not be reproduced on this Linux
renderer. The new path removes the imported-alpha dependency; actual Windows
confirmation remains part of the user's test.

## Country colour along boundaries

The original border fade had a categorical water cutoff separate from the
smoothed coastline. A prepared continuous shade field now extends through
that cutoff, and tint is reconstructed from neighbouring palette samples.
Country selection and hover also extend their visual owner through smoothed
coastal coverage, preventing square holes in the highlighted country.

The display changes do not alter province IDs, ownership, borders, picking,
adjacency, population, or map generation. Current country palette changes
remain effective. The prepared width field retains the starting geography's
border emphasis; rebuilding that emphasis after future political border
changes is outside this visual correction.

## Territory drawer

- Responsive width: approximately 439 px at 1440 and 350 px at 1100.
- Existing lower-half placement, side selection and collapse handle retained.
- Pinned breadcrumb, country flag and State heading.
- Compact population/area cards and a separate selected-province card.
- State Buildings, State Resources and Infrastructure have dedicated frames.
- Buildings show existing starting State inventories; construction and
  operating effects are not activated by this interface.
- Resource data are not populated, so the section says “Data unavailable.”
- Visible starting-estimate and population-bookkeeping lines are removed.
  Exact counts and relevant provenance remain in tooltips.
- Demographics remain expandable; cores/claims use compact flag rows.
- Command-bar statistics have subtle group separators and tighter spacing.

Political portraits/parliament remain assigned to 0.2.1. Existing organisation
membership maps are retained. Placeholder icon artwork is unchanged.

## Test order

1. Leave names enabled. Inspect China, Japan, the USA and Europe while zooming
   and rotating. Letters should appear, with no solid white strips or stutter.
2. In Physical Earth, inspect Japan → Tokai → Province 9. Check the coloured
   coastal shading, selected fill, small islands and nearby land borders.
3. Switch to Political; check ownership colours, selection and boundaries.
4. Inspect your own State and a foreign State. Scroll the wider drawer:
   its heading should stay pinned; buildings/resources/infrastructure should
   remain separate, and the collapse arrow should stay accessible.
5. Hover the population figures for exact values. Scroll over UI panels:
   the map should remain stationary.

Validation details and platform limits are recorded in TEST_RESULTS.md.
