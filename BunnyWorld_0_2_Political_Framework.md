# BunnyWorld 0.2 — Political framework

Updated: 18 October 2026.

## Status and scope

Version 0.2.1 implements compact portrait/parliament placeholders in Government and country/diplomacy panels, changeable government properties costing 100 PP, +1 base PP per completed day, and a colored daily-income breakdown. Properties and PP persist in new-schema saves. Real leaders, parties, seat allocations, election dates, reforms and wider modifiers remain planned; the detailed sections below describe that intended design, not implemented mechanics.

Demographics and the political foundation precede the economy. The initial demographic direction includes age, religion (including nonreligious populations), education, and economic activity. Gender is omitted; ethnicity is postponed. Detailed employment follows with the economy.

## Agreed political direction

### Country panel

- Two portraits flank the legislature visualization.
- In systems with separate offices, show the head of state and head of government, with their names and actual titles.
- The US president holds both executive roles. The proposed second portrait is the Speaker of the House, explicitly labeled as legislative leader, not head of government. This was recommended in discussion; the precise presentation remains to be confirmed.
- Show parliament as a classic semicircle of seats, grouped and colored by party.
- Use exactly 100 gameplay seats: each seat represents 1%. These are the seats used for majority and coalition calculations, rather than a hidden real-size legislature.
- Hovering a seat highlights all seats belonging to that party. Its tooltip shows the party name and seat percentage.
- Parties without seats may remain available in the party list for later elections.
- Show the next legislative election beneath parliament. Use "Never" where there are no legislative elections; unknown or postponed dates must not be treated as no elections.
- Presidential elections need a separate date where applicable. Not every republic has a directly elected president.
- Offices may be filled through direct election, indirect election, parliamentary appointment, hereditary succession, or another country-specific procedure.
- Monarchs change through succession, including death or abdication, rather than parliamentary election results.
- Countries without a legislature must not be given a fictitious parliament.
- Initial proposal: represent the principal elected chamber and defer upper chambers.
- Starting offices and institutions must reflect the 1 January 2000 scenario rather than current-day leaders or rules.

### Government properties

Agreed interface: a separate horizontal line beneath the portraits and legislature. Each property has an icon. Hovering explains its meaning and effects; clicking opens a mini menu to change it. Changes incur political costs, potentially including political power and stability.

Proposed properties:

| Property | Purpose |
| --- | --- |
| Constitutional form | Republic or monarchy; hereditary status of the head of state. |
| Executive system | Presidential, parliamentary, semi-presidential, or another arrangement. |
| Political competition | Competitive democracy, restricted competition, one-party rule, or closed authoritarian rule. |
| Selection rules | How the relevant offices are filled. |
| Distribution of power | Powers of the executive, legislature, and other governing institutions. |

The exact property list remains a proposal. Major constitutional changes should use a reform process rather than instant replacement. Costs, time, approval requirements, resistance, and effects remain to be designed. Avoid duplicating the same mechanic across government properties and ordinary laws.

### Outlook → ideology → party

The user approved a simple hierarchy:

1. Geopolitical outlook: broad political and international camp.
2. Ideology: domestic political orientation within that camp.
3. Party: the actual organization with a name, color, leader, support, and seats.

Keep this manageable; detailed multidimensional party policy modeling is postponed. A party has one primary outlook and an ideology label. The same ideology can exist under several outlooks.

| Outlook | Definition | Illustrative ideologies, not an exhaustive roster |
| --- | --- | --- |
| Western | Support for Western-style liberal democracy, civil liberties, and cooperation with the Western-led international order. | Conservative, liberal, social democratic, green. |
| Multipolar | Support for several independent centers of power and alternatives to Western dominance; accommodates different domestic systems. | Socialist, communist, conservative, developmentalist. |
| Sovereigntist | Priority on national independence and freedom from outside political control, including resistance to deeper integration. | National conservative, nationalist, sovereigntist left. |
| Non-Aligned | Avoidance of commitment to competing power blocs, with practical cooperation across them. | Centrist, conservative, social democratic, socialist. |

"Multipolar" replaces the proposed use of MD's "Emerging" label. "Sovereigntist" is the outlook; nationalism can remain an ideology. Religious politics are represented through party ideology and institutions rather than a fifth geopolitical outlook.

