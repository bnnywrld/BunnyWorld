# Developing BunnyWorld 0.2.0.4

Godot 4.5.1 stable, GL Compatibility. UI-only patch on the complete 0.2.0.3 world baseline. Application version is 0.2.0.4; unchanged world scenario ID remains bunny_world_2000_0_2_0_3, save schema 10. Start fresh across releases; no migration work is authorized.

scripts/main.gd owns the compact header, viewport overlays, tooltip measurement and territory drawer. scripts/foundation_ui.gd owns individual stat boxes and larger national navigation. assets/ui/search.svg is the vector search icon. tests/ui_0204_tests.gd exercises layout, information separation, drawer lifecycle, search and capital thresholds at normal/minimum canvas sizes.

Preserve one resident eight-layer material array, the fixed terrain grid and cached scenery. This patch changes no shaders/geography or camera resource behavior. Regeneration procedures and approximations are preserved in documentation/versions/0_2_0_3/DEVELOPMENT.md.

Build with tools/build_windows.py --godot /path/to/Godot --template /path/to/clean_official_windows_release_x86_64.exe --embed-pck --output /path/to/BunnyWorld_0_2_0_4.exe. Never reuse a previous exported game executable as the template. Validate the exact embedded release using tests/export_pack_version_tests.gd, tools/verify_embedded_0204.py, UI tests and full smoke. Linux loading of the Windows embedded pack does not mean native Windows execution.
