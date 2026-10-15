# Working baseline: BunnyWorld 0.2.0.7

Use `main`. The 0.2.0.6 geography branch and earlier baselines remain in git history. This update contains source, prepared resources, factual MD budgets, generation tools and validation evidence; it does not include an exported Windows executable.

After pulling with Godot closed, double-click **Prepare_BunnyWorld.bat**, then open the project with Godot 4.5.1 Standard. The command-line equivalent is `python tools/restore_repository_assets.py`.

Large resources are stored as checksum-verified lossless parts under repository_assets, indexed by ASSET_RESTORE.json. Known previous-version hashes allow safe automatic border-resource updates without --force. Unknown custom resource edits stop preparation; preserve those before deliberately using --force. The final geography bundle verifies current project version, runtime data, identity textures and border resources together. Godot's import cache is regenerated locally.

No Git LFS, external asset downloads or Python geographic libraries are needed for normal testing. Python 3's standard library suffices for preparation. Regeneration dependencies are listed in DEVELOPMENT.md. Do not commit EXEs, ZIPs, editor caches or local saves. Offline validation pictures do not need their Godot-generated .png.import metadata tracked.

Fresh campaigns only. Local demographic refinement, physical graphics changes and save migration are outside this patch.