These categories are game abstractions, not definitive historical classifications. China and Russia are candidates for the Multipolar camp in the proposed scenario design; country assignments still require research and review.

### How outlooks matter

- Parties within the same outlook are more likely to cooperate, form coalitions, and support reforms.
- Similar ideologies can add compatibility; shared outlook does not eliminate policy disagreements.
- Coalitions across outlooks remain possible, with greater potential disagreement.
- Countries with the same outlook form an informal geopolitical bloc and prefer closer relations, economic cooperation, and common projects.
- Actual alliances, treaties, and international organizations remain separate persistent entities; shared outlook does not automatically create membership or guarantee friendship.
- Disputes, interests, and commitments can outweigh shared outlook.
- Proposed country outlook: derive it from the governing leadership or coalition, not directly from the largest demographic group. Mixed coalitions need a clear primary outlook and secondary information.
- Public outlook support is shown separately from parliamentary seats. Public support and seats can differ.
- Religion, age, education, employment, and living conditions may eventually influence political preferences. No demographic category automatically determines a person's party or outlook.

## Newly requested law row

The user requested fundamental laws beneath government properties, including freedom of speech and conscription. They should be changeable through the same icon, tooltip, and mini-menu interaction, with political costs and consequences.

### Accepted initial category direction — detailed settings and balance pending

| Law | Example settings | Intended future connections |
| --- | --- | --- |
| Speech and media freedom | Free expression; restricted expression; extensive censorship. | Public criticism, political organizing, legitimacy, and information. |
| Freedom of assembly | Protected assembly; permit restrictions; opposition assembly banned. | Protests, party organization, and repression. |
| Religious freedom | Equal freedom of belief; privileged official religion; restricted religious practice. | Religious communities, public support, and rights. |
| Judicial independence | Independent courts; politically influenced courts; executive-controlled courts. | Limits on executive action, legal predictability, and reform resistance. |
| Military recruitment | No standing armed forces; volunteer service; selective conscription; broad conscription. | Available personnel, civilian workforce, and military costs. No gender-specific categories. |
| Immigration and asylum | Broad access; regulated admission; restrictive admission; near-closed admission. | Migration, labor supply, population, and domestic support. |
| Citizenship | Inclusive naturalization; standard naturalization; restrictive naturalization. | Incorporation of migrants and, later, political participation. |
| Labor rights | Strong protections; standard protections; limited protections. | Employment conditions, worker support, productivity, and business costs. |

Example settings are design sketches, not finalized labels or numerical modifiers. Religious freedom describes legal rights; an official religion or theocratic constitutional form can be a distinct government property. Immigration and citizenship need distinct effects to justify separate icons.

Later candidates: healthcare model, education access, pensions and retirement age, trade policy, environmental regulation, surveillance/emergency powers, and foreign intervention policy. Budget allocations belong on the later finance screen; policy rules can remain laws. Detailed military and economic effects become active when those systems exist.

### Proposed reform behavior

- Preview political power cost, time, requirements, and expected effects before enactment.
- Support and stability consequences depend on affected groups and the direction of reform; every change should not automatically reduce stability.
- Legislative approval, executive authority, and constitutional limits depend on government properties.
- Major changes take time; prevent repeatedly switching laws to harvest effects.
- Repression can suppress visible opposition while creating longer-term grievances; do not present it as a universally beneficial stability bonus.
- Tooltips distinguish effects implemented now from future system connections. Do not claim inactive modifiers affect gameplay.
- Numerical balance remains undecided. Legislative support follows the simplified rules below.

## Agreed simplified reform approval rules

Confirmed by the user after the initial law proposal. These rules supersede proposals for case-by-case opposition cooperation, negotiated votes, and referendums.

