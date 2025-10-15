#!/usr/bin/env python3
"""
Recherche les diamants autour d'une position spécifique avec positions exactes
"""

from src.modern_region_reader import ModernRegionReader
import math

# Configuration
WORLD_PATH = "./world"
TARGET_X = -71
TARGET_Z = 24
SEARCH_RADIUS = 64  # Rayon de recherche en blocs
DIAMOND_IDS = [
    'minecraft:diamond_ore',
    'minecraft:deepslate_diamond_ore'
]

print("=" * 70)
print(f"🔍 RECHERCHE DE DIAMANTS AUTOUR DE X={TARGET_X}, Z={TARGET_Z}")
print(f"   Rayon de recherche: {SEARCH_RADIUS} blocs")
print("=" * 70)

reader = ModernRegionReader(WORLD_PATH)

# Calculer la zone de chunks à scanner
chunk_x_min = (TARGET_X - SEARCH_RADIUS) // 16
chunk_x_max = (TARGET_X + SEARCH_RADIUS) // 16
chunk_z_min = (TARGET_Z - SEARCH_RADIUS) // 16
chunk_z_max = (TARGET_Z + SEARCH_RADIUS) // 16

print(f"\n📦 Chunks à scanner: X {chunk_x_min} à {chunk_x_max}, Z {chunk_z_min} à {chunk_z_max}")
print(f"   ({(chunk_x_max - chunk_x_min + 1) * (chunk_z_max - chunk_z_min + 1)} chunks)\n")

diamonds = []

# Scanner les chunks dans la zone
chunks_scanned = 0
for nbt_data, chunk_x, chunk_z in reader.iterate_chunks(show_progress=False):
    # Filtrer par zone
    if not (chunk_x_min <= chunk_x <= chunk_x_max and chunk_z_min <= chunk_z <= chunk_z_max):
        continue
    
    chunks_scanned += 1
    
    # Scanner le chunk pour les diamants
    found = reader.scan_chunk_for_blocks(nbt_data, DIAMOND_IDS, y_min=-64, y_max=20)
    
    # Convertir en coordonnées absolues et calculer la distance
    for x_local, y, z_local, block_id in found:
        abs_x = chunk_x * 16 + x_local
        abs_z = chunk_z * 16 + z_local
        
        # Calculer la distance 2D par rapport au point cible
        distance = math.sqrt((abs_x - TARGET_X)**2 + (abs_z - TARGET_Z)**2)
        
        if distance <= SEARCH_RADIUS:
            diamonds.append({
                'x': abs_x,
                'y': y,
                'z': abs_z,
                'distance': distance,
                'type': block_id
            })

print(f"✓ {chunks_scanned} chunks scannés")
print(f"\n💎 {len(diamonds)} diamant(s) trouvé(s) !\n")

if diamonds:
    # Trier par distance
    diamonds.sort(key=lambda d: d['distance'])
    
    print("=" * 70)
    print("📍 COORDONNÉES DES DIAMANTS (triées par distance)")
    print("=" * 70)
    
    # Afficher les 50 premiers (ou tous si moins de 50)
    display_count = min(50, len(diamonds))
    
    for i, diamond in enumerate(diamonds[:display_count], 1):
        type_icon = "💎" if "deepslate" in diamond['type'] else "◇"
        print(f"{i:3}. {type_icon} X={diamond['x']:4}, Y={diamond['y']:3}, Z={diamond['z']:4}  "
              f"(distance: {diamond['distance']:.1f}m)")
    
    if len(diamonds) > display_count:
        print(f"\n... et {len(diamonds) - display_count} autres diamants")
    
    # Statistiques
    print("\n" + "=" * 70)
    print("📊 STATISTIQUES")
    print("=" * 70)
    
    closest = diamonds[0]
    print(f"💎 Plus proche: X={closest['x']}, Y={closest['y']}, Z={closest['z']} "
          f"({closest['distance']:.1f}m)")
    
    # Distribution par hauteur
    y_counts = {}
    for d in diamonds:
        y = d['y']
        y_counts[y] = y_counts.get(y, 0) + 1
    
    most_common_y = max(y_counts.items(), key=lambda x: x[1])
    print(f"📍 Hauteur la plus fréquente: Y={most_common_y[0]} ({most_common_y[1]} diamants)")
    
    avg_y = sum(d['y'] for d in diamonds) / len(diamonds)
    print(f"📏 Hauteur moyenne: Y={avg_y:.1f}")
    
    # Types de minerai
    deepslate = sum(1 for d in diamonds if 'deepslate' in d['type'])
    normal = len(diamonds) - deepslate
    print(f"\n🪨 Types:")
    print(f"   • Deepslate diamond ore: {deepslate}")
    print(f"   • Diamond ore: {normal}")
    
    print("\n" + "=" * 70)
    print("🎯 CONSEIL DE MINAGE")
    print("=" * 70)
    print(f"Allez à X={closest['x']}, Z={closest['z']}, Y={closest['y']}")
    print(f"C'est le diamant le plus proche ({closest['distance']:.1f} blocs) !")
    print("=" * 70)

else:
    print("❌ Aucun diamant trouvé dans cette zone.")
    print(f"   Essayez d'augmenter le rayon de recherche (actuellement {SEARCH_RADIUS} blocs)")
