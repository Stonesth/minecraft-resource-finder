"""
Configuration globale du projet.
Contient les ID des blocs Minecraft et les paramètres de l'application.
"""

from typing import Dict, List

# IDs des blocs Minecraft (namespace:block_name format depuis 1.13+)
BLOCK_IDS: Dict[str, str] = {
    # Minerais de diamant
    "diamond_ore": "minecraft:diamond_ore",           # Pierre normale
    "deepslate_diamond_ore": "minecraft:deepslate_diamond_ore",  # Deepslate (en profondeur)
    
    # Autres minerais (pour futures extensions)
    "iron_ore": "minecraft:iron_ore",
    "deepslate_iron_ore": "minecraft:deepslate_iron_ore",
    "gold_ore": "minecraft:gold_ore",
    "deepslate_gold_ore": "minecraft:deepslate_gold_ore",
    "copper_ore": "minecraft:copper_ore",
    "deepslate_copper_ore": "minecraft:deepslate_copper_ore",
    "coal_ore": "minecraft:coal_ore",
    "deepslate_coal_ore": "minecraft:deepslate_coal_ore",
    "lapis_ore": "minecraft:lapis_ore",
    "deepslate_lapis_ore": "minecraft:deepslate_lapis_ore",
    "redstone_ore": "minecraft:redstone_ore",
    "deepslate_redstone_ore": "minecraft:deepslate_redstone_ore",
    "emerald_ore": "minecraft:emerald_ore",
    "deepslate_emerald_ore": "minecraft:deepslate_emerald_ore",
}

# Groupes de ressources pour faciliter les recherches
RESOURCE_GROUPS: Dict[str, List[str]] = {
    "diamond": [
        BLOCK_IDS["diamond_ore"],
        BLOCK_IDS["deepslate_diamond_ore"]
    ],
    "iron": [
        BLOCK_IDS["iron_ore"],
        BLOCK_IDS["deepslate_iron_ore"]
    ],
    "gold": [
        BLOCK_IDS["gold_ore"],
        BLOCK_IDS["deepslate_gold_ore"]
    ],
    "copper": [
        BLOCK_IDS["copper_ore"],
        BLOCK_IDS["deepslate_copper_ore"]
    ],
    "coal": [
        BLOCK_IDS["coal_ore"],
        BLOCK_IDS["deepslate_coal_ore"]
    ],
    "lapis": [
        BLOCK_IDS["lapis_ore"],
        BLOCK_IDS["deepslate_lapis_ore"]
    ],
    "redstone": [
        BLOCK_IDS["redstone_ore"],
        BLOCK_IDS["deepslate_redstone_ore"]
    ],
    "emerald": [
        BLOCK_IDS["emerald_ore"],
        BLOCK_IDS["deepslate_emerald_ore"]
    ],
}

# Distribution des minerais par Y-level (hauteur) en Minecraft 1.21
# Format: (y_min, y_max) pour chaque ressource
RESOURCE_Y_DISTRIBUTION: Dict[str, tuple] = {
    "diamond": (-64, 16),      # Plus fréquent entre -64 et -48
    "iron": (-64, 320),        # Présent partout mais pic en montagne et souterrain
    "gold": (-64, 32),         # Badlands: jusqu'à Y=256
    "copper": (-16, 112),      # Montagnes principalement
    "coal": (0, 320),          # Partout, pic en hauteur
    "lapis": (-64, 64),        # Souterrain
    "redstone": (-64, 16),     # Profond uniquement
    "emerald": (-16, 320),     # Montagnes uniquement
}

# Couleurs pour les cartes (RGB)
RESOURCE_COLORS: Dict[str, tuple] = {
    "diamond": (0, 255, 255),      # Cyan
    "iron": (200, 200, 200),       # Gris clair
    "gold": (255, 215, 0),         # Or
    "copper": (255, 140, 0),       # Orange
    "coal": (50, 50, 50),          # Noir
    "lapis": (0, 0, 255),          # Bleu
    "redstone": (255, 0, 0),       # Rouge
    "emerald": (0, 255, 0),        # Vert
    "stone": (128, 128, 128),      # Gris (fond)
    "air": (255, 255, 255),        # Blanc (cavernes)
}

# Paramètres de l'application
APP_CONFIG = {
    "default_y_level": -54,        # Hauteur par défaut pour les cartes 2D (optimal pour diamants)
    "chunk_size": 16,              # Taille d'un chunk (constante Minecraft)
    "region_size": 32,             # Nombre de chunks par région (constante Minecraft)
    "hotspot_radius": 32,          # Rayon (en blocs) pour détecter les zones riches
    "hotspot_threshold": 10,       # Nombre minimum de blocs pour considérer une zone comme riche
    "map_scale": 4,                # Échelle de la carte (1 pixel = N blocs)
}

def get_resource_blocks(resource_name: str) -> List[str]:
    """
    Retourne la liste des IDs de blocs pour une ressource donnée.
    
    Args:
        resource_name: Nom de la ressource (ex: "diamond", "iron")
    
    Returns:
        Liste des IDs de blocs correspondants
    
    Raises:
        ValueError: Si la ressource n'est pas reconnue
    """
    if resource_name not in RESOURCE_GROUPS:
        raise ValueError(f"Ressource inconnue: {resource_name}. "
                        f"Ressources disponibles: {list(RESOURCE_GROUPS.keys())}")
    return RESOURCE_GROUPS[resource_name]

def get_resource_color(resource_name: str) -> tuple:
    """
    Retourne la couleur RGB associée à une ressource.
    
    Args:
        resource_name: Nom de la ressource
    
    Returns:
        Tuple RGB (r, g, b)
    """
    return RESOURCE_COLORS.get(resource_name, (255, 255, 255))
