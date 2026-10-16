# Bunny World 0.2.0.16

Apply over 0.2.0.15 by extracting into the project root and replacing existing files. Close Godot and the game before extracting. Run Prepare_BunnyWorld.bat to verify the bundle, reopen the project and start a fresh campaign.

- North Sumatra: clearer whole-State coverage, less dominant province tint, and internal province lines stay visible farther out for the selected State. Both border meshes are shipped as directly loadable compressed Godot resources, removing the restoration dependency for these files. All 17 provinces and every internal adjacency are checked.
- Cyprus: former UN buffer State and province dissolved into Cyprus State 253 / province 3096. Existing country controllers on the island are retained. Nicosia is the State capital. Population totals are conserved.
- Country colour and selection: categorical ownership remains exact for picking. Visual coverage reconstructs a smooth country transition using neighbouring owner samples; country tint, selection and hover share it. A half-cell alignment correction brings border geometry and selection fields to the actual atlas cell centres. No per-camera geography work or new large textures.
- Country breadcrumb: opens an alphabetical list of owned States in the right inspector. Clicking a State restores its overview. The left panel remains as it was. Only the country list scrolls; the State overview stays unscrolled.

Province redesign remains a separate patch. Proposed next step: update State population inputs, then use population together with area and settlements to guide density. Keep the global province increase at most 20%, and round unnecessary internal corners through shared boundaries while preserving actual coast/State/country corners.

Test checklist: select northern and southern North Sumatra provinces; inspect the entire State; zoom in on southern internal lines. Click Cyprus and the former buffer; both should resolve to Cyprus / Province 1. Inspect a country border in Physical Earth and Political modes. Click a country breadcrumb, scroll a large country list, select a State, and verify the left panel stays unchanged. Keep country names enabled during camera travel.
