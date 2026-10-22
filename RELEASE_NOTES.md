# 0.2.1.7 — Organizations

- Organizations toolbar section with large membership cards and member/feature detail tabs.
- Eight organization types; saved membership statuses, exclusive full alliance membership, integration opt-out queries and headquarters links.
- Existing 19 membership lists preserved. Directory contains 25 additional inactive definitions awaiting the member-list review requested in the design.
- Organizations map mode shows the selected HQ as a gold star and hides country capitals/city markers. No fixed HQ means no star.
- Unbuilt or unbalanced effects/actions are marked Planned and remain inactive. OAU/AU and CST/CSTO display names follow the campaign date; no automatic membership changes.
- Application 0.2.1.7; fresh campaign/schema 22; map/display stay 0.2.1.2. No EXE export.

# 0.2.1.4 — map style and obsolete capital cleanup

- Physical map: retain a light country tint at close zoom; narrow and soften border/coast colour ribbons.
- Quieter state/province borders, thinner unselected coastline ink, less water glare and foam.
- Blend terrain detail more gently with regional colours and lift excessively dark relief shading.
- Remove 42 tiny markers added by the old capital pass that no longer serve as capitals, and 42 associated clusters (190 decorative buildings). Keep original mapped cities, national/current state capitals and added cities ranked 10,000 or above.
- Clear obsolete capital icons on retained cities and refresh scenery priorities/weights against current state capitals.
- Add an idempotent cleanup tool with preservation tests. Refresh JSON bundle checksums.

Application 0.2.1.4; geography/display remain 0.2.1.2. Canonical geography, state/province IDs, ownership, population and demographics are preserved. No new textures, meshes or gameplay systems. Pull clean-globe, run Prepare_BunnyWorld.bat and test a fresh campaign. Windows/laptop FPS remains unmeasured.

## Previous stabilization (0.2.1.3)

Removed the obsolete invisible detail mesh, 31.5 MiB of unused boundary texture payload, legacy coast uploads and stationary camera/uniform work. Rebuilt prepared boundaries to repair stale build provenance. The 10 Hz idle redraw policy and independent simulation are retained.
