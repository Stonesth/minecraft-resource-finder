#!/usr/bin/env python3
"""
Débogue ce qui se trouve à une position spécifique
"""

from src.modern_region_reader import ModernRegionReader
import math

# Position à vérifier
TEST_X = -72
TEST_Y = 24
TEST_Z = 5

print(f"🔍 Analyse de la position X={TEST_X}, Y={TEST_Y}, Z={TEST_Z}\n")

chunk_x = TEST_X // 16
chunk_z = TEST_Z // 16
section_y = TEST_Y // 16
local_x = TEST_X - (chunk_x * 16)
local_y = TEST_Y - (section_y * 16)
local_z = TEST_Z - (chunk_z * 16)

print(f"📦 Chunk: ({chunk_x}, {chunk_z}), Section: Y={section_y}")
print(f"   Local: x={local_x}, y={local_y}, z={local_z}\n")

reader = ModernRegionReader("./world")

# Tous les minerais possibles
ALL_ORES = [
    'minecraft:diamond_ore', 'minecraft:deepslate_diamond_ore',
    'minecraft:copper_ore', 'minecraft:deepslate_copper_ore',
    'minecraft:iron_ore', 'minecraft:deepslate_iron_ore',
    'minecraft:gold_ore', 'minecraft:deepslate_gold_ore',
    'minecraft:lapis_ore', 'minecraft:deepslate_lapis_ore',
    'minecraft:redstone_ore', 'minecraft:deepslate_redstone_ore',
    'minecraft:coal_ore', 'minecraft:deepslate_coal_ore',
    'minecraft:emerald_ore', 'minecraft:deepslate_emerald_ore',
]

for nbt_data, cx, cz in reader.iterate_chunks(show_progress=False):
    if cx != chunk_x or cz != chunk_z:
        continue
    
    print(f"✓ Chunk trouvé\n")
    
    sections = nbt_data.get('sections')
    for section in sections:
        if section.get('Y').value != section_y:
            continue
        
        print(f"✓ Section Y={section_y} trouvée\n")
        
        block_states = section.get('block_states')
        if not block_states:
            print("❌ Pas de block_states")
            break
        
        palette = block_states.get('palette')
        if not palette:
            print("❌ Pas de palette")
            break
        
        print(f"🎨 Palette ({len(palette)} blocs):")
        for idx, block in enumerate(palette):
            name = block.get('Name').value
            print(f"   [{idx:2}] {name}")
        print()
        
        # Décoder
        data = block_states.get('data')
        if not data:
            print("⚠️  Palette unique (1 seul type de bloc)")
            if len(palette) == 1:
                print(f"   Bloc unique: {palette[0].get('Name').value}")
            break
        
        if hasattr(data[0], 'value'):
            data_array = [v.value for v in data]
        else:
            data_array = list(data)
        
        indices = reader._decode_block_states(data_array, len(palette))
        
        # Calculer l'indice linéaire de la position
        linear_idx = local_x + local_z*16 + local_y*256
        
        print(f"🎯 À la position locale ({local_x}, {local_y}, {local_z}):")
        print(f"   Indice linéaire: {linear_idx}")
        print(f"   Palette index: {indices[linear_idx]}")
        print(f"   ✅ BLOC TROUVÉ: {palette[indices[linear_idx]].get('Name').value}")
        print()
        
        # Chercher tous les minerais dans un rayon de 3 blocs
        print("🔍 Minerais dans un rayon de 3 blocs:")
        found_nearby = []
        
        for i, pal_idx in enumerate(indices):
            block_name = palette[pal_idx].get('Name').value
            if block_name in ALL_ORES:
                x_loc = i % 16
                z_loc = (i // 16) % 16
                y_loc = i // 256
                
                abs_x = chunk_x * 16 + x_loc
                abs_y = section_y * 16 + y_loc
                abs_z = chunk_z * 16 + z_loc
                
                dist = ((abs_x - TEST_X)**2 + (abs_y - TEST_Y)**2 + (abs_z - TEST_Z)**2)**0.5
                
                if dist <= 3:
                    found_nearby.append({
                        'x': abs_x, 'y': abs_y, 'z': abs_z,
                        'dist': dist, 'type': block_name
                    })
        
        found_nearby.sort(key=lambda b: b['dist'])
        
        if found_nearby:
            for ore in found_nearby:
                ore_type = ore['type'].replace('minecraft:', '').replace('_ore', '')
                print(f"   • {ore_type:20} à X={ore['x']:4}, Y={ore['y']:3}, Z={ore['z']:4} "
                      f"(dist={ore['dist']:.1f}m)")
        else:
            print("   Aucun minerai trouvé à proximité")
        
        break
    break

print("\n✓ Terminé")
