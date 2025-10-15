#!/usr/bin/env python3
"""
Script de test pour déboguer la lecture des fichiers de région
"""

import anvil
from pathlib import Path

print("🔍 Test de lecture des fichiers .mca")
print("=" * 50)

region_path = Path("./world/region/r.0.0.mca")

if not region_path.exists():
    print(f"❌ Fichier non trouvé : {region_path}")
    exit(1)

print(f"✓ Fichier trouvé : {region_path}")
print(f"  Taille : {region_path.stat().st_size / 1024:.1f} KB")
print()

try:
    print("Chargement de la région...")
    region = anvil.Region.from_file(str(region_path))
    print("✓ Région chargée avec succès !")
    print()
    
    print("Test de lecture d'un chunk (0, 0)...")
    try:
        chunk = region.get_chunk(0, 0)
        print(f"✓ Chunk chargé !")
        print(f"  Version : {chunk.version if hasattr(chunk, 'version') else 'N/A'}")
        print()
        
        print("Test de lecture d'un bloc (8, -60, 8)...")
        try:
            block = chunk.get_block(8, -60, 8)
            print(f"✓ Bloc lu : {block.id}")
        except Exception as e:
            print(f"❌ Erreur lecture bloc : {e}")
        
    except anvil.EmptyChunk:
        print("⚠️  Chunk vide, essayons un autre...")
        
        # Essayer plusieurs chunks
        for cx in range(32):
            for cz in range(32):
                try:
                    chunk = region.get_chunk(cx, cz)
                    print(f"✓ Chunk ({cx}, {cz}) chargé !")
                    
                    # Essayer de lire quelques blocs
                    for y in range(-64, 320, 16):
                        try:
                            block = chunk.get_block(8, y, 8)
                            if block and 'diamond' in block.id.lower():
                                print(f"  💎 DIAMANT TROUVÉ à Y={y} : {block.id}")
                        except:
                            pass
                    
                    break
                except anvil.EmptyChunk:
                    continue
                except Exception as e:
                    print(f"❌ Erreur chunk ({cx}, {cz}): {e}")
                    continue
            else:
                continue
            break
    
except Exception as e:
    print(f"❌ Erreur : {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 50)
print("Fin du test")
