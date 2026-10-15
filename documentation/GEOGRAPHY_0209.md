# BunnyWorld 0.2.0.9 — second geography correction pass

Apply this changed-files patch to the delivered 0.2.0.8 source project. Close
Godot, extract into the folder containing project.godot, replace included files,
run Prepare_BunnyWorld.bat, and start a new campaign in Godot.

## Requested corrections

1. Hebei's original local province 27 is transferred to Beijing.
2. Kashmir's overlapping source intersections are consolidated into Ladakh,
   Jammu and Kashmir, Gilgit-Baltistan, Azad Kashmir, Aksai Chin, Shaksgam and
   Siachen as applicable. Local controller footprints are reconciled with the
   bundled Natural Earth map units; the China-labelled Ladakh exclave and the
   larger misregistered Chinese patch inside Indian Ladakh are removed. Claims
   are retained independently from the corrected scenario controller.
3. The oversized provinces in the Ghazni/Baghlan state are subdivided with
   terrain-guided growth and settlement seeds.
4. Syria uses eight broader geographic regions: Northern Syria, Syrian Coast,
   Central Syria, Damascus, Southern Syria, Raqqa, Deir ez-Zor and Jazira. The
   UNDOF zone stays separate. Large provinces receive additional subdivisions.
5. Sinai's original local province 19 moves to Red Sea Coast.
6. Croatia has three meaningful mainland regions: Northern Croatia, Slavonia
   and Adriatic Croatia. The existing disputed river/island footprints remain
   separately represented.
7. Uruguay has two states: Northern and Southern Uruguay. The small offshore/
   border records are integrated into the relevant region.
8. Transnistria is one state.
9. Donetsk/Luhansk receive substantially more provinces, with additional local
   density improvements in Kharkiv, Zaporizhzhia and Dnipropetrovsk.
10. Devon is merged into Cornwall, retaining the Cornwall name.
11. Castile and León's original local province 14 moves to Basque Country as
    explicitly requested, removing the reported gameplay enclave.
12. Southern Solomon Sea/Eastern Micronesia identity fragments in West Polynesia
    are removed. Tasman Sea receives a coherent cross-date-line extension that
    replaces the Far South Pacific arm and includes the Niue neighbourhood.
    The old state named Niue on the Chatham/Antipodes footprint is renamed
    Chatham and Antipodes Islands. Sea land/lake masks remain identical.
13. Solomon Islands is one state.
14. The old Kalimantan mega-state is replaced by correctly identified West,
    East, South and Central Kalimantan. Central Kalimantan is divided into
    western, central and eastern states using terrain-guided partitions.
15. Lower Amur's original local provinces 14, 37, 3 and 38 move to Okhotsk Kraj.
16. Sakhalin's Kuril island pieces are separated from the main island. Southern
    island pieces join South Kuril Islands; remaining central/northern pieces
    form North Kuril Islands. The previous Kuril Is. state is renamed South
    Kuril Islands. Moneron and the main Sakhalin footprint stay with Sakhalin.
17. The northern Stanovoy portion of Amur becomes a separate state. This is a
    terrain-guided gameplay approximation to improve historical regional
    representation; it is not an archival Manchurian treaty-border trace.
18. Philippine fragments are consolidated into Northern/Central/Southern Luzon,
    Mimaropa, Western/Eastern Visayas, Western/Northern/Southern Mindanao and
    the Spratly Islands footprint.
19. Austria has five states: Western Austria, Salzburg and Upper Austria,
    Lower Austria and Vienna, Styria and Burgenland, and Carinthia.
20. Åland's original local provinces 2 and 5 move to Sweden's Stockholms Län.
21. Venezuela has six states: Western/Central/Eastern Venezuela, Bolívar,
    Amazonas and Caribbean Islands.
22. Riau Islands is a separate state. North Sumatra is split into Northern
    Sumatra and Toba and Southern North Sumatra. The remaining old Riau/North
    Sumatra grouping is renamed Central Sumatra.
23. Georgia has Western and Eastern Georgia, retaining the separate Abkhazia
    and South Ossetia scenario controllers established in the prior version.

## Focused test order

1. Inspect Kashmir/Ladakh closely: names, controller borders and selection.
2. Inspect the new Syrian regions, Ghazni and eastern Ukrainian province sizes.
3. Check all original numbered transfers against the 0.2.0.8 map. The report
   records original local numbers and stable global province IDs. Local display
   numbers can change after splitting/merging; use geography as well as numbers.
4. Inspect Kalimantan, Riau Islands, North Sumatra, the Philippines and Solomons.
5. Inspect Amur/Stanovoy, Lower Amur/Okhotsk and Sakhalin/Kuril membership.
6. Inspect Austria, Croatia, Georgia, Uruguay, Venezuela, Cornwall and
   Transnistria. Check mainland state counts separately from protected areas.
7. Check sea selection around West Polynesia, the date line, Chatham Islands
   and Niue. Zoom out to ensure the replacement boundaries form coherent areas.

For every reported border, hover and click on both sides, then zoom in to check
that province selection matches the state and country shown.

## Preparation and source limits

Natural Earth ADM1/map-unit/disputed-area geometry and the existing relief
grid are the source inputs. Existing province interiors outside the affected
areas are retained. All new generation, connectivity repair, adjacency building
and account relinking happens offline; no runtime geography loops are added.

World population and building totals are conserved. Country-level accounting
changes only with the corrected Kashmir footprints and the requested
Finland-to-Sweden transfer. No demographic refinement or save migration is
performed.

The two previous approximate Russian historical cuts remain subject to visual
review. The new Amur/Stanovoy partition is also approximate at game scale.

The offline generation script caches the pre-patch 0.2.0.8 source inputs in
.geography_0209_baseline on its first run. Regeneration requires that baseline;
ordinary patch installation does not require running the generator.

Reference context for controller/territory interpretation:

- https://www.un.org/geospatial/content/jammu-and-kashmir
- https://www.un.org/geospatial/content/syrian-arab-republic
- Bundled Natural Earth geographic_subdivisions.geojson,
  natural_earth_map_units.geojson and disputed_areas.geojson.
