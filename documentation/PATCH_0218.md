# BunnyWorld 0.2.0.18 — shared map rendering

Apply this changed-files patch over **0.2.0.17**. Close Godot, extract into the folder containing project.godot, run **Prepare_BunnyWorld.bat**, reopen Godot and start a fresh campaign. No new Windows executable is included.

## Rendering changes

- Province geography is fixed; province-to-State membership and State ownership are separate lookup tables. Ownership transfers emit an event that refreshes the live palette and national edge classification.
- Close-view State/province fills, country colours and border lines use one ownership-independent representation: a pair of province IDs and signed distance to their shared smoothed boundary curve. Line coverage uses screen-space derivatives and antialiasing. State and country boundaries are resolved from current membership/ownership, rather than baked into individual State masks.
- Coastal selection is clipped by the same coast field as the terrain and shore ink. It does not apply a second independent province coastal outline.
- Multi-province junctions and ambiguous tiny features conservatively use current categorical membership. Geographic shapes remain bounded by the existing map resolution; this patch does not redesign province shapes or invent coastline detail.
- Starting-ownership border shading and the 204 MB individual land selection pack are no longer loaded. National edge shading responds to current ownership.
- Picking, labels and rendering share verified lossless province pixels. The province-to-State texture is made from current JSON at startup, avoiding an independently imported stale lookup image.
- Camera movement does not rebuild map geometry or load selection masks. Country names stay enabled.

## Geography authoring

`data/provinces.json` and the four lossless province-ID PNGs are authoritative for membership and footprints. `world.json` holds State and ownership data. Province-ID pixels must agree with the province registry, and State membership lists must agree with province membership.

Use **one build command** after geographic edits:

```
python tools/build_map.py --godot "path/to/Godot_v4.5.1-stable_win64.exe"
```

Or pass that executable to **Build_BunnyWorld_Map.bat**. The authoring build requires NumPy, SciPy, Pillow, scikit-image, Shapely and rasterio (the existing geography toolchain). Players applying this prepared patch only need the normal preparation script and Python; its check mode uses the standard library.

The builder detects changed footprints/membership, derives adjacency and grouped geometry, rebuilds border resources, coast coverage and universal boundary fields, then writes a shared build contract and restoration metadata. It does not require region-specific mask repair scripts. `--force` also rebuilds after changing the geometry-generation algorithm. `--check` verifies a prepared map without rebuilding it.

A change of owner requires **no geographic rebuild**. Province-level military occupation remains a separate gameplay system; this patch does not implement warfare or independent province controllers.

## Verification and limits

Graphical tests use Godot 4.5.1's OpenGL Compatibility renderer on Linux software rendering. They exercise North Sumatra, Cyprus, the former DMZ area, State transfer and restoration in political mode, physical edge shading after transfer, a runtime membership merge, country-name/camera stability and sea selection. Spatial checks include Riau and verify the map data is unchanged from .17.

The new universal fields occupy 192 MiB on the GPU, plus a 32 MiB conservative boundary hint. No old individual land highlight textures are uploaded. Native Windows/NVIDIA 940MX performance and the reported difference between the previous Linux and Windows images are **not verified** here; the test sequence below is required on the user's machine.

## Test order

1. Select North Sumatra at country and province zoom. Inspect the complete State highlight and its southern province borders. Pan and zoom with names enabled.
2. Select Cyprus and then the Korean former DMZ area. Follow the coloured edge closely: fill, country shading and line should align without the old stepped bands. Switch between political and physical modes.
3. Select Riau Islands, then nearby water; verify shore selection does not introduce inland blocks.
4. Use the State list to visit another country and return. Confirm normal navigation, selection and map responsiveness.

If a discrepancy remains, preserve a screenshot and the Godot error/output text. A passed Linux test is not a claim that the user's Windows issue has been reproduced or resolved.
