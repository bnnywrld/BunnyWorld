"""Export and compile visual, inspectable Biome Map (assets/biome_map.png)
and runtime multi-biome data (assets/terrain_types.png).

Each pixel in assets/biome_map.png is rendered in a distinct, intuitive RGB color
representing authentic real-world biomes across Earth. The user can view this image
or edit it in any graphics program and re-import with tools/import_biome_map.py.
"""
from pathlib import Path
import re, json
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
CART = ROOT / 'tools/cartography'
ASSETS = ROOT / 'assets'
W, H = 6144, 3072

# Complete 12 distinct visual biomes for the editable map
BIOME_VISUALS = [
    {"id": "rice_paddy", "cat": 2, "name": "Rice Paddies (East/SE Asia)", "rgb": (94, 158, 66),   "hex": "#5e9e42", "texture": "rice_paddy_detail"},
    {"id": "farmland",   "cat": 2, "name": "Farmland / Cropland",        "rgb": (217, 184, 59),  "hex": "#d9b83b", "texture": "farmland_detail"},
    {"id": "plains",     "cat": 4, "name": "Plains / Grassland",         "rgb": (126, 200, 80),  "hex": "#7ec850", "texture": "grassland_detail (new green plains)"},
    {"id": "forest",     "cat": 0, "name": "Deciduous Forest",          "rgb": (45, 128, 51),   "hex": "#2d8033", "texture": "forest (resident_0)"},
    {"id": "taiga",      "cat": 0, "name": "Conifer Forest / Taiga",    "rgb": (21, 84, 54),    "hex": "#155436", "texture": "conifer_detail"},
    {"id": "rainforest", "cat": 7, "name": "Tropical Rainforest",       "rgb": (0, 158, 92),    "hex": "#009e5c", "texture": "rainforest_detail"},
    {"id": "swamp",      "cat": 7, "name": "Swamp & Wetlands",          "rgb": (44, 110, 97),   "hex": "#2c6e61", "texture": "swamp_detail"},
    {"id": "desert",     "cat": 3, "name": "Desert / Arid Sand",        "rgb": (230, 189, 115), "hex": "#e6bd73", "texture": "desert (resident_3)"},
    {"id": "savanna",    "cat": 4, "name": "Savanna & Shrubland",       "rgb": (189, 168, 82),  "hex": "#bda852", "texture": "savanna_detail"},
    {"id": "chaparral",  "cat": 4, "name": "Mediterranean / Chaparral", "rgb": (135, 150, 75),  "hex": "#87964b", "texture": "chaparral / mediterranean"},
    {"id": "rock",       "cat": 5, "name": "Mountain Rock",             "rgb": (110, 115, 122), "hex": "#6e737a", "texture": "rock_detail"},
    {"id": "tundra",     "cat": 4, "name": "Tundra / Permafrost",       "rgb": (143, 168, 155), "hex": "#8fa89b", "texture": "tundra_detail"},
    {"id": "snow",       "cat": 6, "name": "Snow & Ice",                "rgb": (234, 242, 248), "hex": "#eaf2f8", "texture": "snow (resident_6)"},
]
WATER_COLOR = (15, 42, 74) # Deep ocean navy

