#!/usr/bin/env python3
"""
Valide la précision des coordonnées en testant une position connue
"""

from src.modern_region_reader import ModernRegionReader
import math

# ============================================================
# POSITION RÉELLE DU JOUEUR
# ============================================================
PLAYER_X = -87
PLAYER_Y = -28
PLAYER_Z = 32
EXPECTED_BLOCK = 'redstone'  # Ce qu'on devrait trouver

print("=" * 70)
print("🧪 VALIDATION DES COORDONNÉES")
print("=" * 70)
print(f"\n📍 Position réelle du joueur: X={PLAYER_X}, Y={PLAYER_Y}, Z={PLAYER_Z}")
print(f"🔍 Bloc attendu: {EXPECTED_BLOCK.upper()}")
print()

# Définir les IDs possibles
BLOCK_IDS = {
    'diamond': ['minecraft:diamond_ore', 'minecraft:deepslate_diamond_ore'],
    'gold': ['minecraft:gold_ore', 'minecraft:deepslate_gold_ore'],
    'lapis': ['minecraft:lapis_ore', 'minecraft:deepslate_lapis_ore'],
    'iron': ['minecraft:iron_ore', 'minecraft:deepslate_iron_ore'],
    'redstone': ['minecraft:redstone_ore', 'minecraft:deepslate_redstone_ore'],
}

target_ids = BLOCK_IDS.get(EXPECTED_BLOCK, [])
if not target_ids:
    print(f"❌ Type de bloc inconnu: {EXPECTED_BLOCK}")
    exit(1)

# Calculer le chunk
chunk_x = PLAYER_X // 16
chunk_z = PLAYER_Z // 16
local_x = PLAYER_X - (chunk_x * 16)
local_z = PLAYER_Z - (chunk_z * 16)
section_y = PLAYER_Y // 16
local_y = PLAYER_Y - (section_y * 16)

print("📦 Informations de chunk:")
print(f"   Chunk: ({chunk_x}, {chunk_z})")
print(f"   Section Y: {section_y}")
print(f"   Coordonnées locales: x={local_x}, y={local_y}, z={local_z}")
print()

reader = ModernRegionReader("./world")