- The player acts as the governing leadership; choosing a change initiates a government reform.
- Parliamentary systems: the head of state has no approval or veto role in reforms. The governing coalition supplies its seats in support; passage requires a majority, meaning at least 51 of the 100 seats.
- Presidential systems: the president must back the change and the president's own party must hold at least 51 of the 100 seats. Other parties cannot supply the missing seats for this approval rule, including through ad hoc cooperation. Coalition support does not override this presidential own-party requirement.
- Coalition parties support government changes. Opposition parties oppose all changes. No individual legislator votes, cross-party exceptions, opposition bargaining, or conscience votes are simulated.
- Single-ruler governments have a 100-seat legislature entirely filled by the ruler's party. All seats support the ruler's changes automatically. This is an intentional game abstraction, not a claim about every real authoritarian legislature.
- No referendum mechanics.
- Political power, enactment time, and public support or stability consequences still apply even when parliamentary approval is guaranteed. Their exact balance remains pending.
- Ideology and outlook can affect coalition formation and public reactions, but cannot cause a coalition party to defect from a reform vote under these rules.
- Do not automatically approve all reforms for every non-democratic system: the guaranteed 100-seat rule specifically describes single-ruler governments. Other special systems need a simple explicit mapping.
- The previously suggested 67-seat threshold for constitutional reforms was not finalized. Do not silently add a supermajority requirement. Constitutional versus ordinary reform costs and any distinct threshold remain to be settled.

## Millennium Dawn reference inspected

Reference archive: `bunnyversion.zip`, provided locally. This was inspected for suggestions, not asserted to be the newest complete mod.

Relevant files inside the archive:

- `New folder/common/ideologies/00_ideologies.txt`: outlook grouping and subtype definitions.
- `New folder/common/ideas/AA_law_military_ideas.txt`: conscription, military spending, foreign intervention, officer training, and gender-specific military policies. Gender-specific policies are not proposed for BunnyWorld's initial model.
- `New folder/common/ideas/AA_law_migration_ideas.txt`: immigration settings from open to closed borders.
- `New folder/common/ideas/AA_law_budget.txt`: administration, policing, education, healthcare, and social spending.
- `New folder/common/ideas/AA_law_economics.txt`: trade policy and economic-cycle states. Economic cycles should be simulated conditions, not freely selected laws.
- `New folder/common/ideas/AA_law_expanded_economics.txt`: employment regulation, healthcare ownership, environmental mining policy, infrastructure maintenance, and currency-related policy.
- `New folder/common/ideas/AA_law_religion.txt`: religion-related ideas; these should not be copied as demographic changes enacted by clicking a law.
- `New folder/common/ideas/political_reform.txt`: open/censored/closed-nation reform ideas.

## Agreed government approval and system trade-offs

Confirmed by the user on 14 October 2026. Government Approval replaces the earlier suggestion of a discontent indicator exclusive to single-ruler governments.

### Universal approval

- Every country and government system uses one Government Approval score, from 0 to 100%.
- Approval measures public satisfaction with the governing leadership. It is separate from stability, which measures order and institutional stability, and from party/outlook support and parliamentary seats.
- Economic conditions, reforms, and events affect approval. Low approval can put pressure on stability over time; the two indicators do not move identically.
- Parliamentary approval of a reform does not imply public approval: a law may pass while being unpopular.
- No separate hidden discontent meter is required for single-ruler systems.

### Benefits and trade-offs

These are deliberate gameplay abstractions, not claims that a political system automatically produces these outcomes in reality.

| System | Advantages | Trade-offs |
| --- | --- | --- |
| Parliamentary | Modest government approval benefit from broader representation; coalition parties can combine to reach 51 seats. | Coalitions may be unstable; a breakdown can cause government changes and approval losses. Coalition formation or collapse is separate from reform voting: while a coalition exists, its members support all reforms. |
| Presidential | Stable executive tenure and faster, more effective reform enactment when the president's own party has 51+ seats. | Smaller approval benefit than parliamentary government; losing the president's party majority blocks reforms. Protests reduce reform effectiveness even with a sufficient majority. |
| Single-ruler | Guaranteed 100-seat legislative backing, fastest reform enactment, and lower political power costs. | Approval reacts especially strongly to major unpopular laws and poor economic conditions. Popular reforms can also produce substantial gains. Severe protest crises can end the regime. |

Exact bonuses, costs, enactment speeds, approval sensitivity, and coalition instability probabilities remain to be balanced.

### Very low approval and protest crises

The user specified the following system-dependent outcomes:

- Parliamentary systems: very low approval leads to protests and early elections.
- Presidential systems: very low approval leads to protests, without approval-triggered early presidential elections. Protests continue weakening the government's effectiveness at passing laws. Represent this through reform time and/or political power costs, not opposition votes or coalition defections. The president's own-party 51-seat requirement remains unchanged.
- Single-ruler systems: protests can escalate to a regime crisis. If the ruler chooses to step down, the outcome is a revolution; if the ruler refuses to step down, the outcome is a civil war. Preserve these user-selected outcome names rather than silently replacing voluntary departure with an ordinary leadership succession.
- Player-controlled rulers choose whether to step down or refuse. The AI decision rule remains to be designed.

