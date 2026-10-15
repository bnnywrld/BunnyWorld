# BunnyWorld 0.2.0.6 handoff

Baseline: complete 0.2.0.5 source/resources. User approved replacing MD-derived distorted States/provinces with real administrative geography, merging excessive small divisions, and building provinces with large sparse interiors. User explicitly deferred demographics and physical graphics work.

Implemented: 223 retained countries; 2,107 geographic States; 9,194 independent provinces. No MD province bitmap registration remains. Existing country control/coast coverage is unchanged. National population/building totals are retained as minimal bookkeeping; new local allocations are temporary. Modern administrative boundaries are reference geography, not exact 2000 administrative institutions. Scenario ownership remains year-2000-based.

Generation: build_geography_0206.py states; coarsen_states_0206.py; build_geography_0206.py provinces; repair_province_fragments_0206.py; link_geography_0206.py; existing boundary generation/compiler; Godot import. DEVELOPMENT.md gives commands and dependencies. Source inputs and baseline masks are retained. No old-save migration is authorized.

The 0.2.0.5 UI remains. Geometry tests cover every land pixel and country; engine integration covers country/State/province ownership and picking, territory drawers, search and same-version save/load. Native Windows graphics/performance require user testing. See TEST_RESULTS.md and BUILD_INFO.json for final verification.
