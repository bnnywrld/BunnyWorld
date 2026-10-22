# Bunny World 0.2.1.8 — Construction

The **Construction** toolbar button opens a private construction map and a queue/building picker in the existing UI style. Choose a building, then click an owned state to queue one level. Light green means more free shared slots, dark green fewer, blue full; yellow stripes mark queued construction. Closing the tab restores the previous map mode. Construction mode is not available in the general map selector.

Projects use up to **10 civilian industries each**, allocated in queue order. Adjust allocations, move priority up/down, or cancel. Unassigned industries are counted as producing **Manufactured Goods**; volumes, stockpiles and trade await the economy. Progress runs daily while the clock is playing. No AI construction.

The 22 state building types use supplied MD construction-point and monetary costs. Adding a job pays upfront from Treasury and borrows any shortfall. Cancellation refunds the unfinished fraction, reversing that job's borrowing first. Completed economic buildings add annual GDP output using MD base coefficients and starting productivity; existing GDP is preserved. No automatic Treasury income, taxes, interest, employment, energy or market simulation yet.

State capacity uses a generous logarithmic population/area curve with headroom above existing buildings. Infrastructure, Internet Infrastructure and Railroads each have **10 separate levels**, using no shared slots. Railroads currently represent a state network using MD rail-terminal costs/output; province routes, forts, ports and research facilities are later work. Use a **fresh campaign** (save schema 23).

The **Organizations** toolbar button opens your country's memberships as large clickable cards. Open a card for **Members** and **Features**, headquarters, type, outlook affinity and integration level. Cards show counts rather than long member lists. Member rows open country information. The directory also shows the remaining design definitions, clearly inactive pending membership review.

The 19 existing scenario member lists are preserved. All eight organization types have a data foundation; full/associate/observer/partner/suspended statuses and integration opt-outs are saved. Security alliances allow at most one full membership. No organization actions or PP/opinion/economic/military effects are enabled yet: the document leaves balance values and agreement mechanics pending. Unimplemented features are labeled **Planned**.

In **Organizations map mode**, a gold star marks the selected organization's headquarters and national capital/city markers are hidden. Fixed seats are linked to the existing place catalog, falling back to a labeled host-country location if unavailable. Organizations without a fixed HQ get no artificial star. OAU/AU and CST/CSTO labels follow the campaign date; memberships do not automatically change.

Start a **fresh campaign** (save schema 23). Geography, map assets and population are unchanged.

Use branch **clean-globe**. The new globe is connected to the existing country panels, politics, demographics, eight map modes and save system. Current map: **6144×3072**, **224 countries, 1,252 states, 13,074 provinces and 784 sea regions**.

Law choice windows now use the same navy frame, gold accents and button theme as the game panels. Click another law to switch the open picker directly; Escape or × closes it. Changes still cost **100 PP** and apply no effects.

The **Research** tab lists national universities/research institutions. Click an institution to open its **empty technology-tree window**. This patch adds UI only: no technologies, research timers, queues, funding calculations or bonuses. Institution names are deterministic; the provisional country slot counts follow the design's 2–6 range.

Government now has six compact icon rows covering all 28 Constitution & Laws settings. Click a law to see its current selection and alternatives. Each change costs **100 Political Power**, with no law effects or action restrictions yet. The government-type title updates from the selected governance laws. The panel scrolls vertically and choices are saved.

Country-specific year-2000 starting laws are seeded for all 224 countries, including Japan's constitutional monarchy. Broad policy categories are scenario abstractions; some country defaults will need later historical refinement. Map styling and obsolete-capital cleanup from 0.2.1.4 are retained.

Close Godot/game, pull **clean-globe**, run **Prepare_BunnyWorld.bat**, then open **project.godot** in **Godot 4.5.1 Standard**. Application version: **0.2.1.8**; geography/display bundle: **0.2.1.2**. Use a fresh campaign for testing. No EXE is included.

Prepared boundary resources have been rebuilt from the existing canonical map with the checked-in tools to repair stale build provenance. Province/sea PNGs, ownership, population, state/province IDs and demographics are unchanged. Packed assets are required; preparation verifies them before opening the game.

See [validation](TEST_RESULTS.md), [development](DEVELOPMENT.md), and [Windows export instructions](documentation/EXPORT_WINDOWS.md). Windows/laptop FPS remains unmeasured.

Controls: right-drag rotate; wheel zoom; left click inspect; Space pause; 1–4 speed; Ctrl+F search; F focus; F5/F9 save/load; F11 fullscreen; Escape menu.
