# BunnyWorld current handoff — 0.1.12

Latest source is this project; previous 0.1 archives attached in chats are historical inputs. Godot 4.5.1, GDScript, GL Compatibility. Private standalone Windows 10/11 x64 game, download/extract/run; no HOI4 installation required.

0.1.12 builds on completed 0.1.11 terrain/atmosphere/camera work. It adds sparse representative buildings, eight lightweight close-range landmarks, city/metropolitan province grouping, district/locality coverage names and year-2000 population accounting. City provinces include surrounding countryside. Other provinces share one remaining pool per state. Population figures are historical grid estimates on game geometry, not exact municipal censuses.

All country totals and global total 6,144,737,528 are preserved. State totals are redistributed by actual geographic grid coverage to resolve inherited mismatches. 223 active countries, 1,235 states, 40,031 land provinces, 118 ocean zones and 19 organizations. Save schema 8, scenario bunny_world_2000_0_1_12_r2; new campaign required. Province IDs, territorial rights and economic building counters remain; only local Vatican/Rome coverage changes in this update. North/South Chishima and Karafuto fixes remain.

Rendering: town 2 models; city 4–8; large city 8–16; metropolis 16–24; megacity up to 40 per whole metropolitan group. Hard nearby limits: 384 buildings / 32 clusters. Models appear below camera distance 1.18 and fully fade in by 1.08, in all map modes. No building physics, individual shadows or simulation. Landmarks use original generated code geometry; no model downloads.

Population/skyline growth is explicitly postponed. 0.2 discussion prioritizes demographics (population types and pie charts) and political framework (head of state/government portraits, parliament curve with 100 representative seats at 1% share, next election or never), followed by economy. No economy, armies, war or campaign AI yet. Political-system details are still being discussed in another chat.

Windows build and source are the deliverables. User has not tested 0.1.11 or 0.1.12 yet. Require user play testing for native Windows behavior and actual hardware performance; automated checks are documented in TEST_RESULTS.md. Discuss patch scope before starting subsequent work unless explicitly authorized.

Updated 0.1.12 adds Find place / Ctrl+F, population-scope tooltips, a persistent close-range scenery toggle and other graphics/sound/frame preferences, lower gentle coastal lift, and a Vatican geographic-scale vector override. Colosseum selection resolves to Italy. Country count, province IDs, territorial rights and country population totals remain; local Italian province coverage, borders and population shares are rebuilt. No old-save migration/support should be added unless the user explicitly requests it; the user tests every version from a new campaign.
