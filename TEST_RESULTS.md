# 0.2.0.16 validation

43 graphical Godot 4.5.1 runtime checks passed with zero failures and no script/shader errors. The tests ran from an independent installed update over the previous data/scripts and border resources, with a clean Godot import. Prepared asset and bundle verification passed. Rendering used Linux OpenGL compatibility / Mesa software rendering; native Windows GPU performance was not benchmarked.

Data checks passed: 223 countries, 1,352 States, 13,590 provinces. Only the 146 former Cyprus buffer-zone pixels changed province ID. Every country population total is conserved. All 15,062 selection fields decode correctly. Every one of North Sumatra’s 17 provinces has complete State coverage away from the subpixel outer edge (zero missing interior pixels); all 21 internal adjacency boundaries are present. All 22,881 internal province adjacency boundaries globally are represented in the rebuilt mesh.

Country breadcrumb navigation, all owned States in the list, large-country list scrolling, unchanged left panel, return to State overview without a scroll, UI wheel blocking, compact layout, Cyprus merge, save/load and country names enabled passed. Camera movement leaves selection-upload and label-geometry-build counters unchanged.

General province redesign and demographic refinement are deferred.
