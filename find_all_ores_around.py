#!/usr/bin/env python3
"""
Recherche TOUS les minerais autour d'une position spécifique
"""

from src.modern_region_reader import ModernRegionReader
import math
from collections import defaultdict

# ============================================================
# CONFIGURATION - Modifiez ces valeurs
# ============================================================
WORLD_PATH = "./world"
TARGET_X = -88
TARGET_Z = 23
SEARCH_RADIUS = 32  # Rayon de recherche en blocs

# Définition des minerais à chercher
ORE_TYPES = {
    'Diamant 💎': [
        'minecraft:diamond_ore',
        'minecraft:deepslate_diamond_ore'
    ],
    'Or 🪙': [
        'minecraft:gold_ore',
        'minecraft:deepslate_gold_ore'
    ],
    'Fer ⚒️': [
        'minecraft:iron_ore',
        'minecraft:deepslate_iron_ore'
    ],
    'Cuivre 🟠': [
        'minecraft:copper_ore',
        'minecraft:deepslate_copper_ore'
    ],
    'Émeraude 💚': [
        'minecraft:emerald_ore',
        'minecraft:deepslate_emerald_ore'
    ],
    'Lapis 🔵': [
        'minecraft:lapis_ore',
        'minecraft:deepslate_lapis_ore'
    ],
    'Redstone 🔴': [
        'minecraft:redstone_ore',
        'minecraft:deepslate_redstone_ore'
    ],
    'Charbon ⚫': [
        'minecraft:coal_ore',
        'minecraft:deepslate_coal_ore'
    ]
}

print("=" * 70)
print(f"⛏️  RECHERCHE DE TOUS LES MINERAIS")
print(f"   Position: X={TARGET_X}, Z={TARGET_Z}")
print(f"   Rayon: {SEARCH_RADIUS} blocs")
print("=" * 70)

reader = ModernRegionReader(WORLD_PATH)

# Calculer la zone de chunks à scanner
chunk_x_min = (TARGET_X - SEARCH_RADIUS) // 16
chunk_x_max = (TARGET_X + SEARCH_RADIUS) // 16
chunk_z_min = (TARGET_Z - SEARCH_RADIUS) // 16
chunk_z_max = (TARGET_Z + SEARCH_RADIUS) // 16

print(f"\n📦 Chunks à scanner: X {chunk_x_min} à {chunk_x_max}, Z {chunk_z_min} à {chunk_z_max}")
print(f"   ({(chunk_x_max - chunk_x_min + 1) * (chunk_z_max - chunk_z_min + 1)} chunks)\n")

# Dictionnaire pour stocker tous les minerais par type
ores_by_type = defaultdict(list)

# Préparer la liste complète des IDs de minerais
all_ore_ids = []
ore_id_to_type = {}
for ore_type, ids in ORE_TYPES.items():
    for ore_id in ids:
        all_ore_ids.append(ore_id)
        ore_id_to_type[ore_id] = ore_type

# Scanner les chunks
chunks_scanned = 0
print("🔍 Scan en cours...\n")

for nbt_data, chunk_x, chunk_z in reader.iterate_chunks(show_progress=False):
    # Filtrer par zone
    if not (chunk_x_min <= chunk_x <= chunk_x_max and chunk_z_min <= chunk_z <= chunk_z_max):
        continue
    
    chunks_scanned += 1
    
    # Scanner le chunk pour TOUS les minerais
    found = reader.scan_chunk_for_blocks(nbt_data, all_ore_ids, y_min=-64, y_max=320)
    
    # Organiser par type et calculer la distance
    for x_local, y, z_local, block_id in found:
        abs_x = chunk_x * 16 + x_local
        abs_z = chunk_z * 16 + z_local
        
        # Calculer la distance 2D
        distance = math.sqrt((abs_x - TARGET_X)**2 + (abs_z - TARGET_Z)**2)
        
        if distance <= SEARCH_RADIUS:
            ore_type = ore_id_to_type[block_id]
            ores_by_type[ore_type].append({
                'x': abs_x,
                'y': y,
                'z': abs_z,
                'distance': distance,
                'block_id': block_id
            })

print(f"✓ {chunks_scanned} chunks scannés\n")

# Afficher les résultats par type de minerai
print("=" * 70)
print("📊 RÉSULTATS PAR TYPE DE MINERAI")
print("=" * 70)

for ore_type in ORE_TYPES.keys():
    ores = ores_by_type.get(ore_type, [])
    
    if ores:
        # Trier par distance
        ores.sort(key=lambda o: o['distance'])
        
        print(f"\n{ore_type}: {len(ores)} trouvé(s)")
        print("-" * 70)
        
        # Afficher les 10 plus proches
        display_count = min(10, len(ores))
        for i, ore in enumerate(ores[:display_count], 1):
            deepslate = "🪨" if "deepslate" in ore['block_id'] else "  "
            print(f"  {i:2}. X={ore['x']:4}, Y={ore['y']:4}, Z={ore['z']:4}  "
                  f"({ore['distance']:4.1f}m) {deepslate}")
        
        if len(ores) > display_count:
            print(f"      ... et {len(ores) - display_count} autres")
    else:
        print(f"\n{ore_type}: Aucun trouvé")

# Afficher le minerai le plus proche GLOBAL
print("\n" + "=" * 70)
print("🎯 MINERAI LE PLUS PROCHE (tous types)")
print("=" * 70)

all_ores = []
for ore_type, ores in ores_by_type.items():
    for ore in ores:
        ore['type'] = ore_type
        all_ores.append(ore)

if all_ores:
    all_ores.sort(key=lambda o: o['distance'])
    closest = all_ores[0]
    print(f"\n{closest['type']}")
    print(f"Position: X={closest['x']}, Y={closest['y']}, Z={closest['z']}")
    print(f"Distance: {closest['distance']:.1f} blocs")
    print(f"Type: {closest['block_id']}")
else:
    print("\nAucun minerai trouvé dans cette zone.")

# Statistiques globales
print("\n" + "=" * 70)
print("📈 STATISTIQUES GLOBALES")
print("=" * 70)

total_ores = sum(len(ores) for ores in ores_by_type.values())
print(f"\nTotal minerais trouvés: {total_ores}")
print(f"Types différents: {len([t for t, o in ores_by_type.items() if o])}")
print(f"Zone scannée: {SEARCH_RADIUS*2}m × {SEARCH_RADIUS*2}m")
print(f"Densité: {total_ores / (SEARCH_RADIUS*2*SEARCH_RADIUS*2):.4f} minerais/bloc²")

# Top 3 des minerais les plus abondants
print(f"\n🏆 Top 3 des minerais les plus abondants:")
sorted_types = sorted(ores_by_type.items(), key=lambda x: len(x[1]), reverse=True)
for i, (ore_type, ores) in enumerate(sorted_types[:3], 1):
    if ores:
        print(f"  {i}. {ore_type}: {len(ores)} blocs")

print("\n" + "=" * 70)
