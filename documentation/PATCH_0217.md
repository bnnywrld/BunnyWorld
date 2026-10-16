# BunnyWorld 0.2.0.17

Apply over 0.2.0.16. Close Godot and the game, extract the patch into the project root and replace files, then run Prepare_BunnyWorld.bat. Start a fresh campaign.

- Rebuilt State and province selection from the final province-ID atlas using analytic contour distances and half-float coverage, with one coverage field driving fill and outline. Current coastal windows cover all 890 eligible States; obsolete windows keyed to removed States/provinces are absent.
- Rebuilt physical country border shading from current ownership, removing obsolete bands. Sea-region selection no longer outlines inland lakes; lake ink is thin and muted.
- State-list buttons open the overview and smoothly rotate/zoom the camera to the State. Tiny retained territories have discrete markers with larger click targets, keeping their actual shapes. Paracel footprints are enlarged by one native map cell for usability.
- Completed the attached 97-row small-State list: 47 State unions, 278 province unions, and coordinate/2000-control corrections. Explicit Isle of Man and Yucatan province destinations are retained. See SMALL_STATES_0217.md and data/geography_0217_report.json.
- Border resources and the larger display pack now ship as versioned repository parts. This fixes the previous direct-resource files being skipped during GitHub upload. Runtime checks reject border resources from another geography version. Each repository part is below GitHub file limits; do not manually upload the generated selection_distance_0217.bwd.

Final counts: 227 country entities, 1,305 States and 13,312 provinces. Global population and decorative scenery counts are conserved. New small-country economic/demographic profiles remain inherited placeholders until the planned data update.

Test order: (1) North Sumatra southern provinces and coast, (2) former Korean DMZ, (3) Cyprus, (4) Riau and Straits of Malacca with sea selection, (5) country breadcrumb → State list → State button, (6) Gibraltar/Paracels markers, (7) Isle of Man and Yucatan Province 5.

General province-density redesign is deferred; its future global increase remains capped at 20%. Country names stay enabled.
