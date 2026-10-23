# Bunny World 0.2.1.14 — Economy and public services

Start a **fresh campaign (save schema 29)**. Godot **4.5.1 Standard**, GL Compatibility. Close the game/editor, pull **clean-globe**, run **Prepare_BunnyWorld.bat**, then open **project.godot**. No EXE is included. The geography/display bundle remains **0.2.1.2**.

## Economy

The Economy toolbar opens **Overview, Budget, Production and Energy**. All 224 countries now settle national production, consumption, automatic trade and government budgets monthly. Starting GDP, population, building counts and employment are preserved. GDP subsequently follows population, productivity, employment, inputs and new construction; the overview separates nominal GDP from constant-2000-dollar GDP and shows actual last-month real growth.

Budget controls provide population/corporate taxes and military, administration, security, education, healthcare, welfare and research spending. Tax controls respect the active Taxation law. **Changes apply next month**; constitutional/law reforms still use Agenda. Recurring budget deficits use Treasury first, then borrow the shortfall. Debt incurs interest, with rates rising gradually with debt burden and fiscal stress. Surpluses stay in Treasury; the overview offers debt repayment. Construction continues to charge the **full price upfront**, borrowing when necessary; its payments/refunds are recorded separately and never charged again by the monthly budget.

**Trade** has ten clickable goods: Fossil Fuels, Steel, Light Metals, Precious Metals, Technology Metals, Rubber, Microchips, Advanced Composites, Food and Manufactured Goods. Domestic use comes first; affordable shortages are imported and surpluses exported automatically, using multiple suppliers where needed. Partner ranking considers relationships, outlook and proximity. Imports and exports use the same global benchmark, updated monthly from supply/demand with bounded movement. Export proceeds are business activity, not a Treasury windfall; public revenue comes from taxes. Actual suppliers, quantities, values and shortages appear in Trade.

Deposits retain **RU capacity** (one point from MD); monthly output uses **MU**, standardized market bundles with prices in USD per MU. Food uses one person's monthly food basket. These are gameplay units, not a conversion to tonnes. Cropland potential reads the existing year-2000 ESA terrain preparation; starting farms and unrepresented agriculture seed baseline food production. Agriculture Districts add output. Sustained severe food shortages can turn population growth negative. No conventional stockpile, detailed crop or company simulation is introduced.

Buildings supply explicit jobs, while baseline agriculture, services and other businesses retain the rest of starting employment. Hiring/unemployment adjust gradually each month as capacity and activity change; inactive residents are not automatically recruited. Staffed civilian industries assigned to construction keep their economic activity; the remainder produce Manufactured Goods. A gold-bordered **Manufactured Goods** box above the queue shows their factory count and last settled output.

## Education, healthcare and population

**Education quality** appears in Research and Society; it affects research speed and productivity growth. **Healthcare quality** appears in Society and Economy and modifies net population growth. Both range from 0–100. Sustained funding maintains quality; cuts slowly reduce it, and higher funding slowly raises it. Economy → Budget shows each quality's current trend and maintenance funding. R&D funding also affects research speed, with diminishing returns.

The shared base growth rate remains **+1% annually**, compounded monthly, with healthcare and sustained-food-shortage modifiers. Population tooltips in the top bar, national/state inspectors, Society and the ledger show a signed monthly projection, modifiers and recorded national change, colored green/red. Demographic proportions remain fixed: aging, separate births/deaths, migration, attitudes and approval are still inactive.

**Electricity is an empty framework**, as requested: no generation/consumption balance, shortage penalty, electricity trade or energy operating charge. Computing capacity, AI applications, military spending benefits, deeper public-service effects, economic cycles/crises, detailed production recipes, manual trade deals, sanctions, logistics and organization trade bonuses have connection points but remain inactive. Data Centers retain their existing construction/staffing/GDP path; computing and chip-maintenance mechanics await their later phase.

## Existing systems

- **Research:** 1,230 MD technologies in 11 clickable categories; oldest technologies at the top, prerequisites below, ahead-of-time penalties, retained progress and one project per university. Slot backgrounds fill light blue behind readable text. Education/R&D multipliers apply to daily progress and current-rate ETAs. Technology-specific effects and AI research remain future work.
- **Construction:** 23 types, including Data Centers ($6B, 36,000 points, 10,000 employees, one shared slot, cap 20). Same-state/type projects group and build sequentially with up to ten civilian industries per project. Shared capacity grows monthly with population; Infrastructure, Internet and Railroads have separate ten-level caps and capacity map palettes. No AI construction.
- **Government:** large party-grouped parliament, whole-party hover outlines, next-election display and dynamic government title. Named laws use inherited navy/gold pickers. Agenda queues reforms sequentially: 30 × steps² days and existing 100 × steps² PP prices; nominal constitutional/executive/electoral and faith-only changes take 30 days. Current laws remain until completion. No elections, cabinet or coalition mechanics.
- **Leaders and parties:** starting MD support fills 100 seats proportionally, excluding parties below 1% and the Salafist outlook. Supported outlooks are Western, Multipolar, Non-Aligned and Nationalist. Ruling/coalition metadata and leaders occupy their appropriate offices; missing second offices remain empty. 226 matching portraits come from a pinned official MD revision; Lebanon has no matching starting political leader. Party logos unavailable in the supplied archive retain initials/markers.
- **Society:** Population, Public Attitudes, Political Support and Migration sections. Religion categories use fixed colors across national/state charts. Religion & State requires an explicit faith for affiliated policies; it does not convert citizens. Unfinished society controls stay disabled.
- **Diplomacy/organizations:** compact header relations with colored modifier tooltips, a collapsible dock with 83 inactive diplomatic actions, membership cards and an organization-type map filter. All-alliances mode uses leader colors and geographic-centroid labels. Organization agreements do not yet alter the economy.
- **Presentation:** shared navy panels, muted borders, gold accents, compact demographics and currency names. Feature tabs slide when switching; Escape clears sea selection. Research, construction and Agenda completion notices expire after one real minute, including while paused.

## World and controls

Current world: **224 countries, 1,252 states, 13,074 provinces, 784 sea regions**, 6144×3072 display map. MD resource pools and cores/claims overlay canonical states without changing ownership/topology; named pools prefer their matching state and totals are conserved. Cores/claims use small flags with country-name tooltips. Baselines, packed asset parts and geography contracts remain required.

Controls: right-drag rotate; wheel zoom; left-click inspect; Space pause; 1–4 speed; Ctrl+F search; F focus; F5/F9 save/load; F11 fullscreen; Escape closes floating/side panels before the menu.

See [validation](TEST_RESULTS.md), [development](DEVELOPMENT.md), [sources and calibration](DATA_SOURCES.md), and [Windows export](documentation/EXPORT_WINDOWS.md). Temporary QA output and downloaded source archives stay outside the checkout.
