#!/usr/bin/env python3
"""
Vérifier que les coordonnées détectées correspondent à des blocs connus
"""

from src.modern_region_reader import ModernRegionReader

reader = ModernRegionReader("./world")

print("🔍 Vérification des coordonnées\n")

# Chercher le chunk qui contient X=-74, Z=24
target_chunk_x = -74 // 16  # = -5
target_chunk_z = 24 // 16   # = 1

print(f"Chunk cible: ({target_chunk_x}, {target_chunk_z})")
print(f"Coordonnées locales: X={-74 % 16}, Z={24 % 16}\n")

DIAMOND_IDS = ['minecraft:diamond_ore', 'minecraft:deepslate_diamond_ore']

for nbt_data, chunk_x, chunk_z in reader.iterate_chunks(show_progress=False):
    if chunk_x == target_chunk_x and chunk_z == target_chunk_z:
        print(f"✓ Chunk ({chunk_x}, {chunk_z}) trouvé\n")
        
        # Scanner avec la fonction actuelle
        found = reader.scan_chunk_for_blocks(nbt_data, DIAMOND_IDS, -64, 20)
        
        print(f"💎 {len(found)} diamants détectés par scan_chunk_for_blocks\n")
        
        if found:
            print("Premiers diamants trouvés:")
            for i, (x_local, y, z_local, block_id) in enumerate(found[:20]):
                abs_x = chunk_x * 16 + x_local
                abs_z = chunk_z * 16 + z_local
                print(f"  {i+1}. X={abs_x:4}, Y={y:3}, Z={abs_z:4} (local: x={x_local:2}, z={z_local:2}) - {block_id}")
        
        # Maintenant vérifions manuellement les sections
        print("\n" + "="*70)
        print("VÉRIFICATION MANUELLE DES SECTIONS")
        print("="*70 + "\n")
        
        sections = nbt_data.get('sections')
        for section in sections:
            section_y = section.get('Y').value
            
            # Chercher la section qui contient Y=8
            if section_y != 0:  # Y=8 est dans la section Y=0 (0-15)
                continue
            
            print(f"Section Y={section_y} (blocs Y {section_y*16} à {section_y*16+15})")
            
            block_states = section.get('block_states')
            if not block_states:
                print("  Pas de block_states\n")
                continue
            
            palette = block_states.get('palette')
            if not palette:
                print("  Pas de palette\n")
                continue
            
            print(f"  Palette: {len(palette)} blocs")
            
            # Afficher la palette
            for i, block in enumerate(palette):
                name = block.get('Name').value
                print(f"    [{i}] {name}")
            
            # Chercher les indices de diamants
            diamond_indices = []
            for i, block in enumerate(palette):
                name = block.get('Name').value
                if name in DIAMOND_IDS:
                    diamond_indices.append(i)
                    print(f"\n  💎 Diamant trouvé à l'index {i} dans la palette")
            
            if not diamond_indices:
                print("  ❌ Pas de diamant dans cette section\n")
                continue
            
            # Décoder et chercher à la position locale (10, 8, 8)
            # X=-74 dans chunk -5 → local X = -74 - (-5*16) = -74 + 80 = 6
            # Z=24 dans chunk 1 → local Z = 24 - (1*16) = 8
            local_x = -74 - (chunk_x * 16)
            local_z = 24 - (chunk_z * 16)
            local_y = 8 - (section_y * 16)
            
            print(f"\n  Position cible dans ce chunk:")
            print(f"    Local: x={local_x}, y={local_y}, z={local_z}")
            
            # Calculer l'indice linéaire selon différents ordres possibles
            print(f"\n  Tests d'indexation:")
            
            # Ordre 1: y + z*16 + x*256
            idx1 = local_y + local_z*16 + local_x*256
            print(f"    Ordre Y-Z-X (y + z*16 + x*256): index={idx1}")
            
            # Ordre 2: y + x*16 + z*256
            idx2 = local_y + local_x*16 + local_z*256
            print(f"    Ordre Y-X-Z (y + x*16 + z*256): index={idx2}")
            
            # Ordre 3: x + z*16 + y*256
            idx3 = local_x + local_z*16 + local_y*256
            print(f"    Ordre X-Z-Y (x + z*16 + y*256): index={idx3}")
            
            # Décoder les données
            data = block_states.get('data')
            if data:
                import math
                if hasattr(data[0], 'value'):
                    data_array = [v.value for v in data]
                else:
                    data_array = list(data)
                
                bits_per_block = max(4, math.ceil(math.log2(len(palette))))
                indices = reader._decode_block_states(data_array, len(palette))
                
                print(f"\n  Blocs à ces positions:")
                print(f"    idx1 ({idx1}): palette[{indices[idx1]}] = {palette[indices[idx1]].get('Name').value}")
                print(f"    idx2 ({idx2}): palette[{indices[idx2]}] = {palette[indices[idx2]].get('Name').value}")
                print(f"    idx3 ({idx3}): palette[{indices[idx3]}] = {palette[indices[idx3]].get('Name').value}")
        
        break

print("\n✓ Vérification terminée")