Implementation details remain pending: very-low-approval thresholds, persistence requirements, protest escalation timing, penalty size, post-revolution institutions, and civil-war participants and territorial division. A brief dip in approval should not silently be treated as an instant implemented civil war. Full civil-war gameplay depends on the later military system; its design here does not authorize starting military implementation or claiming it exists.

## Accepted political usability and progression improvements

The user accepted the following additions after the approval and crisis discussion:

- Approval tooltip: show the main contributing factors, including economic conditions, recent reforms, protests, and government-system effects, plus a rising/falling trend.
- Gradual crisis escalation: sustained low approval progresses through demonstrations and major protests before reaching the agreed system-specific outcome. Give warnings and recovery opportunities. Exact timing and thresholds remain pending.
- Simple coalition formation: after parliamentary elections, present a few compatible coalition options with combined seats and expected durability. Shared outlook improves durability; mixed outlooks are more fragile. Low approval and electoral setbacks can strain coalitions. Coalition members continue supporting all reforms until the coalition actually changes or collapses.
- Election consequences: low approval harms governing-party support; opposition gains depend on existing support and outlook. Small approval dips do not automatically replace governments.
- Reform queue: one major political reform at a time, with visible progress, costs, and predicted approval effects.
- Clickable notifications for elections, coalition changes, enacted laws, succession, and protest escalation.
- Crisis responses: address grievances by changing policy; spend political power to negotiate a temporary reduction in protest intensity; or order a crackdown with a risk of further approval losses and escalation. Temporary suppression or negotiation does not automatically resolve underlying public dissatisfaction.
- Avoid an unavoidable crisis loop where protest penalties prevent every recovery action. Exact safeguards and costs remain pending.

Recommended release sequencing, not a finalized implementation commitment: first 0.2 release establishes demographics, political presentation, laws, approval, and basic reforms; subsequent 0.2 patches add election and protest simulation. Full revolutions and civil wars require later systems.

## Demographics — existing direction and expanded discussion proposals

### Existing direction

- Population demographics precede the economy.
- Age, religion, education, and economic activity are supported as the initial direction; category boundaries remain open.
- No gender breakdown in the initial simulation. Ethnicity is postponed.
- Different breakdowns describe the same population and must not be added together as separate populations.
- Relevant tabs display pie charts with legends, counts, percentages, and hover details. Chart choice can be revisited where another format is more readable.
- Prior map-planning context includes named city/metropolitan province groups, district groups where a large city spans provinces, and a shared remainder pool for other provinces in each State. Preserve this direction when integrating demographics; verify the latest map source and accounting before implementation. Never count city populations again in the State remainder.

### Proposed population accounting

- State total = sum of disjoint city/metropolitan/district group populations + shared remainder population.
- Country total = sum of its State populations.
- Provinces referencing a shared group do not each store another copy of that group's population. A countryside province shows its shared-pool affiliation rather than implying the full pool lives in that province.
- Where a city province includes countryside, account for the population of the whole covered area, not only the municipal population. Metro and district boundaries must not overlap in accounting.
- Demographic profiles can initially be stored for city groups and State remainder pools; use State or national estimates where local data are unavailable, with provenance recorded. Do not fabricate precise local differences.

### Proposed demographic breakdowns

| Dimension | Initial proposal | Notes |
| --- | --- | --- |
| Age | Underage: below 18. Working age: 18 to below the government's retirement age. Retired/retirement age: at or above that retirement age. | User-approved boundaries. Retirement age is a government-set law. Actual work or retirement status is separate. Any internal aging detail must not introduce extra visible age categories. |
| Religion | Broad religious groups and only the most important branches, plus nonreligious and unknown where necessary. | User-approved limited detail; no further denomination hierarchy planned. Exact category roster remains pending. Religious identity alone does not determine political support. |
| Education | Below completed primary, primary, secondary, tertiary; treat children still in education separately when interpreting attainment. | Show a clearly defined adult attainment denominator. Exact age cutoff and mapping remain pending. |
| Economic activity | Employed, unemployed, outside the labor force. | Students and retirees can be explanatory subgroups, but are not automatically mutually exclusive with employment. Unemployment is unemployed / labor force, not unemployed / total population. Detailed employment begins with the economy. |
| Settlement | City-group population and State remainder, with a separate urban/rural estimate only if data support it. | Remainder is not automatically rural: city groups can include countryside, and smaller towns may be in the remainder. |

