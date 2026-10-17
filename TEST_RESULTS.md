# BunnyWorld 0.2.0.24 verification

74 full-application checks pass with zero failures in Godot 4.5.1 GL Compatibility
on Linux llvmpipe. The checks cover the supplied loading/menu image, aspect
preservation and menu visibility, 370px country/diplomacy inspectors, all eleven
feature toolbar sections, close/toggle/replacement behavior, country flag and
camera-centering action, temporary state hover and restoration, Micronesia's
single-state browser, removed countries/provinces and live GPU island membership.
Menu, loading, Research and state-list views were captured; the menu and panel
layouts were inspected. Native Windows appearance/input feel remains the user's test.

The independent geography check passes 45,043 assertions: exact before/after
province raster comparison, unchanged other province footprints, all memberships,
unique local numbering, national/world populations, capitals, city/scenery island
references, adjacency symmetry and removal from the tiny-land physical fallback.
Exactly five raster pixels are removed, corresponding to Malpelo and Navassa.
Totals: 224 countries, 1,239 states, 13,308 land provinces; 6,144,737,528 residents.

The shared map pipeline rebuilt and verified borders, spatial batches, smooth
boundary/coast fields and tiny-land bits together. Prepared resource restoration,
geography/display bundle hashes and the map/source/cache contracts pass.
GDScript parsing, Python compilation and git diff whitespace checks pass.

There is no renderer redesign, simulation change or new native FPS claim in this
patch. Windows export was not performed. Use a fresh campaign in the .24 source
project. See documentation/PATCH_0224.md for the two short local test groups.
