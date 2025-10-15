#!/usr/bin/env python3
"""
Rétro-ingénierie pour trouver la vraie formule de coordonnées
"""

from src.modern_region_reader import ModernRegionReader
import math

# Positions réelles confirmées par le joueur
TEST_BLOCKS = [
    {'type': 'redstone', 'x': -87, 'y': -28, 'z': 32},
    {'type': 'gold', 'x': -91, 'y': -20, 'z': 29},
    {'type': 'lapis', 'x': -92, 'y': 7, 'z': 27},
    {'type': 'coal', 'x': -89, 'y': 24, 'z': 27},
    {'type': 'iron', 'x': -83, 'y': 27, 'z': 30},
    {'type': 'redstone', 'x': -421, 'y': -55, 'z': 391},
    {'type': 'gold', 'x': -423, 'y': -10, 'z': 408},
    {'type': 'gold', 'x': -88, 'y': -54, 'z': 24},
    {'type': 'lapis', 'x': -81, 'y': 9, 'z': 19},
    {'type': 'emerald', 'x': -423, 'y': 61, 'z': 408},
    {'type': 'diamond', 'x': -73, 'y': -51, 'z': -7},
    {'type': 'diamond', 'x': -77, 'y': 2, 'z': 28},
]

BLOCK_IDS = {
    'diamond': ['minecraft:diamond_ore', 'minecraft:deepslate_diamond_ore'],
    'gold': ['minecraft:gold_ore', 'minecraft:deepslate_gold_ore'],
    'lapis': ['minecraft:lapis_ore', 'minecraft:deepslate_lapis_ore'],
    'iron': ['minecraft:iron_ore', 'minecraft:deepslate_iron_ore'],
    'redstone': ['minecraft:redstone_ore', 'minecraft:deepslate_redstone_ore'],
    'coal': ['minecraft:coal_ore', 'minecraft:deepslate_coal_ore'],
    'emerald': ['minecraft:emerald_ore', 'minecraft:deepslate_emerald_ore'],
}