# Chercher le chunk
found_chunk = False
for nbt_data, cx, cz in reader.iterate_chunks(show_progress=False):
    if cx == chunk_x and cz == chunk_z:
        found_chunk = True
        print(f"✓ Chunk ({cx}, {cz}) trouvé\n")
        
        # Scanner avec ma fonction
        print("🔍 Test 1: Scan avec ma fonction scan_chunk_for_blocks")
        print("-" * 70)
        found_blocks = reader.scan_chunk_for_blocks(nbt_data, target_ids, y_min=-64, y_max=320)
        
        print(f"   Total trouvé: {len(found_blocks)} blocs de {EXPECTED_BLOCK}")
        
        # Vérifier si la position exacte est dans les résultats
        exact_match = False
        close_matches = []
        
        for x_loc, y, z_loc, block_id in found_blocks:
            abs_x = cx * 16 + x_loc
            abs_z = cz * 16 + z_loc
            
            distance = math.sqrt((abs_x - PLAYER_X)**2 + (y - PLAYER_Y)**2 + (abs_z - PLAYER_Z)**2)
            
            if abs_x == PLAYER_X and y == PLAYER_Y and abs_z == PLAYER_Z:
                exact_match = True
                print(f"\n   ✅ POSITION EXACTE TROUVÉE !")
                print(f"      X={abs_x}, Y={y}, Z={abs_z}")
                print(f"      Local: x={x_loc}, y={y}, z={z_loc}")
                print(f"      Type: {block_id}")
            
            if distance <= 5:
                close_matches.append({
                    'x': abs_x, 'y': y, 'z': abs_z,
                    'local_x': x_loc, 'local_z': z_loc,
                    'distance': distance,
                    'block_id': block_id
                })
        
        if not exact_match:
            print(f"\n   ❌ POSITION EXACTE NON TROUVÉE")
            
            if close_matches:
                close_matches.sort(key=lambda b: b['distance'])
                print(f"\n   📏 Blocs proches (rayon 5 blocs):")
                for match in close_matches[:10]:
                    print(f"      • X={match['x']:4}, Y={match['y']:4}, Z={match['z']:4} "
                          f"(distance: {match['distance']:.1f}m) - {match['block_id']}")
            else:
                print(f"\n   ⚠️  Aucun bloc trouvé dans un rayon de 5 blocs")
        
        # Test 2: Analyse manuelle de la section
        print(f"\n🔬 Test 2: Analyse manuelle de la section Y={section_y}")
        print("-" * 70)
        
        sections = nbt_data.get('sections')
        section_found = False
        
        for section in sections:
            sec_y = section.get('Y').value
            if sec_y != section_y:
                continue
            
            section_found = True
            print(f"   ✓ Section Y={sec_y} trouvée")
            
            block_states = section.get('block_states')
            if not block_states:
                print(f"   ❌ Pas de block_states")
                continue
            
            palette = block_states.get('palette')
            if not palette:
                print(f"   ❌ Pas de palette")
                continue
            
            print(f"   Palette: {len(palette)} types de blocs")
            
            # Chercher TOUS les indices du bloc attendu dans la palette
            target_indices = []
            for idx, block in enumerate(palette):
                name = block.get('Name').value
                if name in target_ids:
                    target_indices.append(idx)
                    print(f"   💎 {EXPECTED_BLOCK.upper()} trouvé à l'index {idx} de la palette: {name}")
            
            if not target_indices:
                print(f"   ❌ {EXPECTED_BLOCK.upper()} non trouvé dans la palette de cette section")
                continue
            
            # Décoder les données
            data = block_states.get('data')
            if not data:
                print(f"   ⚠️  Pas de data (palette unique)")
                continue
            
            # Convertir
            if hasattr(data[0], 'value'):
                data_array = [v.value for v in data]
            else:
                data_array = list(data)
            
            # Décoder
            bits_per_block = max(4, math.ceil(math.log2(len(palette))))
            indices = reader._decode_block_states(data_array, len(palette))
            
            print(f"   Bits per block: {bits_per_block}")
            print(f"   Total indices décodés: {len(indices)}")
            
            # Calculer l'indice linéaire attendu avec le bon ordre (X-Z-Y)
            expected_index = local_x + local_z*16 + local_y*256
            
            print(f"\n   🎯 Vérification de la position locale (x={local_x}, y={local_y}, z={local_z}):")
            print(f"      Indice linéaire calculé (X-Z-Y): {expected_index}")
            print(f"      Palette index à cette position: {indices[expected_index]}")
            print(f"      Bloc à cette position: {palette[indices[expected_index]].get('Name').value}")
            
            if indices[expected_index] in target_indices:
                print(f"      ✅ C'EST DU {EXPECTED_BLOCK.upper()} ! Le calcul est CORRECT !")
            else:
                print(f"      ❌ Ce n'est PAS du {EXPECTED_BLOCK.upper()}")
                
                # Chercher où sont TOUS les blocs attendus
                print(f"\n   🔍 Recherche de toutes les positions avec les indices {target_indices}:")
                positions_found = []
                for i, pal_idx in enumerate(indices):
                    if pal_idx in target_indices:
                        # Formule correcte: X-Z-Y
                        x_loc = i % 16
                        z_loc = (i // 16) % 16
                        y_loc = i // 256
                        positions_found.append((x_loc, y_loc, z_loc, i))
                
                print(f"      Trouvé {len(positions_found)} blocs de {EXPECTED_BLOCK}")
                if positions_found:
                    print(f"      Positions (local):")
                    for x, y, z, idx in positions_found[:10]:
                        abs_x_calc = cx * 16 + x
                        abs_z_calc = cz * 16 + z
                        abs_y_calc = sec_y * 16 + y
                        marker = " ← ATTENDU" if (x == local_x and y == local_y and z == local_z) else ""
                        print(f"        x={x:2}, y={y:2}, z={z:2} → X={abs_x_calc:4}, Y={abs_y_calc:4}, Z={abs_z_calc:4}{marker}")
        
        if not section_found:
            print(f"   ❌ Section Y={section_y} non trouvée dans ce chunk")
        
        break

if not found_chunk:
    print(f"❌ Chunk ({chunk_x}, {chunk_z}) non trouvé dans le monde")

print("\n" + "=" * 70)
print("✓ Test terminé")
print("=" * 70)
