#!/usr/bin/env python3
"""Test de parsing NBT direct"""

import struct
import zlib
from pathlib import Path
from io import BytesIO
from nbt import nbt

region_file = Path("./world/region/r.0.0.mca")

with open(region_file, 'rb') as f:
    # Lire chunk (0,0)
    f.seek(0)
    offset_data = struct.unpack('>I', f.read(4))[0]
    offset = (offset_data >> 8) * 4096
    
    f.seek(offset)
    length = struct.unpack('>I', f.read(4))[0]
    compression_type = struct.unpack('B', f.read(1))[0]
    chunk_data = f.read(length - 1)
    
    print(f"Compression type: {compression_type}")
    print(f"Compressed size: {len(chunk_data)}")
    
    # Décompresser
    decompressed = zlib.decompress(chunk_data)
    print(f"Decompressed size: {len(decompressed)}")
    print(f"First bytes: {decompressed[:20].hex()}")
    
    # Essayer de parser directement avec nbt
    try:
        # Méthode 1: avec fileobj
        data = nbt.NBTFile(fileobj=BytesIO(decompressed))
        print(f"✓ Parsing réussi !")
        print(f"  Clés: {list(data.keys())[:10]}")
    except Exception as e:
        print(f"❌ Erreur méthode 1: {e}")
        
        # Méthode 2: Parser manuellement le premier tag
        try:
            bio = BytesIO(decompressed)
            tag_type = struct.unpack('b', bio.read(1))[0]
            name_length = struct.unpack('>H', bio.read(2))[0]
            name = bio.read(name_length).decode('utf-8') if name_length > 0 else ""
            
            print(f"\nStructure NBT:")
            print(f"  Tag type: {tag_type} (TAG_Compound)")
            print(f"  Name length: {name_length}")
            print(f"  Name: '{name}'")
            
            # Utiliser la fonction de parsing interne
            from nbt.nbt import TAG_Compound
            bio2 = BytesIO(decompressed)
            bio2.read(1)  # Skip tag type
            bio2.read(2)  # Skip name length
            if name_length > 0:
                bio2.read(name_length)  # Skip name
            
            compound = TAG_Compound()
            compound._parse_buffer(bio2)
            
            print(f"✓ Parsing manuel réussi !")
            print(f"  Clés: {list(compound.keys())[:10]}")
            
        except Exception as e2:
            print(f"❌ Erreur parsing manuel: {e2}")
