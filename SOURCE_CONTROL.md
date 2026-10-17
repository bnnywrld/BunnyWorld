# BunnyWorld .28 source update

Apply the .28 changed-files patch over a confirmed .27 project, then test a fresh campaign before promoting it as your working baseline. This source patch does not by itself update GitHub main.

Close Godot before replacing/pulling files. Run Prepare_BunnyWorld.bat and allow editor imports to finish before testing or exporting. Prepared meshes are stored as lossless checksum-verified parts under repository_assets; do not substitute old border files or atlas caches. Previous official hashes allow automatic restoration of updated prepared assets, while unknown custom changes remain protected.

Do not commit ZIPs, EXEs, .godot caches or local saves. The current offline workflow and geographic dependencies are in DEVELOPMENT.md. Windows testing needs only Godot 4.5.1 Standard and the prepared source project, not the geographic Python dependencies.