### Proposed demographic evolution and interface

- Begin with country-specific births, deaths, and age progression; add migration once its drivers and destination rules are implemented.
- Avoid constant percentage growth forever; age structure should eventually influence births and deaths. Aggregate demographic rates can operate without tracking individual sex or gender.
- Migration transfers people and their profiles; domestic movement conserves national population, and international movement conserves global population. Births increase totals; deaths reduce them.
- Update demographic simulation periodically rather than every render frame. Cadence and rate conversion remain to be designed.
- National and State demographic panels should use population-weighted aggregation, not an unweighted average of percentages.
- Show total population, annual natural change, net migration where implemented, and a trend. Provide chart tooltips with counts, percentages, and denominator.
- Initial scenario figures refer to around 2000. Preserve source year, geography, estimate status, and confidence where relevant. Distinguish observed data from modeled estimates.
- Avoid simulating every possible combination of age, religion, education, and employment at first. Use aggregate groups; introduce joint distributions only when a gameplay mechanic needs them.
- Proposed initial scope: reliable accounting, starting profiles, charts, births/deaths, and basic aging. Detailed migration, occupational classes, income groups, and demographic political preferences follow later.

### Latest demographic decisions

The user accepted education and economic activity as demographic dimensions, accepted religion with only the most important branches, and requested exactly three age groups: underage, working age, and retired. These decisions supersede the earlier four-group age display and suggestions for progressively more detailed religious categories.

The working-age boundary is fixed at 18. Retirement age is set by the government through a retirement-age law, using the agreed reform approval and cost rules. Age groups are: below 18; from 18 up to but excluding retirement age; and retirement age or above. Available retirement-age settings, scenario starting values, reform balance, and pension mechanics remain to be finalized. Retirement age must exceed 18.

Changing retirement age reclassifies the existing population without changing the total population or automatically changing anybody's job. Retain enough internal age detail to recompute the groups accurately rather than moving an arbitrary fraction between groups. The interface still shows only the three agreed groups. Future effects can include potential labor supply, pension eligibility and spending, and public approval; these connections must not be claimed active before their systems exist.

Education and economic activity category details and the religious branch roster remain to be finalized. Retain the simple employment split: employed, unemployed, outside the labor force. A working-age person is not necessarily employed, and a retirement-age person may still work. Age and economic activity therefore remain separate breakdowns.

### Agreed age-group economic roles

- Underage population generates no tax income. Its size determines the population-dependent education cost.
- Retired/retirement-age population generates no tax income. Its size determines the population-dependent pension cost.
- These are deliberate simplified gameplay rules. They override any later assumption that a retirement-age person automatically contributes tax revenue merely because economic activity records them as working.
- Education funding/service level determines cost per underage person; pension policy determines cost per retirement-age person. Exact rates, budgets, and time units remain to be designed. Other education costs, such as higher education, are not yet specified.
- Raising retirement age reduces the retirement-age group and moves those people into the working-age group; lowering it does the reverse. Total population is conserved. This changes the future pension-cost base, but does not itself create jobs, wages, or tax revenue.
- Raising retirement age decreases Government Approval. This is an explicit agreed reform consequence, in addition to normal approval and enactment requirements. Penalty magnitude and duration remain to be balanced; an approval benefit for lowering retirement age has not been specified.
- Working-age tax generation will be defined with the economy. Do not assume every working-age person earns taxable income: employment, earnings, and tax policy still need a model.
- This agreement concerns population-generated tax income. Corporate taxes and other government revenue sources remain undecided.

Other expanded demographic specifications above remain discussion proposals unless explicitly accepted. The latest map build must be inspected before settling the population schema.

## Agreed Political Power model

The user specified a Millennium Dawn-like resource with a base generation of 1 Political Power per day.

