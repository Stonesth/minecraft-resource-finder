#!/usr/bin/env python3
"""
Debug bas niveau de la lecture des fichiers .mca
"""

import struct
import gzip
import zlib
from pathlib import Path
from io import BytesIO
from nbt import nbt

print("🔍 Debug bas niveau des fichiers .mca")
print("=" * 60)

region_file = Path("./world/region/r.0.0.mca")

if not region_file.exists():
    print(f"❌ Fichier non trouvé: {region_file}")
    exit(1)

print(f"✓ Fichier: {region_file}")
print(f"  Taille: {region_file.stat().st_size / 1024:.1f} KB")
print()

with open(region_file, 'rb') as f:
    # Lire la table des offsets
    print("📋 Lecture de la table des offsets...")
    
    chunks_found = 0
    for chunk_z in range(32):
        for chunk_x in range(32):
            offset_index = 4 * ((chunk_x % 32) + (chunk_z % 32) * 32)
            f.seek(offset_index)
            offset_data = struct.unpack('>I', f.read(4))[0]
            
            if offset_data != 0:
                chunks_found += 1
                
                if chunks_found <= 3:  # Afficher les 3 premiers
                    offset = (offset_data >> 8) * 4096
                    sector_count = offset_data & 0xFF
                    
                    print(f"\n  Chunk ({chunk_x}, {chunk_z}):")
                    print(f"    Offset data: 0x{offset_data:08x}")
                    print(f"    Offset: {offset}")
                    print(f"    Sectors: {sector_count}")
                    
                    # Lire le chunk
                    f.seek(offset)
                    length = struct.unpack('>I', f.read(4))[0]
                    compression_type = struct.unpack('B', f.read(1))[0]
                    
                    print(f"    Length: {length}")
                    print(f"    Compression: {compression_type} ({'GZip' if compression_type == 1 else 'Zlib' if compression_type == 2 else 'Unknown'})")
                    
                    # Lire et décompresser
                    chunk_data = f.read(length - 1)
                    
                    try:
                        if compression_type == 1:
                            decompressed = gzip.decompress(chunk_data)
                        elif compression_type == 2:
                            decompressed = zlib.decompress(chunk_data)
                        else:
                            print("    ❌ Type de compression inconnu")
                            continue
                        
                        print(f"    ✓ Décompressé: {len(decompressed)} bytes")
                        
                        # Parser NBT
                        try:
                            nbt_data = nbt.NBTFile(fileobj=BytesIO(decompressed))
                            print(f"    ✓ NBT parsé avec succès")
                            print(f"    Clés NBT: {list(nbt_data.keys())[:10]}")
                            
                            # Vérifier les sections
                            if 'sections' in nbt_data:
                                print(f"    ✓ Sections trouvées: {len(nbt_data['sections'])}")
                            else:
                                print(f"    ⚠️  Pas de 'sections' dans NBT")
                                print(f"    Toutes les clés: {list(nbt_data.keys())}")
                        
                        except Exception as e:
                            print(f"    ❌ Erreur parsing NBT: {e}")
                    
                    except Exception as e:
                        print(f"    ❌ Erreur décompression: {e}")

print(f"\n" + "=" * 60)
print(f"Total chunks trouvés: {chunks_found}")
