#!/usr/bin/env python3
"""
Liste TOUTES les positions où se trouve le Lapis dans la section
"""

from src.modern_region_reader import ModernRegionReader
import math

PLAYER_X = -87
PLAYER_Y = -28
PLAYER_Z = 32

chunk_x = PLAYER_X // 16
chunk_z = PLAYER_Z // 16
section_y = PLAYER_Y // 16

print(f"Position joueur: X={PLAYER_X}, Y={PLAYER_Y}, Z={PLAYER_Z}")
print(f"Chunk: ({chunk_x}, {chunk_z}), Section: {section_y}\n")

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
        
        print(f"✓ Section trouvée, {len(palette)} blocs dans la palette\n")
        
        # Trouver le Lapis
        lapis_idx = None
        for idx, block in enumerate(palette):
            if block.get('Name').value in LAPIS_IDS:
                lapis_idx = idx
                print(f"💎 Lapis trouvé à l'index {idx}: {block.get('Name').value}\n")
                break
        
        if lapis_idx is None:
            print("❌ Pas de Lapis dans la palette")
            break
        
        # Décoder
        data = block_states.get('data')
        if hasattr(data[0], 'value'):
            data_array = [v.value for v in data]
        else:
            data_array = list(data)
        
        bits_per_block = max(4, math.ceil(math.log2(len(palette))))
        indices = reader._decode_block_states(data_array, len(palette))
        
        print(f"Décodage: {len(indices)} indices, {bits_per_block} bits/bloc\n")
        
        # Chercher TOUS les indices qui contiennent le Lapis
        print("🔍 Recherche de TOUTES les positions de Lapis (index {}):\n".format(lapis_idx))
        
        lapis_positions = []
        for i, pal_idx in enumerate(indices):
            if pal_idx == lapis_idx:
                lapis_positions.append(i)
        
        print(f"✓ {len(lapis_positions)} positions trouvées avec l'index {lapis_idx}\n")
        
        if len(lapis_positions) == 0:
            print("❌ AUCUN Lapis trouvé ! Le décodage est peut-être cassé.\n")
            
            # Afficher les premiers indices décodés
            print("Premiers 20 indices décodés:")
            for i in range(min(20, len(indices))):
                print(f"  [{i}] → palette[{indices[i]}] = {palette[indices[i]].get('Name').value}")
        else:
            print(f"Liste des {len(lapis_positions)} positions (index linéaire):")
            print("="*80)
            
            for linear_idx in lapis_positions:
                # Essayer de retrouver x, y, z avec TOUTES les formules
                print(f"\nIndex linéaire: {linear_idx}")
                
                # Formule 1: y + z*16 + x*256
                x1 = linear_idx // 256
                z1 = (linear_idx % 256) // 16
                y1 = linear_idx % 16
                abs_x1 = cx * 16 + x1
                abs_z1 = cz * 16 + z1
                abs_y1 = section_y * 16 + y1
                dist1 = ((abs_x1-PLAYER_X)**2 + (abs_y1-PLAYER_Y)**2 + (abs_z1-PLAYER_Z)**2)**0.5
                marker1 = " ← JOUEUR ICI !" if abs_x1==PLAYER_X and abs_y1==PLAYER_Y and abs_z1==PLAYER_Z else ""
                print(f"  Formule y+z*16+x*256: local({x1:2},{y1:2},{z1:2}) → abs({abs_x1:4},{abs_y1:4},{abs_z1:4}) dist={dist1:.1f}m{marker1}")
                
                # Formule 2: y + x*16 + z*256
                z2 = linear_idx // 256
                x2 = (linear_idx % 256) // 16
                y2 = linear_idx % 16
                abs_x2 = cx * 16 + x2
                abs_z2 = cz * 16 + z2
                abs_y2 = section_y * 16 + y2
                dist2 = ((abs_x2-PLAYER_X)**2 + (abs_y2-PLAYER_Y)**2 + (abs_z2-PLAYER_Z)**2)**0.5
                marker2 = " ← JOUEUR ICI !" if abs_x2==PLAYER_X and abs_y2==PLAYER_Y and abs_z2==PLAYER_Z else ""
                print(f"  Formule y+x*16+z*256: local({x2:2},{y2:2},{z2:2}) → abs({abs_x2:4},{abs_y2:4},{abs_z2:4}) dist={dist2:.1f}m{marker2}")
                
                # Formule 3: x + y*16 + z*256
                z3 = linear_idx // 256
                y3 = (linear_idx % 256) // 16
                x3 = linear_idx % 16
                abs_x3 = cx * 16 + x3
                abs_z3 = cz * 16 + z3
                abs_y3 = section_y * 16 + y3
                dist3 = ((abs_x3-PLAYER_X)**2 + (abs_y3-PLAYER_Y)**2 + (abs_z3-PLAYER_Z)**2)**0.5
                marker3 = " ← JOUEUR ICI !" if abs_x3==PLAYER_X and abs_y3==PLAYER_Y and abs_z3==PLAYER_Z else ""
                print(f"  Formule x+y*16+z*256: local({x3:2},{y3:2},{z3:2}) → abs({abs_x3:4},{abs_y3:4},{abs_z3:4}) dist={dist3:.1f}m{marker3}")
        
        break
    break

print("\n✓ Test terminé")