- Political Power accumulates and pays for reforms and other political actions. Existing agreed reform approval rules still apply; spending Political Power cannot substitute for the required seats.
- Government laws can increase or decrease daily generation.
- Membership of international organizations can increase or decrease daily generation according to the organization and its commitments; membership is not automatically always beneficial or always costly.
- Coalition strength and parliamentary seat count affect daily generation. Larger governing majorities and stronger coalitions should provide greater political capacity; exact formulas remain pending.
- Leader traits affect generation. Charismatic leaders receive bonuses; uncharismatic leaders receive penalties. Trait magnitude and stacking remain pending.
- High stability increases daily Political Power generation; low stability decreases it.
- High Government Approval increases daily Political Power generation; low approval decreases it. Approval and stability remain separate contributing factors, with exact neutral points, ranges, and modifier sizes pending.
- In parliamentary systems, the head of state belonging to the same party as the head of government increases Political Power generation; belonging to a different party decreases it.
- This parliamentary head-of-state modifier does not grant the head of state a vote, approval requirement, or veto over reforms. They still have no say in the reform approval process under the agreed simplified model.
- Proposed handling, not yet explicitly approved: a nonpartisan or hereditary head of state gives neither the same-party bonus nor the different-party penalty. Do not invent party membership for monarchs.
- The existing US proposal places the Speaker in the second portrait slot; do not misinterpret that Speaker as a separate head of state or apply the parliamentary two-office modifier to the US.

Suggested readable presentation: show current Political Power and net daily gain. Hover lists the base +1/day and every active modifier separately. Exact flat versus percentage modifiers, bounds on daily generation, stockpile limits, costs, and balance remain to be finalized. Avoid double-counting coalition seats and coalition strength for the same benefit.

## Agreed Cabinet panel

- Place a button labeled "Cabinet" near the portraits and parliament area in the country control panel.
- Clicking it slides out a smaller panel to the right, beside the main country control panel.
- The player can choose government cabinet members for ministerial offices. Defense and labor were explicitly requested as examples; the full office roster remains to be finalized.
- Cabinet members provide bonuses relevant to their assigned role. Exact traits and balance remain pending. Effects tied to unimplemented economic or military systems must be identified as future connections, not active gameplay bonuses.
- Changing cabinet members costs Political Power. Exact replacement costs and any additional constraints remain pending.
- Proposed simple initial roster: finance/economy, foreign affairs, defense, interior, education, health, and labor/social affairs. This roster is a recommendation, not yet approved.
- Proposed interface: each office shows its current minister, bonuses, and a "Change" action opening candidates with their traits and replacement cost. Candidate eligibility, coalition allocation, portraits, vacancies, and AI appointments remain to be designed.
- Cabinet selection must not silently introduce new legislative confirmation votes or override the agreed simple reform voting model.
- Use country-appropriate office titles where available while retaining common gameplay role identifiers.

## Agreed country navigation layout

- Remove the existing feature-navigation buttons (including planned features such as Research) from their current positions in the country control panel and relocate them to a compact toolbar directly beneath the country flag and country name.
- Replace visible text names on those buttons with generated icons appropriate to each feature. Create the actual icon assets during the authorized UI implementation; none have been generated by this design update.
- Use a consistent icon style with silhouettes and contrast readable at button size. Exact asset style and toolbar order remain to be finalized.
- Recommended usability: retain feature names in hover tooltips and accessible labels, and provide distinct hover, selected, and disabled states. These labels do not reinstate visible text on the toolbar.
- Planned, unimplemented features must not imply working functionality. Recommended handling is a disabled icon with a clear "Planned" tooltip until its system exists.
- Preserve the agreed Cabinet button near the portraits and parliament; this relocation request targets the existing feature-navigation buttons and does not silently move Cabinet away from its agreed position.
- Inspect the latest map-build source to identify all existing buttons before implementing. The attached original 0.1.0 source is not sufficient evidence of the current control-panel layout.
- This is a saved design change, not a claim that the current runnable build has been modified.

## Agreed top-bar indicators and starting finances

