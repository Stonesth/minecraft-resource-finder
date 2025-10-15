#!/usr/bin/env python3
"""Test détaillé du décodage"""

from src.modern_region_reader import ModernRegionReader
import math

reader = ModernRegionReader("./world")

print("🔍 Test détaillé du décodage\n")

DIAMOND_IDS = ['minecraft:diamond_ore', 'minecraft:deepslate_diamond_ore']

for nbt_data, chunk_x, chunk_z in reader.iterate_chunks(show_progress=False):
    sections = nbt_data.get('sections')
    if not sections:
        continue
    
    for section in sections:
        block_states = section.get('block_states')
        if not block_states:
            continue
        
        palette = block_states.get('palette')
        if not palette:
            continue
        
        # Chercher les diamants dans la palette
        diamond_idx = None
        for idx, block_entry in enumerate(palette):
            block_name = block_entry.get('Name')
            if block_name and block_name.value in DIAMOND_IDS:
                diamond_idx = idx
                break
        
        if diamond_idx is None:
            continue
        
        # On a trouvé une section avec des diamants !
        section_y = section.get('Y').value
        print(f"📦 Chunk ({chunk_x}, {chunk_z}), Section Y={section_y}")
        print(f"   Palette size: {len(palette)}")
        print(f"   Diamant à l'index: {diamond_idx}")
        
        data = block_states.get('data')
        if not data:
            print(f"   ⚠️  Pas de data (palette unique)\n")
            continue
        
        print(f"   Data array length: {len(data)}")
        
        # Calculer bits per block
        bits_per_block = max(4, math.ceil(math.log2(len(palette)))) if len(palette) > 1 else 4
        print(f"   Bits per block: {bits_per_block}")
        
        # Vérifier le type de data[0]
        print(f"   Type data[0]: {type(data[0])}")
        print(f"   data[0] class: {data[0].__class__.__name__}")
        
        # Convertir en liste Python
        if hasattr(data[0], 'value'):
            data_array = [long_val.value for long_val in data]
        else:
            data_array = list(data)
        print(f"   Après conversion: type = {type(data_array[0])}")
        print(f"   Premier long: {data_array[0]:064b}")
        
        # Décoder les premiers blocs manuellement
        mask = (1 << bits_per_block) - 1
        print(f"   Mask: {mask:b} ({mask})")
        
        print(f"\n   Premiers indices décodés:")
        for i in range(10):
            bit_index = i * bits_per_block
            long_index = bit_index // 64
            bit_offset = bit_index % 64
            
            if long_index >= len(data_array):
                break
            
            value = data_array[long_index] >> bit_offset
            
            # Gérer le chevauchement
            if bit_offset + bits_per_block > 64 and long_index + 1 < len(data_array):
                remaining_bits = bit_offset + bits_per_block - 64
                value |= (data_array[long_index + 1] << (64 - bit_offset))
            
            palette_idx = value & mask
            block_name = palette[palette_idx].get('Name').value if palette_idx < len(palette) else "???"
            
            is_diamond = "💎" if palette_idx == diamond_idx else "  "
            print(f"     [{i}] palette_idx={palette_idx} → {block_name} {is_diamond}")
        
        # Compter combien de fois l'index diamant apparaît
        diamond_count = 0
        for i in range(4096):
            bit_index = i * bits_per_block
            long_index = bit_index // 64
            bit_offset = bit_index % 64
            
            if long_index >= len(data_array):
                break
            
            value = data_array[long_index] >> bit_offset
            
            if bit_offset + bits_per_block > 64 and long_index + 1 < len(data_array):
                remaining_bits = bit_offset + bits_per_block - 64
                value |= (data_array[long_index + 1] << (64 - bit_offset))
            
            palette_idx = value & mask
            if palette_idx == diamond_idx:
                diamond_count += 1
        
        print(f"\n   💎 Total diamants dans cette section: {diamond_count}")
        
        # Tester avec la fonction de la classe
        print(f"\n   Test avec _decode_block_states:")
        indices = reader._decode_block_states(data_array, len(palette))
        print(f"     Indices retournés: {len(indices)}")
        print(f"     Premiers: {indices[:10]}")
        diamond_count_func = sum(1 for idx in indices if idx == diamond_idx)
        print(f"     💎 Diamants comptés: {diamond_count_func}")
        
        print("\n" + "=" * 70 + "\n")
        
        # Montrer seulement le premier chunk pour debug
        break
    
    # Si on a trouvé un chunk avec diamants, sortir de la boucle principale
    if diamond_idx is not None:
        break

print("Aucun chunk avec diamants trouvé")
