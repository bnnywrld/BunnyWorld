# Bunny World 0.2.0.27

Year-2000 population and demographics update over **0.2.0.26**. All 1,264 states have complete age, religion and education profiles with sources or disclosed estimates. Population: **6,146,495,066** across 224 countries. Geography and starting ownership are unchanged.

The inline three demographic charts remain. Separate workforce figures replace the Activity pie; participation and unemployment rates save/load independently. See [methods, limitations, sources and test order](documentation/DEMOGRAPHICS_0227.md).

## Apply and run

1. Close the game and Godot. Back up your working .26 project.
2. Extract the .27 changed-files ZIP into that project root, beside project.godot, replacing included files.
3. Run **Prepare_BunnyWorld.bat**. Application, geography and display versions must report **0.2.0.27**.
4. Open with **Godot 4.5.1 Standard**, allow imports to finish, and start a **fresh campaign**.
5. For an EXE, follow [Windows export instructions](documentation/EXPORT_WINDOWS.md). No Windows executable is included.

Data validation passed 15,858 checks; Godot headless passed 11,041 runtime checks, with zero failures. Native Windows visuals/performance remain the user test. This release does not add a jobs or population simulation.

Controls: right-drag rotate; wheel zoom; left click inspect; Space pause; 1–4 speed; Ctrl+F search; F focus; F5/F9 same-version save/load; F11 fullscreen; Escape menu. F5 in the editor starts the project.
