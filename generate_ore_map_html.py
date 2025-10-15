#!/usr/bin/env python3
"""
Génère une page HTML interactive avec tous les minerais trouvés
"""

from src.modern_region_reader import ModernRegionReader
import math
from collections import defaultdict
import json
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================
WORLD_PATH = "./world"
TARGET_X = -88
TARGET_Z = 23
SEARCH_RADIUS = 32
OUTPUT_HTML = "output/carte_minerais.html"

# Définition des minerais
ORE_TYPES = {
    'Diamant': {
        'emoji': '💎',
        'color': '#00FFFF',
        'ids': ['minecraft:diamond_ore', 'minecraft:deepslate_diamond_ore']
    },
    'Or': {
        'emoji': '🪙',
        'color': '#FFD700',
        'ids': ['minecraft:gold_ore', 'minecraft:deepslate_gold_ore']
    },
    'Fer': {
        'emoji': '⚒️',
        'color': '#D3D3D3',
        'ids': ['minecraft:iron_ore', 'minecraft:deepslate_iron_ore']
    },
    'Cuivre': {
        'emoji': '🟠',
        'color': '#FF8C00',
        'ids': ['minecraft:copper_ore', 'minecraft:deepslate_copper_ore']
    },
    'Émeraude': {
        'emoji': '💚',
        'color': '#00FF00',
        'ids': ['minecraft:emerald_ore', 'minecraft:deepslate_emerald_ore']
    },
    'Lapis': {
        'emoji': '🔵',
        'color': '#0000FF',
        'ids': ['minecraft:lapis_ore', 'minecraft:deepslate_lapis_ore']
    },
    'Redstone': {
        'emoji': '🔴',
        'color': '#FF0000',
        'ids': ['minecraft:redstone_ore', 'minecraft:deepslate_redstone_ore']
    },
    'Charbon': {
        'emoji': '⚫',
        'color': '#404040',
        'ids': ['minecraft:coal_ore', 'minecraft:deepslate_coal_ore']
    }
}

print("=" * 70)
print("🗺️  GÉNÉRATION DE LA CARTE HTML DES MINERAIS")
print("=" * 70)

reader = ModernRegionReader(WORLD_PATH)

# Calculer la zone de chunks
chunk_x_min = (TARGET_X - SEARCH_RADIUS) // 16
chunk_x_max = (TARGET_X + SEARCH_RADIUS) // 16
chunk_z_min = (TARGET_Z - SEARCH_RADIUS) // 16
chunk_z_max = (TARGET_Z + SEARCH_RADIUS) // 16

print(f"\n📍 Position centrale: X={TARGET_X}, Z={TARGET_Z}")
print(f"🔍 Rayon de recherche: {SEARCH_RADIUS} blocs")
print(f"📦 Chunks: X {chunk_x_min} à {chunk_x_max}, Z {chunk_z_min} à {chunk_z_max}\n")

# Collecter les minerais
ores_by_type = defaultdict(list)
all_ore_ids = []
ore_id_to_type = {}

for ore_type, data in ORE_TYPES.items():
    for ore_id in data['ids']:
        all_ore_ids.append(ore_id)
        ore_id_to_type[ore_id] = ore_type

print("🔍 Scan des chunks...\n")

chunks_scanned = 0
for nbt_data, chunk_x, chunk_z in reader.iterate_chunks(show_progress=False):
    if not (chunk_x_min <= chunk_x <= chunk_x_max and chunk_z_min <= chunk_z <= chunk_z_max):
        continue
    
    chunks_scanned += 1
    found = reader.scan_chunk_for_blocks(nbt_data, all_ore_ids, y_min=-64, y_max=320)
    
    for x_local, y, z_local, block_id in found:
        abs_x = chunk_x * 16 + x_local
        abs_z = chunk_z * 16 + z_local
        distance = math.sqrt((abs_x - TARGET_X)**2 + (abs_z - TARGET_Z)**2)
        
        if distance <= SEARCH_RADIUS:
            ore_type = ore_id_to_type[block_id]
            ores_by_type[ore_type].append({
                'x': abs_x,
                'y': y,
                'z': abs_z,
                'distance': distance,
                'deepslate': 'deepslate' in block_id
            })

print(f"✓ {chunks_scanned} chunks scannés")

