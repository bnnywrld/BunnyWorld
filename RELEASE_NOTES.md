# 0.2.1.3 — clean globe stabilization

- Remove obsolete invisible detail mesh and per-frame patch updates.
- Skip 31.5 MiB of unused boundary GPU fields and legacy local coast uploads; retain offline inputs for reproducibility.
- Update camera/culling and view/hover uniforms only when their inputs change.
- Skip five ocean-neighbor texture taps outside the coastal bands that need them.
- Share sandbox terrain/coverage textures between political and physical materials.
- Repair preparation: rebuild prepared boundary resources with the shipped generators and refresh the scenery checksum.
- Correct documented geography counts and resolution.

Canonical map PNGs, IDs, populations, ownership and demographics are unchanged. Existing simulation and idle redraw policy are preserved. No new gameplay systems or Windows executable. Native Windows/laptop FPS unmeasured.
