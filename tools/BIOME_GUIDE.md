# BunnyWorld Biome Reference & Editing Guide

The Biome Map (`assets/biome_map.png`) visualizes real-world vegetation, terrain, and climate types across Earth.

## Biome Color Palette Table

| Biome Name | Hex Color | RGB Color | Active Texture Asset | Real-World Geographic Regions |
|:-----------|:---------:|:---------:|:---------------------|:------------------------------|
| **Rice Paddies (East/SE Asia)** | `#5e9e42` | `(94, 158, 66)` | `rice_paddy_detail` |  |
| **Farmland / Cropland** | `#d9b83b` | `(217, 184, 59)` | `farmland_detail` |  |
| **Plains / Grassland** | `#7ec850` | `(126, 200, 80)` | `grassland_detail (new green plains)` |  |
| **Deciduous Forest** | `#2d8033` | `(45, 128, 51)` | `forest (resident_0)` |  |
| **Conifer Forest / Taiga** | `#155436` | `(21, 84, 54)` | `conifer_detail` |  |
| **Tropical Rainforest** | `#009e5c` | `(0, 158, 92)` | `rainforest_detail` |  |
| **Swamp & Wetlands** | `#2c6e61` | `(44, 110, 97)` | `swamp_detail` |  |
| **Desert / Arid Sand** | `#e6bd73` | `(230, 189, 115)` | `desert (resident_3)` |  |
| **Savanna & Shrubland** | `#bda852` | `(189, 168, 82)` | `savanna_detail` |  |
| **Mediterranean / Chaparral** | `#87964b` | `(135, 150, 75)` | `chaparral / mediterranean` |  |
| **Mountain Rock** | `#6e737a` | `(110, 115, 122)` | `rock_detail` |  |
| **Tundra / Permafrost** | `#8fa89b` | `(143, 168, 155)` | `tundra_detail` |  |
| **Snow & Ice** | `#eaf2f8` | `(234, 242, 248)` | `snow (resident_6)` |  |
| **Water / Oceans** | `#0f2a4a` | `(15, 42, 74)` | Ocean / Lake water | Global oceans, seas, and inland lakes |

## How to Edit Biomes Manually

1. Open `assets/biome_map.png` in any image editor (Photoshop, GIMP, Paint.NET, Aseprite, etc.).
2. Use the **Eyedropper tool** to pick any biome color from the palette table above, or enter the exact Hex/RGB values.
3. Paint with the **Pencil / Brush tool** over any area you wish to adjust (e.g. painting rice paddies, adding farmland, expanding forests, painting wetlands).
4. Save `assets/biome_map.png`.
5. Run the importer in your terminal:
```bash
python tools/import_biome_map.py
```
The importer will automatically match your colors, recalculate seamless boundary transitions, and update `assets/terrain_types.png` for the game engine!
