#!/usr/bin/env python3
"""
Script de debug pour inspecter le contenu des chunks Minecraft 1.21
"""

from src.modern_region_reader import ModernRegionReader
from pathlib import Path
import json

print("🔍 Debug des chunks Minecraft 1.21")
print("=" * 60)

reader = ModernRegionReader("./world")
regions = reader.list_region_files()

print(f"✓ {len(regions)} fichiers de région trouvés")
print()

# Analyser le premier chunk non vide
chunk_count = 0
for nbt_data, chunk_x, chunk_z in reader.iterate_chunks(show_progress=False):
    chunk_count += 1
    
    if chunk_count > 3:  # Limiter à 3 chunks pour le debug
        break
    
    print(f"\n📦 Chunk ({chunk_x}, {chunk_z})")
    print("-" * 60)
    
    # Afficher la structure NBT
    print("Structure NBT disponible :")
    for key in nbt_data.keys():
        print(f"  • {key}: {type(nbt_data[key])}")
    
    # Chercher les sections
    if 'sections' in nbt_data:
        sections = nbt_data['sections']
        print(f"\n✓ {len(sections)} sections trouvées")
        
        for i, section in enumerate(sections):
            if i >= 2:  # Limiter l'affichage
                print(f"  ... ({len(sections) - 2} autres sections)")
                break
            
            print(f"\n  Section #{i}:")
            print(f"    Y: {section.get('Y', 'N/A')}")
            
            if 'block_states' in section:
                block_states = section['block_states']
                print(f"    block_states: {type(block_states)}")
                
                if 'palette' in block_states:
                    palette = block_states['palette']
                    print(f"    palette: {len(palette)} blocs")
                    
                    # Afficher les 5 premiers blocs de la palette
                    for j, block in enumerate(palette):
                        if j >= 5:
                            print(f"      ... ({len(palette) - 5} autres blocs)")
                            break
                        
                        block_name = block.get('Name', 'N/A')
                        print(f"      [{j}] {block_name}")
                        
                        # Vérifier s'il y a des diamants
                        if block_name and 'diamond' in str(block_name).lower():
                            print(f"        🎉 DIAMANT TROUVÉ !")
    
    else:
        print("❌ Pas de 'sections' trouvé")
        print("Clés disponibles:", list(nbt_data.keys()))

print("\n" + "=" * 60)
print(f"Total chunks analysés: {chunk_count}")
