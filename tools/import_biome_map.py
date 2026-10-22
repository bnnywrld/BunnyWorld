"""Import user edits from assets/biome_map.png into assets/terrain_types.png.

Matches each pixel's RGB color to the closest biome in the palette,
maps to the standard categories (0 to 7), computes smooth Gaussian blending
between adjacent families, and saves assets/terrain_types.png.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
W, H = 6144, 3072

BIOME_PALETTE = [
    {"id": "rice_paddy", "cat": 2, "name": "Rice Paddies (East/SE Asia)", "rgb": (94, 158, 66)},
    {"id": "farmland",   "cat": 2, "name": "Farmland / Cropland",        "rgb": (217, 184, 59)},
    {"id": "plains",     "cat": 4, "name": "Plains / Grassland",         "rgb": (126, 200, 80)},
    {"id": "forest",     "cat": 0, "name": "Deciduous Forest",          "rgb": (45, 128, 51)},
    {"id": "taiga",      "cat": 0, "name": "Conifer Forest / Taiga",    "rgb": (21, 84, 54)},
    {"id": "rainforest", "cat": 7, "name": "Tropical Rainforest",       "rgb": (0, 158, 92)},
    {"id": "swamp",      "cat": 7, "name": "Swamp & Wetlands",          "rgb": (44, 110, 97)},
    {"id": "desert",     "cat": 3, "name": "Desert / Arid Sand",        "rgb": (230, 189, 115)},
    {"id": "savanna",    "cat": 4, "name": "Savanna & Shrubland",       "rgb": (189, 168, 82)},
    {"id": "chaparral",  "cat": 4, "name": "Mediterranean / Chaparral", "rgb": (135, 150, 75)},
    {"id": "rock",       "cat": 5, "name": "Mountain Rock",             "rgb": (110, 115, 122)},
    {"id": "tundra",     "cat": 4, "name": "Tundra / Permafrost",       "rgb": (143, 168, 155)},
    {"id": "snow",       "cat": 6, "name": "Snow & Ice",                "rgb": (234, 242, 248)},
]
WATER_COLOR = (15, 42, 74)

def main():
    print("Reading user-edited Biome Map: assets/biome_map.png...")
    biome_map_path = ASSETS / 'biome_map.png'
    if not biome_map_path.exists():
        print(f"ERROR: {biome_map_path} not found!")
        return
        
    img = Image.open(biome_map_path).convert('RGB')
    if img.size != (W, H):
        print(f"Resizing input image from {img.size} to ({W}, {H})...")
        img = img.resize((W, H), Image.Resampling.NEAREST)
    arr = np.asarray(img)
    
    # KD-Tree for nearest color matching
    palette_rgbs = [b['rgb'] for b in BIOME_PALETTE]
    palette_cats = [b['cat'] for b in BIOME_PALETTE]
    
    # Include water color as 255
    palette_rgbs.append(WATER_COLOR)
    palette_cats.append(255)
    
    tree = cKDTree(np.array(palette_rgbs, dtype=float))
    
    unique_colors, inv = np.unique(arr.reshape(-1, 3), axis=0, return_inverse=True)
    _, match_idx = tree.query(unique_colors.astype(float))
    matched_cats = np.array(palette_cats)[match_idx]
    grid_cats = matched_cats[inv].reshape((H, W)).astype(np.uint8)
    
    # Land mask from province_ids.png
    prov_img = Image.open(ASSETS / 'province_ids.png')
    prov_arr = np.array(prov_img)
    if prov_arr.ndim == 3:
        pid = prov_arr[:, :, 0].astype(np.uint32) + prov_arr[:, :, 1].astype(np.uint32) * 256
    else:
        pid = prov_arr.astype(np.uint32)
    land = (pid > 0)
    
    # Any land pixel mistakenly classified as water (255) defaults to plains (4)
    grid_cats[land & (grid_cats == 255)] = 4
    grid_cats[~land] = 4
    
    print("Compiling smooth multi-biome transition data (assets/terrain_types.png)...")
    p1 = grid_cats.copy()
    p2 = grid_cats.copy()
    v1 = np.zeros((H, W), dtype=np.float32)
    v2 = np.zeros((H, W), dtype=np.float32)
    
    for cat in range(8):
        weight = gaussian_filter((grid_cats == cat).astype(np.float32), 1.2, mode=('nearest', 'wrap'))
        best = weight > v1
        p2[best] = p1[best]
        v2[best] = v1[best]
        p1[best] = cat
        v1[best] = weight[best]
        second = (~best) & (weight > v2)
        p2[second] = cat
        v2[second] = weight[second]
        
    fraction = v2 / np.maximum(v1 + v2, 1e-6)
    types_arr = np.stack([p1, p2, np.rint(fraction * 255.0).astype(np.uint8)], axis=-1)
    types_img = Image.fromarray(types_arr, mode='RGB')
    types_img.save(ASSETS / 'terrain_types.png', optimize=True)
    print("SAVED: assets/terrain_types.png")
    print("IMPORT_BIOMES_SUCCESSFUL")

if __name__ == '__main__':
    main()
