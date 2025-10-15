#!/usr/bin/env python3
"""
Vérifier que les chunks se chargent et afficher leur structure
"""

from src.modern_region_reader import ModernRegionReader

print("🔍 Vérification du chargement des chunks")
print("=" * 60)

reader = ModernRegionReader("./world")

chunk_count = 0
chunks_with_sections = 0

for nbt_data, chunk_x, chunk_z in reader.iterate_chunks(show_progress=False):
    chunk_count += 1
    
    if chunk_count <= 3:
        print(f"\n📦 Chunk ({chunk_x}, {chunk_z})")
        print(f"  Clés NBT: {list(nbt_data.keys())[:15]}")
        
        if 'sections' in nbt_data:
            chunks_with_sections += 1
            sections = nbt_data['sections']
            print(f"  ✓ {len(sections)} sections trouvées")
            
            # Analyser la première section
            if len(sections) > 0:
                section = sections[0]
                print(f"\n  Section 0:")
                print(f"    Y: {section.get('Y', 'N/A')}")
                
                if 'block_states' in section:
                    bs = section['block_states']
                    if 'palette' in bs:
                        palette = bs['palette']
                        print(f"    Palette: {len(palette)} types de blocs")
                        
                        # Afficher tous les blocs de la palette
                        for i, block in enumerate(palette):
                            name = block.get('Name')
                            if name:
                                print(f"      [{i}] {name.value}")
                                
                                # Chercher diamant
                                if 'diamond' in str(name.value).lower():
                                    print(f"        🎉 DIAMANT DÉTECTÉ !")
        else:
            print(f"  ❌ Pas de sections")
    
    if chunk_count >= 10:
        break

print(f"\n" + "=" * 60)
print(f"Total chunks chargés: {chunk_count}")
print(f"Chunks avec sections: {chunks_with_sections}")
