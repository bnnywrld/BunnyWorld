# BunnyWorld 0.2.0.1 — Terrain, scenery and waterways

Extract the complete Windows ZIP and run BunnyWorld_0_2_0_1.exe. Start a fresh campaign.

Windows packaging correction: the first 0.2.0.1 ZIP mistakenly used a launcher with the original 0.1 game embedded. After the external-pack correction did not resolve the user's report, this package uses a uniquely named executable containing the current game. The exact executable's embedded game data passes version/resource and scene checks. Window title, loading screen and main menu identify 0.2.0.1. Replace the full extracted folder with this package.

- Replaces geographic JPEG tile streaming with resident terrain: year-2000 ESA CCI land-cover families, regional colour, NOAA elevation and eight fixed aerial materials. Terrain textures no longer change memory slots when the camera travels.
- Material mipmaps and GPU compression are prepared offline. The material library occupies about 22.4 MB. World-anchored triplanar mapping avoids longitude/pole stretching, and class-weight blending softens biome transitions.
- One reusable close-view grid is displaced by the GPU. Moving the camera changes its coordinates without rebuilding the mesh.
- Startup loading progress covers world data, terrain, city meshes and graphics preparation. All city/landmark meshes are retained for reuse during the session.
- Buildings and landmarks are exactly 3× their previous display scale. Skylines contain four to five times as many representative buildings, up to 200 per metropolitan group, with at most 1,024 buildings and 64 clusters nearby.
- Landmark labels are removed. City names retain label priority. Scenery still fades in only at close zoom, and the existing scenery toggle remains available.
- Age, religion, education and economic activity charts appear together in one 2×2 demographics view. Sources and development explanations move to documentation; useful population denominators remain visible.
- Selected major rivers appear as terrain-following ribbons. Suez and Panama have visible canal courses and explicit reciprocal sea-passage links. Bosporus and Dardanelles connect restored Black Sea/Marmara zones to the world ocean. Inland lakes remain excluded from sea zones.
- Preserves 0.2.0 demographics, finances, icons, ledger, country controls, terrain tilt, province IDs, populations, ownership and territorial rights.

Year-2000 land-cover data is sampled for the globe; material detail is representative rather than a unique photograph of every place. Waterway centre lines are approximate. There is no naval movement/control simulation yet: passage links establish map connectivity for subsequent systems.

No old-save compatibility or migration is added. Population growth remains for later demographic work. Native Windows execution and performance on the user's PC require user testing; see TEST_RESULTS.md for the checks run here.
