#!/usr/bin/env python3
"""
Teste ce que le scanner de diamants détecte vraiment
"""

from src.modern_region_reader import ModernRegionReader

WORLD_PATH = "./world"
TEST_CHUNK_X = -5  # Chunk où est X=-72
TEST_CHUNK_Z = 0   # Chunk où est Z=5

DIAMOND_IDS = [
    'minecraft:diamond_ore',
    'minecraft:deepslate_diamond_ore'
]

print(f"🔍 Test du scan de diamants dans le chunk ({TEST_CHUNK_X}, {TEST_CHUNK_Z})\n")

reader = ModernRegionReader(WORLD_PATH)

for nbt_data, chunk_x, chunk_z in reader.iterate_chunks(show_progress=False):
    if chunk_x != TEST_CHUNK_X or chunk_z != TEST_CHUNK_Z:
        continue
    
    print(f"✓ Chunk ({chunk_x}, {chunk_z}) trouvé\n")
    
    # Scanner avec la fonction officielle
    found_diamonds = reader.scan_chunk_for_blocks(nbt_data, DIAMOND_IDS, y_min=-64, y_max=64)
    
    print(f"💎 Diamants trouvés par scan_chunk_for_blocks: {len(found_diamonds)}\n")
    
    if found_diamonds:
        print("📍 Positions détectées comme diamants:")
        for x_local, y, z_local, block_id in found_diamonds[:20]:
            abs_x = chunk_x * 16 + x_local
            abs_z = chunk_z * 16 + z_local
            print(f"   • X={abs_x:4}, Y={y:3}, Z={abs_z:4} - {block_id}")
        
        if len(found_diamonds) > 20:
            print(f"   ... et {len(found_diamonds) - 20} autres")
    else:
        print("   Aucun diamant détecté")
    
    print()
    
    # Maintenant cherchons manuellement dans les sections
    print("🔬 Vérification manuelle des sections:")
    sections = nbt_data.get('sections')
    
    for section in sections:
        section_y = section.get('Y').value
        
        block_states = section.get('block_states')
        if not block_states:
            continue
        
        palette = block_states.get('palette')
        if not palette:
            continue
        
        # Chercher diamant ET cuivre dans la palette
        diamond_indices = []
        copper_indices = []
        
        for idx, block in enumerate(palette):
            name = block.get('Name').value
            if name in DIAMOND_IDS:
                diamond_indices.append((idx, name))
            elif 'copper' in name.lower():
                copper_indices.append((idx, name))
        
        if diamond_indices or copper_indices:
            print(f"\n   Section Y={section_y}:")
            if diamond_indices:
                for idx, name in diamond_indices:
                    print(f"      💎 Diamant à l'index {idx}: {name}")
            if copper_indices:
                for idx, name in copper_indices:
                    print(f"      🟧 Cuivre à l'index {idx}: {name}")
    
    break

print("\n✓ Test terminé")
