# BunnyWorld 0.2.0.27 — year-2000 demographics

All 1,264 states have population and complete age, religion and education profiles. The 224 country populations sum to **6,146,495,066**, compared with 6,144,737,528 in .26. This is a historical scenario estimate for the game's existing footprints, not a claim of census precision for every state.

## Population

GHS-POP R2023A's 2000 population raster was freshly registered to the current province images. Source cell centres determine membership; coastal mismatches within 8 km snap to existing coastal land. The compact province aggregate, registration hashes and source archive checksum are included. About 842,419 source inhabitants could not be mapped; 18,780,233 were assigned by coastal snapping. No old numeric-ID population cache was reused.

The 50 US states, DC and Puerto Rico use April 1, 2000 census anchors. Nine selected small-country/territory groups use World Bank 2000 benchmarks, including the combined FSM/Palau Micronesia state. Remaining populations use the current-footprint grid sums. Different sources represent dates within 2000 rather than a uniform January 1 count. A military-base or island name does not imply an empty footprint: inhabitants of larger game footprints are retained. Truly uninhabited areas retain complete profile shares but display no resident counts.

## Age and education

National 2000 age distributions provide the baseline, with disclosed peer profiles when absent. Regional estimates use settlement concentration, capitals and explicit regional context; no random state-ID variation is used. Population-weighted state age shares reconcile to national baselines. The single-year profile supports the game's under-18, working-age and retired groups. Retirement starts at the current owner's policy threshold; this is not a reconstruction of every historical retirement law.

Education measures adults aged 25+, using Barro-Lee 2000 completed attainment when available, then disclosed nearby-year WDI/UNESCO or peer estimates. The four exclusive categories are below primary, primary, secondary and tertiary. Incomplete primary/secondary/tertiary study is assigned to the highest completed level. Adult-weighted regional estimates reconcile to national targets. Urban and rural differences are modeled, not individually measured regional censuses.

## Religion

There are **210 explicit regional religion estimates**. Remaining states use complete historical national or controller proxies, documented in each profile. Religion is not inferred from income, density or a random seed. Regional estimates incorporate known broad patterns such as India's state differences, Syrian communities, northern/southern Nigeria, and overseas territories. Labels are canonicalized to avoid duplicate Christian categories; shares are mutually exclusive and total 100%. Some states appropriately share a national profile where reliable local distinctions are unavailable. These are educated historical estimates, not exact local census transcriptions.

## Workforce and interface

The inline Age, Religion and Education charts remain. The Activity pie is removed. Separate state and country figures show participation, labour force, employed, unemployed and people outside the labour force. Unemployment divides unemployed by labour force. Participation divides labour force by the game's working-age population (18 to the retirement threshold). Historical national participation benchmarks generally cover 15+ and are adapted to this game definition; regional rates are estimates. Missing national benchmarks use explicitly disclosed defaults.

Counts are rounded consistently: employed + unemployed = labour force; labour force + outside labour force = working-age population. Country rates use summed numerators and denominators. State participation and unemployment rates persist independently in same-version saves. Owner transfers retain the state's demographic profile, while retirement grouping follows the new owner's policy. Invalid saved rates are rejected before committing the load.

No job allocation, births, deaths, aging or migration simulation is introduced. GDP totals change through the existing population × GDP-per-person calculation; GDP per person and fiscal/building values were not re-researched.

## Geography and validation

Province images, province records, state membership and starting ownership are unchanged from .26. All approved mergers and exclusions remain. Population changes affect population-based map display and city estimates; renderer geometry is reused. The shared build now refreshes data-version metadata without rebuilding identical mesh resources.

- Data validator: **15,858 checks, zero failures**; all profiles complete, all 224 country sums verified.
- Godot 4.5.1 headless: **11,041 checks, zero failures**; full startup, inline charts, workforce identities, country aggregation, owner transfers, retirement changes, save/load and invalid-save rejection.
- Headless checks cannot certify native Windows appearance or hardware GPU performance. This patch makes no FPS improvement claim.

## Apply and test

Apply this changed-files ZIP over **0.2.0.26 only**, beside project.godot. Run Prepare_BunnyWorld.bat, open with Godot 4.5.1 Standard, and start a **fresh campaign**. Earlier saves are unsupported. This is a source patch, not an EXE.

1. Compare Delhi/Bihar and Beijing/Tibet populations and their three inline charts. Inspect Syrian and Nigerian regional religion differences and Mayotte.
2. Check separate workforce figures at state and country level. Hover values for full counts and source/method notes.
3. Change a state owner with the existing console, then save/load with F5/F9. The state profile should remain while the country totals update. Confirm game/build bundles show .27.

## Sources and reproducibility

- [EC JRC GHS-POP R2023A](https://human-settlement.emergency.copernicus.eu/ghs_pop2023.php), DOI [10.2905/2FF68A52-5B5B-4A22-8F40-C41DA8332CFE](https://doi.org/10.2905/2FF68A52-5B5B-4A22-8F40-C41DA8332CFE).
- [US Census 2000 resident-population tables](https://www.census.gov/data/tables/2000/dec/2000-resident-population.html).
- [Barro-Lee attainment data](https://barrolee.github.io/BarroLeeDataSet/Data.html), Barro and Lee (2013), Journal of Development Economics 104, 184–198.
- [World Bank API](https://api.worldbank.org/v2/) and the project's cached WDI/UN/ILO/UNESCO series. Benchmark years are retained separately from modeled year 2000.
- [CIA World Factbook 2000 archive](https://www.gutenberg.org/ebooks/3672), national religion context.
- Regional context: [India 2001 religion census](https://censusindia.gov.in/nada/index.php/catalog/21462), [China 2000 census](https://www.stats.gov.cn/english/NewsEvents/200204/t20020423_25983.html), [ONS religion history](https://www.ons.gov.uk/peoplepopulationandcommunity/culturalidentity/religion/articles/howreligionhaschangedinenglandandwales/2015-06-04), [Pew historical Russian religion](https://www.pewresearch.org/religion/2014/02/10/russians-return-to-religion-but-not-to-church/). These inform regional judgments; they do not directly substantiate every modeled percentage.

`data/state_demographics.json` records per-state sources and estimate status. `data/demographics_0227_report.json` contains all country changes and benchmark metadata. Generation/curation tools, compact grid aggregates and small source files are included. The original multi-gigabyte raster is excluded; the fetch and aggregation scripts record how to reproduce it. Rebuilding demographic inputs requires a clean .26 world/demographics baseline, not the already-updated .27 world.