# Toutes les formules possibles pour convertir indice → (x, y, z)
FORMULAS = {
    'y+z*16+x*256': lambda i: (i // 256, i % 16, (i // 16) % 16),  # Y-Z-X (actuel)
    'y+x*16+z*256': lambda i: ((i // 16) % 16, i % 16, i // 256),  # Y-X-Z
    'x+y*16+z*256': lambda i: (i % 16, (i // 16) % 16, i // 256),  # X-Y-Z
    'x+z*16+y*256': lambda i: (i % 16, i // 256, (i // 16) % 16),  # X-Z-Y
    'z+x*16+y*256': lambda i: ((i // 16) % 16, i // 256, i % 16),  # Z-X-Y
    'z+y*16+x*256': lambda i: (i // 256, (i // 16) % 16, i % 16),  # Z-Y-X
}

print("=" * 80)
print("🔬 RÉTRO-INGÉNIERIE DE LA FORMULE DE COORDONNÉES")
print("=" * 80)
print(f"\n📋 {len(TEST_BLOCKS)} blocs à tester\n")

reader = ModernRegionReader("./world")

# Statistiques par formule
formula_scores = {name: 0 for name in FORMULAS.keys()}
formula_distances = {name: [] for name in FORMULAS.keys()}

for idx, block_info in enumerate(TEST_BLOCKS, 1):
    block_type = block_info['type']
    x, y, z = block_info['x'], block_info['y'], block_info['z']
    
    print(f"[{idx}/{len(TEST_BLOCKS)}] {block_type.upper()} à X={x}, Y={y}, Z={z}")
    
    chunk_x = x // 16
    chunk_z = z // 16
    section_y = y // 16
    local_x = x - (chunk_x * 16)
    local_y = y - (section_y * 16)
    local_z = z - (chunk_z * 16)
    
    print(f"     Chunk ({chunk_x}, {chunk_z}), Section Y={section_y}")
    print(f"     Local: x={local_x}, y={local_y}, z={local_z}")
    
    target_ids = BLOCK_IDS.get(block_type, [])
    if not target_ids:
        print(f"     ❌ Type inconnu\n")
        continue
    
    # Chercher le chunk
    found = False
    for nbt_data, cx, cz in reader.iterate_chunks(show_progress=False):
        if cx != chunk_x or cz != chunk_z:
            continue
        
        sections = nbt_data.get('sections')
        if not sections:
            continue
        
        for section in sections:
            if section.get('Y').value != section_y:
                continue
            
            block_states = section.get('block_states')
            if not block_states:
                continue
            
            palette = block_states.get('palette')
            if not palette:
                continue
            
            # Trouver les indices du bloc dans la palette
            target_indices = []
            for pal_idx, block in enumerate(palette):
                name = block.get('Name').value
                if name in target_ids:
                    target_indices.append(pal_idx)
            
            if not target_indices:
                print(f"     ⚠️  Pas trouvé dans la palette\n")
                break
            
            print(f"     ✓ Palette indices: {target_indices}")
            
            # Décoder
            data = block_states.get('data')
            if not data:
                print(f"     ⚠️  Pas de data\n")
                break
            
            if hasattr(data[0], 'value'):
                data_array = [v.value for v in data]
            else:
                data_array = list(data)
            
            bits_per_block = max(4, math.ceil(math.log2(len(palette))))
            indices = reader._decode_block_states(data_array, len(palette))
            
            # Trouver TOUS les blocs correspondants
            matching_linear_indices = []
            for i, pal_idx in enumerate(indices):
                if pal_idx in target_indices:
                    matching_linear_indices.append(i)
            
            print(f"     ✓ {len(matching_linear_indices)} blocs trouvés dans la section")
            
            # Tester TOUTES les formules
            best_formula = None
            best_distance = float('inf')
            
            for formula_name, formula_func in FORMULAS.items():
                min_dist = float('inf')
                closest_pos = None
                
                for linear_idx in matching_linear_indices:
                    # Convertir avec cette formule
                    x_loc, y_loc, z_loc = formula_func(linear_idx)
                    abs_x = chunk_x * 16 + x_loc
                    abs_y = section_y * 16 + y_loc
                    abs_z = chunk_z * 16 + z_loc
                    
                    # Distance à la position réelle
                    dist = ((abs_x - x)**2 + (abs_y - y)**2 + (abs_z - z)**2)**0.5
                    
                    if dist < min_dist:
                        min_dist = dist
                        closest_pos = (abs_x, abs_y, abs_z)
                
                formula_distances[formula_name].append(min_dist)
                
                if min_dist == 0:
                    print(f"     ✅ {formula_name:20} → EXACT !")
                    formula_scores[formula_name] += 1
                    if best_distance > 0:
                        best_formula = formula_name
                        best_distance = 0
                elif min_dist < 3:
                    print(f"     🟡 {formula_name:20} → {closest_pos} (dist={min_dist:.1f}m)")
                    if min_dist < best_distance:
                        best_formula = formula_name
                        best_distance = min_dist
            
            if best_distance > 3:
                print(f"     ❌ Aucune formule proche")
            
            found = True
            break
        
        if found:
            break
    
    if not found:
        print(f"     ❌ Chunk/Section non trouvé")
    
    print()

# Résultats finaux
print("=" * 80)
print("📊 RÉSULTATS FINAUX")
print("=" * 80)
print()

print("🏆 Score par formule (nombre de matches exacts):")
sorted_scores = sorted(formula_scores.items(), key=lambda x: x[1], reverse=True)
for formula_name, score in sorted_scores:
    percentage = (score / len(TEST_BLOCKS)) * 100
    stars = "⭐" * score
    print(f"  {formula_name:20} : {score:2}/{len(TEST_BLOCKS)} ({percentage:5.1f}%) {stars}")

print()
print("📏 Distance moyenne par formule:")
for formula_name in FORMULAS.keys():
    distances = formula_distances[formula_name]
    if distances:
        avg_dist = sum(distances) / len(distances)
        max_dist = max(distances)
        print(f"  {formula_name:20} : moy={avg_dist:5.2f}m, max={max_dist:5.2f}m")

# Déterminer la meilleure formule
best_formula_name = sorted_scores[0][0]
best_score = sorted_scores[0][1]

print()
print("=" * 80)
if best_score >= len(TEST_BLOCKS) * 0.8:
    print(f"✅ FORMULE TROUVÉE : {best_formula_name}")
    print(f"   Précision : {best_score}/{len(TEST_BLOCKS)} matches exacts")
else:
    print(f"⚠️  AUCUNE FORMULE PARFAITE")
    print(f"   Meilleure : {best_formula_name} avec {best_score}/{len(TEST_BLOCKS)} matches")
    print(f"   Le problème peut être ailleurs (décodage, synchronisation, etc.)")
print("=" * 80)
