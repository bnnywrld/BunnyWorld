# BunnyWorld 0.2 — proposed patch roadmap

Updated: 14 October 2026.

## Purpose and status

Deliver the agreed demographic and political foundation in five substantial, bounded patches. This roadmap is a proposed implementation sequence, not a claim that work has begun or the latest map build has been inspected.

The detailed design is preserved in `BunnyWorld_0_2_Political_Framework.md`. The user's accepted rules take precedence over general implementation suggestions here. Each patch should deliver a runnable Windows package and matching source with change notes and verification results.

Version numbers assume 0.2 follows the completed 0.1 map series; confirm the latest actual release before implementation. Do not develop against the supplied old 0.1.0 source when a newer map source exists.

## Preparation before the first patch

- Obtain and inspect the latest complete map-build source, build notes, and population accounting. Preserve the working baseline.
- Fix any reported launch, picking, population-total, save/load, or severe performance problems that would undermine the new features. Do not expand into further decorative map work by default.
- Confirm the MD reference archive's completeness and supported scenario initialization before using it for political or financial imports.
- The user tests every version from a new game. Do not implement cross-version save compatibility, save migration, legacy-schema support, or backward-compatibility testing unless the user explicitly requests it. Normal saving/loading within the same version remains supported; reject incompatible old saves clearly rather than converting them.
- Use country-independent model code and data-driven country settings. Do not attempt to execute arbitrary HOI4 scripts as a substitute for supported import logic.
- Establish which scenario data can be imported and which need sourced estimates. Missing source values must be reported, not fabricated.

## Patch 0.2.0 — interface and starting demographic foundation

### Main deliverable

The player can inspect a country's starting population and compare countries through the new UI.

### Included

- Reconcile State totals, disjoint city/metropolitan/district groups, and shared remainder pools with the latest map implementation. Avoid double counting. Preserve population totals.
- Starting demographic profiles for age, religion, education, and economic activity. Use national or State estimates where finer data are unavailable; label provenance and uncertainty.
- Exactly three visible age groups: below 18; 18 to below the government-set retirement age; retirement age and above. Retain sufficient internal age detail for later aging and retirement-age changes.
- Religion uses major groups and important branches only, with nonreligious and unknown where needed. No ethnicity or gender simulation.
- National and State demographic charts with counts, percentages, and clear denominators. Economic activity distinguishes employed, unemployed, and outside the labor force; adult educational attainment does not classify all children as uneducated adults.
- Country-feature icon toolbar directly below the flag and country name; relocate existing navigation buttons. Show planned features as disabled with tooltips.
- Consistent generated icons for the toolbar and existing top-bar indicators, with readable numerical values and hover labels.
- Treasury and Debt indicators; import valid MD 2000 starting values after unit/initialization checks. GDP may also be imported where supported, for the ledger. No simulated budget flows yet.
- Ledger button and sortable country table: flag/name, population, GDP, GDP per capita, stability, war support, State count, government outlook, debt, treasury. Optional search and row-to-country navigation are small usability improvements.
- World Tension globe immediately right of the timer and its popup sections. Keep starting wars deferred; no invented event history. Finalize a clearly labeled initial tension convention before release rather than silently inventing a historical figure.

### Boundaries and verification

Static starting demographic profiles and financial balances are inspectable; births/deaths, full economics, elections, and wars are not added here. Existing outlook data can populate the ledger temporarily; revised outlook assignments follow in 0.2.1. Verify population accounting, aggregation, numerical sorting, tooltips, icon readability, and save/load. Profiles must not imply false province-level precision.

## Patch 0.2.1 — political institutions, parties, leaders, and Cabinet

### Main deliverable

Countries have recognizable governments and a coherent political panel, with Cabinet appointments as the first new political action.

### Included

- Data-driven government properties and office selection rules for parliamentary, presidential, and single-ruler systems; explicitly map other systems such as semi-presidential governments without inventing an approval route.
- Two portraits around a 100-seat party semicircle. Correctly label country offices; the proposed US second portrait is the Speaker, not a second executive office. Resolve this presentation before implementation.
- Hovering a seat highlights its entire party and displays name and seat percentage.
- Separate legislative and presidential election information where appropriate; no scheduled elections shown as "Never". Hereditary and indirect offices are correctly identified.
- Four outlooks: Western, Multipolar, Sovereigntist, Non-Aligned; simple ideology labels nested under outlooks; actual parties with colors, leaders, support, and seats.
- Starting governing parties/coalitions, outlook affinity, and separate public support data. No automatic alliances from shared outlook.
- Government-property icon row and fundamental-law row. Display current settings and effects; enacted reform mechanics follow in 0.2.2.
- Cabinet button near portraits/parliament, sliding a smaller panel right. Ministers have role-specific traits; replacing them costs Political Power. Finalize the proposed seven-office roster and eligible candidate rules before implementing.
- Base Political Power generation of +1/day and Cabinet-related modifiers needed for appointments. Complete modifier balancing follows in 0.2.2. Future economic or military traits are labeled inactive until their systems exist.
- Save support for political structures, parties, leaders, and appointments.

