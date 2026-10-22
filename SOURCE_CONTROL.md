# Keeping BunnyWorld small

The working version is on clean-globe. Keep game code/data, required assets, geographic build inputs, licenses and current design/development notes. Large packed resources in repository_assets are required: Prepare_BunnyWorld.bat restores the checksum-verified originals. They are not backups.

## Every update

1. Work in the existing checkout; put temporary copies, screenshots, ZIPs and exported games outside it.
2. Replace current assets/data in place. The map packager now verifies all active parts and removes every unreferenced pack after publishing the new manifest.
3. Run `python tools/repository_hygiene.py --prune` after other asset-packaging workflows too.
4. Review and stage additions, changes **and deletions**. Run `python tools/repository_hygiene.py` before committing. GitHub runs the same check on pushes and pull requests.
5. Update current documentation. Delivery-only patch manifests/removal lists and QA output are ignored. Keep important design notes, sources and current validation summaries.

.gdignore files stop Godot importing tool datasets and generating useless CSV translations. .gitignore excludes build/cache/delivery output. Required cartography baselines remain because generators and tests reference them. Do not remove them merely because they have old version numbers.

## Disk space and branches

Branches share Git objects; each branch is not another full game copy. Unmerged branch-only assets can retain space. Removing branches does not erase the old assets still reachable from main's commit history.

Pulling the cleanup removes tracked obsolete packs from the working folder. It does not shrink existing Git history, remove ignored local files, or remove separate backup folders. Godot's .godot import cache is separate and is regenerated when the editor opens.

For the smallest new checkout use:

```
git clone --depth 1 --single-branch --branch clean-globe https://github.com/bnnywrld/BunnyWorld.git
```

Use a clean sibling folder first; preserve any local edits or uncommitted patches before replacing an existing checkout. A shallow clone avoids downloading old asset history. Do not use reset --hard or clean -fdx to recover disk space.

## Cleanup record (18 October 2026)

Removed obsolete asset packs, delivery paperwork, old duplicate handoffs, earlier QA output and Godot-generated CSV translations. Current game code/data and all manifest-referenced assets remain. The recovery/0.2.0.27-demographics branch contained only an unfinished checkpoint note (no unique implementation); main already contains the subsequent .27, .28 and .29 updates. geography-0.2.0.6 is an ancestor of main. Neither branch contains unique game code needed by the current version.

The GitHub connector can update main but cannot delete branch refs. Delete those two remote branches from GitHub's branches page or with `git push origin --delete geography-0.2.0.6 recovery/0.2.0.27-demographics` from an authenticated checkout.
