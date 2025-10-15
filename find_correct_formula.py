#!/usr/bin/env python3
"""
Teste toutes les formules possibles pour trouver la bonne
"""

from src.modern_region_reader import ModernRegionReader
import math

# Position du Lapis confirmée par le joueur
PLAYER_X = -87
PLAYER_Y = -28
PLAYER_Z = 32

chunk_x = PLAYER_X // 16  # -6
chunk_z = PLAYER_Z // 16  # 2
local_x = PLAYER_X - (chunk_x * 16)  # 9
local_z = PLAYER_Z - (chunk_z * 16)  # 0
section_y = PLAYER_Y // 16  # -2
local_y = PLAYER_Y - (section_y * 16)  # 4

print(f"Position: X={PLAYER_X}, Y={PLAYER_Y}, Z={PLAYER_Z}")
print(f"Chunk: ({chunk_x}, {chunk_z}), Section: {section_y}")
print(f"Local: x={local_x}, y={local_y}, z={local_z}\n")

reader = ModernRegionReader("./world")

LAPIS_IDS = ['minecraft:lapis_ore', 'minecraft:deepslate_lapis_ore']

for nbt_data, cx, cz in reader.iterate_chunks(show_progress=False):
    if cx != chunk_x or cz != chunk_z:
        continue
    
    sections = nbt_data.get('sections')
    for section in sections:
        if section.get('Y').value != section_y:
            continue
        
        block_states = section.get('block_states')
        palette = block_states.get('palette')
        
        # Trouver l'index du Lapis
        lapis_idx = None
        for idx, block in enumerate(palette):
            if block.get('Name').value in LAPIS_IDS:
                lapis_idx = idx
                break
        
        if lapis_idx is None:
            print("Pas de Lapis dans cette section")
            break
        
        print(f"Lapis à l'index {lapis_idx} de la palette\n")
        
        # Décoder
        data = block_states.get('data')
        if hasattr(data[0], 'value'):
            data_array = [v.value for v in data]
        else:
            data_array = list(data)
        
        bits_per_block = max(4, math.ceil(math.log2(len(palette))))
        indices = reader._decode_block_states(data_array, len(palette))
        
        print(f"Total indices: {len(indices)}, Bits: {bits_per_block}\n")
        
        # Tester TOUTES les formules possibles
        print("Test de toutes les formules d'indexation:")
        print("=" * 80)
        
        formulas = [
            ("y + z*16 + x*256", lambda x,y,z: y + z*16 + x*256),
            ("y + x*16 + z*256", lambda x,y,z: y + x*16 + z*256),
            ("x + y*16 + z*256", lambda x,y,z: x + y*16 + z*256),
            ("x + z*16 + y*256", lambda x,y,z: x + z*16 + y*256),
            ("z + x*16 + y*256", lambda x,y,z: z + x*16 + y*256),
            ("z + y*16 + x*256", lambda x,y,z: z + y*16 + x*256),
        ]
        
        for formula_name, formula_func in formulas:
            idx = formula_func(local_x, local_y, local_z)
            if idx >= len(indices):
                print(f"❌ {formula_name:20} → index {idx} hors limites")
                continue
            
            palette_idx = indices[idx]
            block_name = palette[palette_idx].get('Name').value
            
            if palette_idx == lapis_idx:
                print(f"✅ {formula_name:20} → index {idx:4} → LAPIS TROUVÉ ! 💎")
                print(f"   → CETTE FORMULE EST CORRECTE !")
            else:
                print(f"❌ {formula_name:20} → index {idx:4} → {block_name}")
        
        print("=" * 80)
        break
    break

print("\n✓ Test terminé")
