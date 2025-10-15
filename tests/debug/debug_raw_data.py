#!/usr/bin/env python3
"""
Affiche les données brutes NBT pour déboguer
"""

from src.modern_region_reader import ModernRegionReader

PLAYER_X = -87
PLAYER_Y = -28  
PLAYER_Z = 32

chunk_x = PLAYER_X // 16
chunk_z = PLAYER_Z // 16
section_y = PLAYER_Y // 16

print(f"Position: X={PLAYER_X}, Y={PLAYER_Y}, Z={PLAYER_Z}")
print(f"Chunk: ({chunk_x}, {chunk_z}), Section: {section_y}\n")

reader = ModernRegionReader("./world")

for nbt_data, cx, cz in reader.iterate_chunks(show_progress=False):
    if cx != chunk_x or cz != chunk_z:
        continue
    
    print(f"✓ Chunk ({cx}, {cz}) trouvé\n")
    
    sections = nbt_data.get('sections')
    for section in sections:
        if section.get('Y').value != section_y:
            continue
        
        print(f"✓ Section Y={section_y} trouvée\n")
        
        block_states = section.get('block_states')
        if not block_states:
            print("❌ Pas de block_states")
            break
        
        print("📋 Clés dans block_states:")
        for key in block_states.keys():
            print(f"   - {key}")
        print()
        
        # Vérifier le type de structure
        data = block_states.get('data')
        if data:
            print(f"📊 Data array:")
            print(f"   Type: {type(data)}")
            print(f"   Longueur: {len(data)}")
            if len(data) > 0:
                print(f"   Premier élément type: {type(data[0])}")
                print(f"   Premiers 5 longs: {data[:5]}")
        else:
            print("⚠️  Pas de data array (palette unique)")
        print()
        
        palette = block_states.get('palette')
        if palette:
            print(f"🎨 Palette ({len(palette)} blocs):")
            for idx, block in enumerate(palette):
                name = block.get('Name')
                print(f"   [{idx:2}] {name.value if name else 'N/A'}")
        print()
        
        # Chercher s'il y a d'autres champs non documentés
        print("🔍 Tous les champs de la section:")
        for key in section.keys():
            val = section.get(key)
            if key not in ['Y', 'block_states', 'biomes', 'BlockLight', 'SkyLight']:
                print(f"   - {key}: {type(val)}")
        
        break
    break

print("\n✓ Terminé")