### Boundaries and verification

Treat scenario data preparation as substantive work, not a free addition. Import reusable MD party/leader information where supported; verify starting offices for 2000. Do not invent historical ministers or parliamentary compositions to fill gaps. Avoid a huge fictional portrait-generation project in this patch. Verify 100-seat totals, titles, appointments/costs, regime mappings, and persistence. Election dates are displayed but elections do not yet change governments.

## Patch 0.2.2 — laws, reforms, Political Power, and Government Approval

### Main deliverable

Players enact political changes and see their costs, timing, and public consequences.

### Included

- Full Political Power generation and tooltip breakdown: base +1/day; laws; organization memberships; coalition strength/seats; leader traits; stability; Government Approval; parliamentary head-of-state/head-of-government party relationship.
- Resolve nonpartisan and hereditary head-of-state handling; recommendation is neither same-party bonus nor different-party penalty. The head of state receives no parliamentary reform veto.
- Universal 0–100 Government Approval, distinct from stability and support/seat percentages. Explain contributing factors and trend.
- System trade-offs: parliamentary approval benefit/coalition exposure; presidential stable executive and faster reforms with own-party majority; single-ruler fastest/cheapest reforms but stronger approval sensitivity.
- Clickable government properties and laws with preview menus: cost, requirements, enactment time, and approval consequences.
- Agreed approval rules: parliamentary coalition needs 51 seats; president's own party needs 51 seats plus president backing; single-ruler party has all 100 seats. Coalition supports all reforms, opposition opposes all. No negotiated opposition votes or referendums.
- One major reform at a time with progress, completion notification, and clear blocked states.
- Eight accepted initial law directions, plus government-set retirement age. Finalize exact settings and effects before balancing. Changes to government form must update applicable rules coherently.
- Retirement-age changes recompute age-group shares without creating people or jobs; raising retirement age reduces approval. Underage and retired populations generate no population tax income and determine education/pension cost bases. Show future finance connections without claiming a budget already exists.
- World Tension event-recording foundation for explicitly defined implemented events only. No arbitrary tension increases for every domestic reform.

### Boundaries and verification

No referendum, individual legislator, bargaining, or detailed policy-axis simulation. Constitutional thresholds are still unresolved; settle them before coding rather than silently adding the earlier proposed 67-seat rule. Verify approval routes, insufficient-PP behavior, daily modifiers, reform completion, population reclassification, and saves. Avoid double-counting coalition strength/seats and duplicate cost modifiers.

## Patch 0.2.3 — elections, coalitions, protests, and political AI

### Main deliverable

The political world changes over time and governments respond to public dissatisfaction.

### Included

- Simple legislative elections producing exactly 100 seats and presidential elections on separate schedules. Selection and inauguration can be distinct where scenario rules require it.
- Approval affects governing-party support; distribute opposition gains through a bounded, transparent rule. Do not assume vote share always equals seat share without explicitly choosing the simplified electoral conversion.
- Simple coalition options with seat totals and expected durability. Shared outlook helps compatibility; coalition parties support reforms until coalition membership actually changes.
- Coalition strain and collapse; orderly government replacement or an election where applicable.
- Sustained low approval produces warnings, demonstrations, and escalating protests. Parliamentary crises lead to early elections. Presidential crises do not trigger early presidential elections; protests weaken reform effectiveness without changing the own-party seat rule.
- Responses: address grievances, negotiate temporary protest relief for Political Power, or crack down with approval/escalation risks.
- Single-ruler crisis choice: stepping down leads to revolution; refusal leads toward civil war. Preserve the agreed design, but do not implement fake combat outcomes. Finalize which transition can be supported now; keep full civil war deferred until military mechanics exist and explain that boundary in the UI/release notes.
- Head-of-state succession and simple indirect selection for represented systems, with sourced successors/candidates where possible and clearly identified fictional replacements if later authorized.
- Basic political AI uses the same approval/cost rules for Cabinet appointments, reforms, coalition selection, and crisis responses. No full campaign AI, military AI, or detailed diplomatic negotiation.
- Political notifications and persistent event history.

