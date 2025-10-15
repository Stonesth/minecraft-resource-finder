#!/usr/bin/env python3
"""
Tester tous les ordres possibles de conversion indice → coordonnées
"""

from src.modern_region_reader import ModernRegionReader
import math

reader = ModernRegionReader("./world")

print("🔍 Test des ordres de coordonnées\n")

# Position où l'utilisateur a trouvé du Lapis : X=-81, Y=9, Z=19
# Vérifions dans quel chunk c'est
lapis_chunk_x = -81 // 16  # = -6
lapis_chunk_z = 19 // 16   # = 1
lapis_local_x = -81 - (lapis_chunk_x * 16)  # = -81 - (-96) = 15
lapis_local_z = 19 - (lapis_chunk_z * 16)   # = 19 - 16 = 3
lapis_y = 9
lapis_section_y = 9 // 16  # = 0

print(f"📍 Lapis trouvé par l'utilisateur:")
print(f"   Absolues: X=-81, Y=9, Z=19")
print(f"   Chunk: ({lapis_chunk_x}, {lapis_chunk_z})")
print(f"   Locales: x={lapis_local_x}, y={lapis_y % 16}, z={lapis_local_z}")
print(f"   Section Y: {lapis_section_y}\n")

LAPIS_IDS = ['minecraft:lapis_ore', 'minecraft:deepslate_lapis_ore']

# Chercher ce chunk
for nbt_data, chunk_x, chunk_z in reader.iterate_chunks(show_progress=False):
    if chunk_x == lapis_chunk_x and chunk_z == lapis_chunk_z:
        print(f"✓ Chunk ({chunk_x}, {chunk_z}) trouvé\n")
        
        sections = nbt_data.get('sections')
        for section in sections:
            section_y_val = section.get('Y').value
            
            if section_y_val != lapis_section_y:
                continue
            
            print(f"Section Y={section_y_val}")
            
            block_states = section.get('block_states')
            if not block_states:
                continue
            
            palette = block_states.get('palette')
            if not palette:
                continue
            
            print(f"Palette: {len(palette)} blocs")
            
            # Chercher le lapis dans la palette
            lapis_idx = None
            for idx, block in enumerate(palette):
                name = block.get('Name').value
                if name in LAPIS_IDS:
                    lapis_idx = idx
                    print(f"  💎 Lapis à l'index {idx} de la palette: {name}\n")
            
            if lapis_idx is None:
                print("  ❌ Pas de lapis dans cette section\n")
                continue
            
            data = block_states.get('data')
            if not data:
                print("  ⚠️  Pas de data\n")
                continue
            
            # Convertir
            if hasattr(data[0], 'value'):
                data_array = [v.value for v in data]
            else:
                data_array = list(data)
            
            # Décoder
            bits_per_block = max(4, math.ceil(math.log2(len(palette))))
            indices = reader._decode_block_states(data_array, len(palette))
            
            print(f"  Bits per block: {bits_per_block}")
            print(f"  Total indices: {len(indices)}\n")
            
            # Tester TOUS les ordres possibles
            print("  Test de TOUS les ordres de coordonnées:")
            print("  " + "="*60)
            
            # Les 6 ordres possibles pour XYZ
            orders = [
                ('X-Y-Z', lambda i: (i // 256, i % 16, (i // 16) % 16)),
                ('X-Z-Y', lambda i: (i // 256, (i // 16) % 16, i % 16)),
                ('Y-X-Z', lambda i: ((i // 16) % 16, i % 16, i // 256)),
                ('Y-Z-X', lambda i: ((i // 16) % 16, i // 256, i % 16)),
                ('Z-X-Y', lambda i: (i % 16, (i // 16) % 16, i // 256)),
                ('Z-Y-X', lambda i: (i % 16, i // 256, (i // 16) % 16))
            ]
            
            for order_name, order_func in orders:
                # Calculer l'indice linéaire attendu pour la position du lapis
                # Position locale: x=15, y=9, z=3
                found_at_expected = False
                
                # Parcourir tous les indices pour trouver le lapis
                lapis_positions = []
                for i, palette_idx in enumerate(indices):
                    if palette_idx == lapis_idx:
                        x, y, z = order_func(i)
                        lapis_positions.append((x, y, z, i))
                        
                        # Vérifier si c'est la position attendue
                        if x == lapis_local_x and y == (lapis_y % 16) and z == lapis_local_z:
                            found_at_expected = True
                
                status = "✅" if found_at_expected else "❌"
                print(f"  {status} Ordre {order_name}: {len(lapis_positions)} lapis trouvés")
                
                if found_at_expected:
                    print(f"      → TROUVÉ à la position attendue (x={lapis_local_x}, y={lapis_y % 16}, z={lapis_local_z})")
                    print(f"      → CET ORDRE EST CORRECT !")
                
                # Afficher TOUTES les positions trouvées
                if lapis_positions:
                    print(f"      Positions trouvées (x, y, z, index):")
                    for pos in lapis_positions:
                        x, y, z, idx = pos
                        abs_x = chunk_x * 16 + x
                        abs_z = chunk_z * 16 + z
                        abs_y = section_y_val * 16 + y
                        marker = " ← ATTENDU" if (x == lapis_local_x and y == (lapis_y % 16) and z == lapis_local_z) else ""
                        print(f"        local(x={x:2}, y={y:2}, z={z:2}) → abs(X={abs_x:4}, Y={abs_y:3}, Z={abs_z:3}){marker}")
            
            print("  " + "="*60)
            
        break

print("\n✓ Test terminé")