def main():
    print(f"Building high-definition Biome Map ({W}x{H})...")
    
    # 1. Parse ESA Legend
    legend_text = (CART / 'landcover_0201_legend.js').read_text()
    entries = []
    for line in legend_text.splitlines():
        if line.strip().startswith('//'): continue
        m = re.match(r"\s*\['(\d+)',.*?'([0-9A-F]{6})', '([0-9A-F]{6})', '([0-9A-F]{6})'", line)
        if m:
            val = int(m[1])
            for col in m.groups()[1:]:
                entries.append((tuple(bytes.fromhex(col)), val))
    
    # 2. Load ESA raw classification image
    raw_img = Image.open(CART / 'landcover_2000_0201.png').convert('RGB')
    if raw_img.size != (W, H):
        raw_img = raw_img.resize((W, H), Image.Resampling.NEAREST)
    raw = np.asarray(raw_img)
    
    unique, inv = np.unique(raw.reshape(-1, 3), axis=0, return_inverse=True)
    colors = np.array([e[0] for e in entries], float)
    values = np.array([e[1] for e in entries])
    _, ix = cKDTree(colors).query(unique.astype(float))
    codes = values[ix][inv].reshape((H, W)).astype(np.uint8)
    
    # 3. Load elevation (etopo)
    etopo = np.load(CART / 'etopo_021.npz')['meters']
    etopo_img = Image.fromarray(etopo)
    if etopo_img.size != (W, H):
        etopo_img = etopo_img.resize((W, H), Image.Resampling.BILINEAR)
    elev = np.asarray(etopo_img)
    
    # 4. Load gameplay land mask from province_ids.png
    prov_img = Image.open(ASSETS / 'province_ids.png')
    prov_arr = np.array(prov_img)
    if prov_arr.ndim == 3:
        pid = prov_arr[:, :, 0].astype(np.uint32) + prov_arr[:, :, 1].astype(np.uint32) * 256
    else:
        pid = prov_arr.astype(np.uint32)
    land = (pid > 0)
    
    # Fill missing land pixels (where ESA resolution called it 210/water or 0/no-data)
    # with nearest terrestrial land code
    valid_terrestrial = land & ~np.isin(codes, [0, 210])
    if np.any(land & ~valid_terrestrial):
        print("Filling coastline/delta land pixels with nearest terrestrial classification...")
        _, nearest_idx = distance_transform_edt(~valid_terrestrial, return_indices=True)
        codes = codes[nearest_idx[0], nearest_idx[1]]
    
    # Coordinate grids: lat from +90 to -90, lon from -180 to +180
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    lats = 90.0 - (y_coords + 0.5) / H * 180.0
    lons = (x_coords + 0.5) / W * 360.0 - 180.0
    abs_lats = np.abs(lats)
    
    # 5. Classify every land pixel into a distinct visual biome
    vis_map = np.full((H, W), "plains", dtype=object)
    # Shader category array: 0 to 7
    categories = np.full((H, W), 4, dtype=np.uint8) # default category 4 (Plains)
    
    # Farmland / Cropland (Code 10, 11, 12, 30, 40)
    farm_mask = np.isin(codes, [10, 11, 12, 30, 40])
    
    # East & Southeast Asia: China, Japan, Korea, Vietnam, Thailand, Taiwan, Philippines
    # Lons ~68E to 142E, Lats -10S to 46N
    is_asia = (lons >= 68.0) & (lons <= 142.0) & (lats >= -10.0) & (lats <= 46.0)
    rice_mask = (farm_mask & is_asia) | ((codes == 20) & is_asia)
    euro_farm_mask = farm_mask & ~rice_mask
    
    vis_map[rice_mask] = "rice_paddy"
    categories[rice_mask] = 2
    
    vis_map[euro_farm_mask] = "farmland"
    categories[euro_farm_mask] = 2
    
    # Forest / Woodland (Code 60, 61, 62, 90, 100)
    forest_mask = np.isin(codes, [60, 61, 62, 90, 100])
    vis_map[forest_mask] = "forest"
    categories[forest_mask] = 0
    
    # Conifer Forest / Boreal Taiga (Code 70, 71, 72, 80, 81, 82)
    conifer_mask = np.isin(codes, [70, 71, 72, 80, 81, 82])
    # Also northern boreal belt (lat > 56N) and high mountain slopes
    boreal_taiga = (lats >= 56.0) & (forest_mask | (codes == 130)) & (elev < 1200.0)
    mountain_pine = forest_mask & (elev >= 700.0) & (abs_lats >= 25.0)
    conifer_all = conifer_mask | boreal_taiga | mountain_pine
    vis_map[conifer_all] = "taiga"
    categories[conifer_all] = 0
    
    # Tropical Rainforest (Code 50: broadleaved evergreen, or equatorial broadleaf)
    rainforest_mask = (codes == 50) | (np.isin(codes, [60, 61, 62]) & (abs_lats <= 18.0) & (elev < 1000.0))
    vis_map[rainforest_mask] = "rainforest"
    categories[rainforest_mask] = 7
    
    # Swamp & Wetlands (Code 160, 170, 180 + Everglades, Pantanal, Pripet)
    wetlands_mask = np.isin(codes, [160, 170, 180])
    is_everglades = (lons >= -82.0) & (lons <= -80.0) & (lats >= 24.5) & (lats <= 27.5)
    is_pantanal = (lons >= -59.0) & (lons <= -55.0) & (lats >= -22.0) & (lats <= -16.0)
    is_pripet = (lons >= 25.0) & (lons <= 30.0) & (lats >= 51.0) & (lats <= 53.0)
    wetlands_mask |= (is_everglades | is_pantanal | is_pripet)
    vis_map[wetlands_mask] = "swamp"
    categories[wetlands_mask] = 7

    # Mediterranean / Chaparral Zones
    is_med_basin = (lons >= -10.0) & (lons <= 42.0) & (lats >= 28.0) & (lats <= 46.0)
    is_california = (lons >= -125.0) & (lons <= -115.0) & (lats >= 31.0) & (lats <= 41.0)
    is_chile_med = (lons >= -75.0) & (lons <= -70.0) & (lats >= -38.0) & (lats <= -30.0)
    is_cape_med = (lons >= 17.0) & (lons <= 26.0) & (lats >= -35.0) & (lats <= -31.0)
    is_aus_med = ((lons >= 114.0) & (lons <= 122.0) & (lats >= -36.0) & (lats <= -30.0)) | \
                 ((lons >= 135.0) & (lons <= 148.0) & (lats >= -39.0) & (lats <= -34.0))
    is_med_zone = is_med_basin | is_california | is_chile_med | is_cape_med | is_aus_med
    chaparral_mask = np.isin(codes, [120, 121, 122]) & is_med_zone
    vis_map[chaparral_mask] = "chaparral"
    categories[chaparral_mask] = 4

    # Desert / Arid Sand / Badlands:
    # 1. American Southwest & Northern Mexico (Mojave, Sonoran, Chihuahuan, Great Basin, Baja):
    is_sw_desert = (lons >= -122.0) & (lons <= -99.5) & (lats >= 23.0) & (lats <= 44.0) & \
                   np.isin(codes, [120, 121, 122, 130, 150, 151, 152, 153, 190, 200, 202]) & \
                   (elev < 2400.0) & ~farm_mask & ~forest_mask & ~conifer_all & ~is_california

    # 2. Australian Outback & Desert Interior (Great Victoria, Simpson, Tanami, Gibson):
    is_aus_outback = (lons >= 114.0) & (lons <= 146.0) & (lats >= -36.0) & (lats <= -17.0) & \
                     np.isin(codes, [120, 121, 122, 130, 150, 151, 152, 153, 190, 200, 202]) & \
                     ~farm_mask & ~forest_mask & ~conifer_all & ~is_aus_med

    # 3. Sahara, Arabian Peninsula, Middle East, Central Asian Deserts (Gobi, Taklamakan, Karakum, Kyzylkum, Iranian plateau):
    is_mideast_sahara = (lons >= -18.0) & (lons <= 70.0) & (lats >= 10.0) & (lats <= 38.0) & \
                        np.isin(codes, [120, 121, 122, 130, 150, 151, 152, 153, 190, 200, 202]) & \
                        (elev < 2500.0) & ~farm_mask & ~forest_mask & ~conifer_all & ~is_med_basin

    is_central_asia = (lons >= 50.0) & (lons <= 112.0) & (lats >= 35.0) & (lats <= 48.0) & \
                      np.isin(codes, [120, 122, 130, 150, 151, 152, 153, 190, 200, 202]) & \
                      (elev < 2200.0) & ~farm_mask & ~forest_mask & ~conifer_all

    # 4. Atacama, Patagonian Steppe, Kalahari, Namib:
    is_atacama = (lons >= -73.0) & (lons <= -67.0) & (lats >= -28.0) & (lats <= -18.0) & (elev < 3200.0) & ~farm_mask
    is_kalahari = (lons >= 11.0) & (lons <= 28.0) & (lats >= -30.0) & (lats <= -18.0) & \
                  np.isin(codes, [120, 122, 150, 151, 152, 153, 190, 200, 202]) & ~farm_mask

    # 5. Global bare ground:
    bare_ground = np.isin(codes, [200, 202]) & (elev < 2200.0)

    desert_mask = is_sw_desert | is_aus_outback | is_mideast_sahara | is_central_asia | is_atacama | is_kalahari | bare_ground
    vis_map[desert_mask] = "desert"
    categories[desert_mask] = 3

    # Savanna (Code 150, 151, 152, 153 in warm latitudes outside desert)
    savanna_mask = np.isin(codes, [120, 150, 151, 152, 153]) & (abs_lats <= 32.0) & (elev < 1800.0) & ~desert_mask
    vis_map[savanna_mask] = "savanna"
    categories[savanna_mask] = 4
    
    # Mountain Rock (Code 201 + high steep rocky peaks > 2000m in temperate, > 3200m in tropics)
    rock_mask = (codes == 201) | ((elev >= 2200.0) & (abs_lats >= 25.0)) | (elev >= 3500.0)
    vis_map[rock_mask] = "rock"
    categories[rock_mask] = 5
    
    # Tundra / Permafrost (Code 140 + high northern subpolar latitudes > 62N with low vegetation)
    tundra_mask = (codes == 140) | ((lats >= 63.0) & np.isin(codes, [120, 130, 150, 152, 153]))
    vis_map[tundra_mask] = "tundra"
    categories[tundra_mask] = 4
    
    # Snow & Ice (Code 220 + extreme polar elevations / Greenland / Antarctica)
    snow_mask = (codes == 220) | (elev >= 5200.0) | ((lats >= 72.0) & (codes == 0))
    vis_map[snow_mask] = "snow"
    categories[snow_mask] = 6
    
    # 6. Render the Visual Biome Map (assets/biome_map.png)
    print("Rendering visual biome map with intuitive colors...")
    vis_rgb = np.zeros((H, W, 3), dtype=np.uint8)
    
    for b in BIOME_VISUALS:
        mask = (vis_map == b['id']) & land
        vis_rgb[mask] = b['rgb']
        count = np.count_nonzero(mask)
        print(f"  {b['name']:<32}: {count:>8} pixels ({count / np.count_nonzero(land) * 100:5.2f}%)")
    
    vis_rgb[~land] = WATER_COLOR
    vis_img = Image.fromarray(vis_rgb, mode='RGB')
    vis_img.save(ASSETS / 'biome_map.png', optimize=True)
    print("SAVED: assets/biome_map.png")
    
    # 7. Compile Smooth Transition Data for the Shader (assets/terrain_types.png)
    print("Compiling smooth multi-biome transitions for shader (8 categories)...")
    p1 = categories.copy()
    p2 = categories.copy()
    v1 = np.zeros((H, W), dtype=np.float32)
    v2 = np.zeros((H, W), dtype=np.float32)
    
    for cat in range(8):
        weight = gaussian_filter((categories == cat).astype(np.float32), 1.2, mode=('nearest', 'wrap'))
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
    
    # 8. Export Guide Documentation
    guide = ["# BunnyWorld Biome Reference & Editing Guide\n"]
    guide.append("The Biome Map (`assets/biome_map.png`) visualizes real-world vegetation, terrain, and climate types across Earth.\n")
    guide.append("## Biome Color Palette Table\n")
    guide.append("| Biome Name | Hex Color | RGB Color | Active Texture Asset | Real-World Geographic Regions |")
    guide.append("|:-----------|:---------:|:---------:|:---------------------|:------------------------------|")
    for b in BIOME_VISUALS:
        r, g, bl = b['rgb']
        guide.append(f"| **{b['name']}** | `{b['hex']}` | `({r}, {g}, {bl})` | `{b['texture']}` | {b.get('description', '')} |")
    guide.append(f"| **Water / Oceans** | `#0f2a4a` | `({WATER_COLOR[0]}, {WATER_COLOR[1]}, {WATER_COLOR[2]})` | Ocean / Lake water | Global oceans, seas, and inland lakes |\n")
    
    guide.append("## How to Edit Biomes Manually\n")
    guide.append("1. Open `assets/biome_map.png` in any image editor (Photoshop, GIMP, Paint.NET, Aseprite, etc.).")
    guide.append("2. Use the **Eyedropper tool** to pick any biome color from the palette table above, or enter the exact Hex/RGB values.")
    guide.append("3. Paint with the **Pencil / Brush tool** over any area you wish to adjust (e.g. painting rice paddies, adding farmland, expanding forests, painting wetlands).")
    guide.append("4. Save `assets/biome_map.png`.")
    guide.append("5. Run the importer in your terminal:\n```bash\npython tools/import_biome_map.py\n```")
    guide.append("The importer will automatically match your colors, recalculate seamless boundary transitions, and update `assets/terrain_types.png` for the game engine!\n")
    
    (ROOT / 'tools/BIOME_GUIDE.md').write_text("\n".join(guide), encoding='utf-8')
    print("SAVED: tools/BIOME_GUIDE.md")
    print("BIOMES_SUCCESSFULLY_EXPORTED")

if __name__ == '__main__':
    main()
