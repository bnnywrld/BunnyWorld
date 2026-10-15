# BunnyWorld 0.2.0.6 — Geographic States and Provinces

- Replace MD province bitmap registration with real geographic administrative shapes and independent province generation.
- Build 2,107 States, consolidating small subdivisions, enclaves and island groups.
- Build 9,194 provinces on local equal-area grids, guided by administrative edges, settlements, relief and rivers. Sparse desert and polar interiors use much larger cells.
- Retain all 223 scenario countries and their accepted territorial coverage.
- Repair native-texture fragments, regenerate identity textures and border meshes, and reconnect capitals, search, cities and territory inspection.
- Retain national population/building totals only as runtime bookkeeping. Local demographic refinement is deferred. No save migration is added.
- Retain the 0.2.0.5 interface and terrain graphics. Guard chart drawing against degenerate full-circle or tiny slices exposed by small States.

Use a fresh extraction and new campaign. Natural Earth administrative boundaries are geographic references; they do not reproduce every year-2000 administrative institution. Existing scenario controllers remain authoritative.