# Générer le HTML
html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carte des Minerais - Minecraft</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #fff;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(0, 0, 0, 0.7);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }}
        
        h1 {{
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }}
        
        .info-box {{
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .filters {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 30px;
            justify-content: center;
        }}
        
        .filter-btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .filter-btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }}
        
        .filter-btn.active {{
            box-shadow: 0 0 20px currentColor;
        }}
        
        .ore-section {{
            margin-bottom: 30px;
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 10px;
        }}
        
        .ore-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
            cursor: pointer;
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
        }}
        
        .ore-header:hover {{
            background: rgba(255, 255, 255, 0.15);
        }}
        
        .ore-emoji {{
            font-size: 2em;
        }}
        
        .ore-title {{
            font-size: 1.5em;
            font-weight: bold;
        }}
        
        .ore-count {{
            margin-left: auto;
            background: rgba(255, 255, 255, 0.2);
            padding: 5px 15px;
            border-radius: 20px;
        }}
        
        .ore-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 10px;
            max-height: 400px;
            overflow-y: auto;
            padding: 10px;
        }}
        
        .ore-item {{
            background: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 5px;
            border-left: 3px solid;
            transition: all 0.3s;
        }}
        
        .ore-item:hover {{
            background: rgba(255, 255, 255, 0.2);
            transform: translateX(5px);
        }}
        
        .coords {{
            font-family: 'Courier New', monospace;
            font-weight: bold;
        }}
        
        .distance {{
            color: #FFD700;
            font-size: 0.9em;
        }}
        
        .deepslate {{
            background: rgba(100, 100, 100, 0.3);
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 30px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #FFD700;
        }}
        
        .stat-label {{
            margin-top: 5px;
            opacity: 0.8;
        }}
        
        .hidden {{
            display: none;
        }}
        
        ::-webkit-scrollbar {{
            width: 10px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.3);
            border-radius: 5px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.5);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⛏️ Carte des Minerais - Minecraft</h1>
        
        <div class="info-box">
            <div><strong>📍 Position centrale:</strong> X={TARGET_X}, Z={TARGET_Z}</div>
            <div><strong>🔍 Rayon de recherche:</strong> {SEARCH_RADIUS} blocs</div>
            <div><strong>📅 Généré le:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</div>
        </div>
        
        <div class="filters">
"""

# Ajouter les boutons de filtre
for ore_type, data in ORE_TYPES.items():
    count = len(ores_by_type.get(ore_type, []))
    html_content += f"""
            <button class="filter-btn active" 
                    data-ore="{ore_type}"
                    style="background-color: {data['color']}; color: #000;">
                <span>{data['emoji']}</span>
                <span>{ore_type} ({count})</span>
            </button>
"""

html_content += """
        </div>
        
        <div id="ore-sections">
"""

# Ajouter les sections pour chaque minerai
for ore_type, data in ORE_TYPES.items():
    ores = ores_by_type.get(ore_type, [])
    if not ores:
        continue
    
    ores.sort(key=lambda o: o['distance'])
    
    html_content += f"""
        <div class="ore-section" data-ore-section="{ore_type}">
            <div class="ore-header" onclick="toggleSection('{ore_type}')">
                <span class="ore-emoji">{data['emoji']}</span>
                <span class="ore-title">{ore_type}</span>
                <span class="ore-count">{len(ores)} trouvé(s)</span>
            </div>
            <div class="ore-list" id="list-{ore_type}">
"""
    
    for i, ore in enumerate(ores[:100], 1):  # Limiter à 100 par type
        deepslate_class = "deepslate" if ore['deepslate'] else ""
        html_content += f"""
                <div class="ore-item {deepslate_class}" style="border-color: {data['color']}">
                    <div class="coords">X={ore['x']}, Y={ore['y']}, Z={ore['z']}</div>
                    <div class="distance">📏 {ore['distance']:.1f}m</div>
                    {'<div>🪨 Deepslate</div>' if ore['deepslate'] else ''}
                </div>
"""
    
    if len(ores) > 100:
        html_content += f"<div class='ore-item'>... et {len(ores) - 100} autres</div>"
    
    html_content += """
            </div>
        </div>
"""

# Statistiques globales
total_ores = sum(len(ores) for ores in ores_by_type.values())
types_found = len([t for t, o in ores_by_type.items() if o])

html_content += f"""
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{total_ores}</div>
                <div class="stat-label">Minerais totaux</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{types_found}</div>
                <div class="stat-label">Types différents</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{SEARCH_RADIUS*2}m</div>
                <div class="stat-label">Zone scannée</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{chunks_scanned}</div>
                <div class="stat-label">Chunks analysés</div>
            </div>
        </div>
    </div>
    
    <script>
        // Filtres
        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                this.classList.toggle('active');
                const oreType = this.dataset.ore;
                const section = document.querySelector(`[data-ore-section="${{oreType}}"]`);
                if (section) {{
                    section.classList.toggle('hidden');
                }}
            }});
        }});
        
        // Toggle sections
        function toggleSection(oreType) {{
            const list = document.getElementById(`list-${{oreType}}`);
            if (list.style.display === 'none') {{
                list.style.display = 'grid';
            }} else {{
                list.style.display = 'none';
            }}
        }}
    </script>
</body>
</html>
"""

# Créer le dossier output s'il n'existe pas
import os
os.makedirs('output', exist_ok=True)

# Écrire le fichier HTML
with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✅ Carte HTML générée avec succès !")
print(f"📂 Fichier: {OUTPUT_HTML}")
print(f"\n💎 Total minerais: {total_ores}")
print(f"📊 Types trouvés: {types_found}/{len(ORE_TYPES)}")
print(f"\n🌐 Ouvrez le fichier dans votre navigateur pour voir la carte interactive !")