### Boundaries and verification

Concentrate on peaceful political turnover, coalition stability, and protest responses. Verify scheduled/early elections, unchanged presidential tenure during ordinary approval crises, seat totals, AI legality, succession, escalation/recovery, and long-run saves. Set limits that prevent a perpetual election or unavoidable protest spiral. Full revolution settlement and civil-war armies/territory remain future design work where dependencies are absent.

## Patch 0.2.4 — demographic evolution and economic handoff

### Main deliverable

Population evolves, demographic forecasts are understandable, and the game is ready for its economic development phase.

### Included

- Country-specific births, deaths, and aging with periodic simulation updates rather than per-frame processing. Convert annual rates consistently to the chosen cadence.
- Gradual transfers into working age at 18 and retirement-age groups at the government-set threshold.
- Population-weighted updates through city groups and remainder pools, keeping province references consistent and updating city visuals only through existing supported map hooks.
- Demographic summaries: natural change, births/deaths, age distribution, potential working-age population, and trends.
- Show education and pension cost bases and, if rates are finalized, clearly labeled projections. Do not deduct actual Treasury expenses until a coherent revenue/spending model is authorized.
- Internal labor-force definitions and education measures consistent with the later economy. Avoid automatic jobs or tax income from age changes.
- Basic migration accounting interfaces preserving population when transferring groups, but no unsupported automatic migration or large migration AI. Detailed drivers follow the economy/diplomacy.
- Consistency pass across charts, political costs, Cabinet traits, tooltips, ledger, and source metadata.
- Performance and long-run simulation checks justified by evolving populations and political systems.

### Boundaries and verification

No constant exponential growth detached from future age structure as the permanent model. No detailed occupations, wealth classes, every demographic cross-combination, or individual people. Verify population conservation except recorded births/deaths, age transitions, changed retirement thresholds, national totals, deterministic progression where supported, and saving/loading within this version only.

## Next development phase: economy

Once this foundation is tested, develop an economic model using inspected MD formulas as reference: employment and earnings; taxation; education/health/social budgets; pensions; Treasury flows; debt and interest; and State investment. The exact version label can be chosen later (for example 0.3). Do not append the entire economy to the last demographic patch merely because starting financial figures already exist.

## Shared small improvements

- Keep icon style, hover labels, numeric formatting, and panel behavior consistent.
- Explain inactive and missing data rather than displaying misleading zeroes or bonuses.
- Retain country-specific titles but common internal role identifiers.
- Pair every new persistent state with save handling for the same version only. Cross-version compatibility is excluded unless explicitly requested later.
- Test model behavior headlessly where meaningful, inspect the actual UI, and package the tested build. Native Windows launch/performance still require user feedback when unavailable in the development environment.
- Review each completed patch before adding another system. A discovered blocking defect gets fixed without automatically expanding the patch into unrelated work.

## Deferred scope

The user approved this five-patch sequence and the suggested small improvements in their fitting patches. Cross-version save compatibility is explicitly excluded indefinitely unless the user requests it; it is not an automatic task for a later release.

Full warfare/civil-war operations, upper chambers, detailed economic simulation before the next phase, ethnicity/gender population dimensions, complex religious denominations, individual legislative votes, referendums, large focus trees, space exploration, and full organization integration/voting mechanics.

No fixed delivery-time estimate is implied. The source and data audit may expose a large global-data gap; report it and revise the data work concretely rather than hiding missing country coverage or fragmenting the feature roadmap into tiny releases.

## Implementation record — 0.2.0

Implemented on 14 October 2026 using 0.1.12 revision 2. Delivered the demographic starting foundation, icon UI, Treasury/Debt import, sortable Ledger and World Tension popup. Starting profile coverage: age 220, religion 169, education 179, activity 208 of 223 scenario countries, including clearly labeled parent proxies; unsupported values remain unknown. Treasury/debt supported for 210/195 countries. Education supplemented with authors' Barro-Lee 2000 estimates. Retirement age currently uses a 65-year gameplay baseline, pending reform laws in 0.2.2. All 0.1.12 national population totals retained. No population evolution or budget flows yet. Same-version saving retained; no migration. Model and graphics/UI checks pass with the exact Windows PCK under the matching Linux runtime; native Windows launch remains for user testing. Refer to the 0.2.0 source archive for implementation and source notes.