- Replace text labels for existing top-bar indicators, including Political Power and stability, with appropriate generated icons in the same coherent UI asset style. Retain visible numerical values.
- Add Treasury and Debt indicators to the top bar, each with a generated icon and its numerical value.
- Recommended tooltips retain indicator names, meanings, and relevant breakdowns. Political Power lists daily modifiers; future finance tooltips can show balance changes and debt details once simulated.
- Use the supplied Millennium Dawn scenario data for starting Treasury and Debt. Inspect the actual initialization scripts, variables, units, and dated history before importing; do not assume a missing declaration means zero or that raw history is a fully initialized game state.
- Preserve separate measures: Treasury is the government's cash balance; Debt is outstanding government borrowing. Do not confuse these with GDP or net them into one displayed value.
- Starting finances must correspond to the 1 January 2000 scenario. Confirm the completeness/version of the MD reference before a production import and report unsupported or missing values as such rather than fabricating precision.
- Translate source money units into one consistent game unit and use readable abbreviated values with the full value and unit in tooltips. Exact display currency/unit remains to be finalized.
- Imported starting values do not imply an implemented economy. Budget flows, taxes, spending, interest, and automatic borrowing remain dependent on the later economic model.
- Icon assets and actual runnable-build changes are deferred to authorized implementation; this update records the plan only.

## Agreed world Ledger

- Add a Ledger button somewhere on the top bar, using the agreed generated-icon style and a hover label. Exact placement remains to be finalized.
- Clicking opens a global country ledger similar in purpose to Millennium Dawn's ledger.
- One row per scenario country, with flag and country name followed by statistics.
- Required columns: population; GDP; GDP per capita; stability; war support; number of States; government outlook; Debt; Treasury.
- Every statistic is sortable through its column header. Recommended behavior: repeated clicks toggle ascending/descending; numeric values sort on their underlying numbers, not formatted strings; outlook sorts by name. Exact default sort remains pending.
- Recommended additions: country search, a fixed country-name column, scrolling for the full roster, and selecting a row to open or focus that country's control panel. These usability additions are proposals, not separately approved requirements.
- GDP per capita is calculated from GDP and population using compatible units and dates. Do not import or calculate it as an unrelated modifier.
- State count means currently owned States, not provinces; government outlook is the governing outlook rather than the population's largest outlook category.
- Treasury and Debt remain separate and use the same units and definitions as the top bar.
- Use live game state for implemented statistics. Import GDP and other starting financial data from MD only after checking its initialization, definitions, units, and scenario date. The request does not establish that usable starting GDP exists for every country.
- If a statistic is unimplemented or its source value is missing, show an explicit unavailable marker with a tooltip; do not fill unknown values with a false zero. Display valid imported starting figures even before economic evolution is implemented, but identify their status.
- Ledger data must refresh as relevant game state changes without rescanning or rebuilding every row every render frame.
- This is a saved feature specification; no ledger has been implemented in the runnable build by this conversation.

## Agreed World Tension globe and popup

- Place a globe button immediately to the right of the timer/date controls.
- Display the current World Tension number on the globe. Use the coherent generated UI-icon style established for the other top-bar controls, with legible number contrast.
- Clicking the globe opens a popup containing current wars and a history of events that raised World Tension.
- Do not add or reconstruct ongoing wars from the starting scenario for now. This defers starting-war data and simulation; it does not establish that there were historically no wars in 2000.
- The current-wars section may initially be empty because war simulation and scenario wars are deferred. Recommended wording: "Starting wars are not modeled yet" rather than implying historical world peace.
- Recommended event entries show date, event description, involved countries, and the tension increase. Exact layout remains to be finalized.
- Entries must correspond to actual recorded game events. Do not fabricate tension events or claim future war mechanics already produce them.
- Initial tension, range/display units, event contributions, decay, and diplomatic effects remain to be designed. The user's request establishes the indicator and popup, not a starting value or tension formula.
- World Tension and its event history should be preserved in saves when implemented.
- This conversation records the planned UI and data foundation; it does not authorize immediate full war-system development.

## Delivery boundary

### Standing save policy

The user starts a new game when testing every version. Do not implement cross-version save compatibility, save migration, legacy-schema support, or backward-compatibility tests unless the user explicitly requests them. This policy applies beyond 0.2 and supersedes any older handoff suggestion to migrate saves. Keep ordinary save/load within each version and preserve that version's implemented state. Clearly reject incompatible older saves instead of silently converting or resetting them.

The five-patch roadmap and suggested small improvements have been approved, subject to this save policy. Approval of the plan does not start implementation before the latest source and map-work handoff are ready.

This conversation authorizes planning and saving the design, not starting implementation. The initial law-category direction and simplified legislative support rules have been accepted. Detailed law settings, numerical effects, party rosters, portraits, starting data, election mechanics, and constitutional reform thresholds remain to be finalized. Preserve this document alongside future source releases and update it when decisions change.
