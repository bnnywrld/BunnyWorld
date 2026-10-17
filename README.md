# Bunny World 0.2.0.26

State detail patch over the confirmed **0.2.0.25** project / GitHub main at `aeacb59`.
Adds 29 meaningful states using existing whole provinces in China, Syria, India,
Morocco, Pakistan and Colombia. **224 countries, 1,264 states, 13,308 land provinces.**
Taiwan, Afghanistan, the Philippines and all other explicit exclusions stay unchanged.
Previously approved island and territory mergers remain.

See the [complete state changes, member provinces and test checklist](documentation/state_audit_0226/STATE_CHANGES.md)
and [all-country count comparison](documentation/state_audit_0226/COUNTRY_COUNTS.md).

## Apply and run

1. Close Godot and the game. Keep a copy of your working 0.2.0.25 project.
2. Extract the changed-files patch into that project root, beside `project.godot`, replacing included files.
3. Run **Prepare_BunnyWorld.bat**. Application, geography and display bundles must all report **0.2.0.26**.
4. Open `project.godot` with **Godot 4.5.1 Standard**, let imports finish and press F5.
5. Start a **fresh campaign**. Earlier scenario saves are not compatible with this geography.
6. For a Windows release build, follow [EXE export instructions](documentation/EXPORT_WINDOWS.md).

This patch contains source and prepared resource parts, not a Windows executable.
Obsolete compressed parts listed in PATCH_REMOVED_FILES_0226.txt may be removed;
keeping those unreferenced parts does not affect play. Do not delete unrelated files.

## What is preserved

The four canonical province images are byte-identical to .25, including Antarctica.
No province was added, cut or deleted, and no starting province owner changed.
Every country retains its exact population, buildings and building-slot total.
The shared map pipeline refreshes membership, adjacency, borders and prepared resources.

Population subdivision shares are explicitly modeled from existing settlement ranks
and rural land area; they are not regional census counts. State-specific demographic
refinement remains a separate task. This patch leaves rendering and simulation code unchanged.

## Validation

The .26 data validator passed **65,301 checks**. Godot 4.5.1 headless passed **330 runtime checks**
for membership, state browsing, hover highlight, inline demographics and an offscreen owner transfer.
Prepared resources and the map build contract verify. Headless ownership checks inspect the
texture upload buffer, not hardware GPU readback. Native Windows graphics/performance were not tested here.

Your short test: inspect a new state in each target country, hover it in the state browser,
check its capital and inline chart, then try an owner transfer. Briefly check Taiwan,
Afghanistan, Micronesia, Papua New Guinea and Antarctica.

Controls: right-drag rotate; wheel zoom; left click inspect; Space pause; 1–4 speed;
Ctrl+F search; F focus; F5/F9 same-version save/load; F11 fullscreen; Escape menu.
F5 in the **editor** starts the project.

Earlier release history: [archived .25 README](documentation/versions/README_main_0225.md),
[.25 patch](documentation/PATCH_0225.md), [.25 MD audit](documentation/state_audit_0225/AUDIT.md).
