#!/usr/bin/env python3
"""
Test pour comprendre le problème de coordonnées Z
"""

from src.modern_region_reader import ModernRegionReader

reader = ModernRegionReader("./world")

print("🔍 Test des coordonnées Z\n")

DIAMOND_IDS = ['minecraft:diamond_ore', 'minecraft:deepslate_diamond_ore']

# Chercher un chunk avec des diamants et afficher les détails
diamonds_found = []

for nbt_data, chunk_x, chunk_z in reader.iterate_chunks(show_progress=False):
    found = reader.scan_chunk_for_blocks(nbt_data, DIAMOND_IDS, -64, 20)
    
    if found:
        # Prendre les premiers diamants
        for x_local, y, z_local, block_id in found[:5]:
            abs_x = chunk_x * 16 + x_local
            abs_z = chunk_z * 16 + z_local
            
            diamonds_found.append({
                'chunk_x': chunk_x,
                'chunk_z': chunk_z,
                'local_x': x_local,
                'local_y': y,
                'local_z': z_local,
                'abs_x': abs_x,
                'abs_y': y,
                'abs_z': abs_z,
                'block': block_id
            })
        
        if len(diamonds_found) >= 20:
            break

print(f"💎 {len(diamonds_found)} diamants trouvés\n")
print("="*100)
print(f"{'#':<4} {'Chunk':^12} {'Local':^20} {'Absolues':^24} {'Bloc':<30}")
print("="*100)

for i, d in enumerate(diamonds_found, 1):
    chunk_str = f"({d['chunk_x']:3},{d['chunk_z']:3})"
    local_str = f"x={d['local_x']:2} y={d['local_y']:3} z={d['local_z']:2}"
    abs_str = f"X={d['abs_x']:4} Y={d['abs_y']:3} Z={d['abs_z']:4}"
    
    print(f"{i:<4} {chunk_str:^12} {local_str:^20} {abs_str:^24} {d['block']:<30}")

print("="*100)

# Vérification : Le diamant que l'utilisateur a trouvé
print(f"\n🎯 VÉRIFICATION : Diamant trouvé par l'utilisateur")
print(f"   Position réelle: X=-73, Y=-51, Z=-7")
print(f"   Chunk attendu: ({-73//16}, {-7//16}) = ({-73//16}, {-7//16})")
print(f"   Coordonnées locales attendues: x={-73 % 16}, z={-7 % 16}")

# Chercher dans mes résultats
print(f"\n   Mes prédictions proches de X=-73, Y=-51:")
for d in diamonds_found:
    if d['abs_x'] in [-73, -72, -74] and d['abs_y'] in [-51, -50, -52]:
        print(f"     • X={d['abs_x']}, Y={d['abs_y']}, Z={d['abs_z']}")

print("\n")
