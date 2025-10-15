#!/usr/bin/env python3
"""Test du décodage des block states"""

from src.modern_region_reader import ModernRegionReader

reader = ModernRegionReader("./world")

print("🔍 Test de décodage des block states\n")

chunks_tested = 0
chunks_with_diamonds_old = 0
chunks_with_diamonds_new = 0

DIAMOND_IDS = [
    'minecraft:diamond_ore',
    'minecraft:deepslate_diamond_ore'
]

for nbt_data, chunk_x, chunk_z in reader.iterate_chunks(show_progress=False):
    chunks_tested += 1
    
    # Tester avec la nouvelle méthode
    found_new = reader.scan_chunk_for_blocks(nbt_data, DIAMOND_IDS, -64, 20)
    
    # Tester l'ancienne méthode (palette seulement)
    sections = nbt_data.get('sections')
    has_diamonds_in_palette = False
    
    if sections:
        for section in sections:
            block_states = section.get('block_states')
            if not block_states:
                continue
            
            palette = block_states.get('palette')
            if not palette:
                continue
            
            for block_entry in palette:
                block_name = block_entry.get('Name')
                if block_name and block_name.value in DIAMOND_IDS:
                    has_diamonds_in_palette = True
                    break
            
            if has_diamonds_in_palette:
                break
    
    if has_diamonds_in_palette:
        chunks_with_diamonds_old += 1
    
    if found_new:
        chunks_with_diamonds_new += 1
    
    # Afficher les 3 premiers chunks avec diamants
    if has_diamonds_in_palette and chunks_with_diamonds_old <= 3:
        print(f"📦 Chunk ({chunk_x}, {chunk_z}):")
        print(f"   Diamants dans palette: OUI")
        print(f"   Diamants décodés: {len(found_new)}")
        
        # Afficher la structure de la première section avec diamants
        for section in sections:
            block_states = section.get('block_states')
            if not block_states:
                continue
            
            palette = block_states.get('palette')
            if not palette:
                continue
            
            has_diamond = False
            for block_entry in palette:
                block_name = block_entry.get('Name')
                if block_name and block_name.value in DIAMOND_IDS:
                    has_diamond = True
                    break
            
            if has_diamond:
                print(f"\n   Section Y={section.get('Y').value}:")
                print(f"     Palette size: {len(palette)}")
                
                data = block_states.get('data')
                if data:
                    print(f"     Data array length: {len(data)}")
                    print(f"     Data type: {type(data[0]) if len(data) > 0 else 'N/A'}")
                else:
                    print(f"     Data: NONE (palette unique)")
                
                # Afficher la palette
                print(f"     Palette:")
                for i, block in enumerate(palette[:10]):
                    name = block.get('Name')
                    if name:
                        print(f"       [{i}] {name.value}")
                
                break
        
        print()
    
    if chunks_tested >= 100:
        break

print("=" * 70)
print(f"Chunks testés: {chunks_tested}")
print(f"Chunks avec diamants (palette): {chunks_with_diamonds_old}")
print(f"Chunks avec diamants (décodage): {chunks_with_diamonds_new}")
print("=" * 70)

if chunks_with_diamonds_old > 0 and chunks_with_diamonds_new == 0:
    print("\n❌ PROBLÈME: Le décodage ne trouve rien alors que la palette contient des diamants !")
    print("   → Le bug est dans _decode_block_states")
elif chunks_with_diamonds_old == 0:
    print("\n⚠️  Aucun diamant trouvé dans les 100 premiers chunks")
else:
    print(f"\n✓ Le décodage semble fonctionner ({chunks_with_diamonds_new}/{chunks_with_diamonds_old})")
