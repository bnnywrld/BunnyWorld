# BunnyWorld 0.2.0.20 verification

All 55 State requests are covered. The 0.2.0.19 geography passes 17 structural/spatial checks, prepared resource restoration, runtime loading, and ownership/save-load checks. Its land coverage and global population are preserved.

The performance patch leaves the geography data and province PNGs byte-identical to 0.2.0.19. Five production-renderer camera views show 22.8–61.0% lower median frame times on Linux software rendering, with the same visible boundaries/highlights. Close-view submitted primitives fall by 61.7%.

23 full-application runtime checks pass, including ownership transfer/restoration, physical edges, membership updates, camera uploads, country-name stability and sea selection. Prepared asset/map-contract tests pass.

See validation_0220/comparison.json and runtime_results.json. Native Windows/NVIDIA 940MX performance is not measured here.
