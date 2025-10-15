"""
Module de détection des ressources dans les chunks Minecraft.
"""

from typing import List, Dict, Tuple
from collections import defaultdict
from dataclasses import dataclass

from .config import get_resource_blocks, RESOURCE_Y_DISTRIBUTION, APP_CONFIG
from .modern_region_reader import ModernRegionReader


@dataclass
class ResourceLocation:
    """
    Représente l'emplacement d'une ressource trouvée.
    """
    x: int  # Coordonnée X absolue (en blocs)
    y: int  # Coordonnée Y absolue (en blocs)
    z: int  # Coordonnée Z absolue (en blocs)
    block_id: str  # ID du bloc (ex: "minecraft:diamond_ore")
    resource_type: str  # Type de ressource (ex: "diamond")


@dataclass
class ResourceStats:
    """
    Statistiques sur les ressources trouvées.
    """
    resource_type: str
    total_count: int
    locations: List[ResourceLocation]
    y_distribution: Dict[int, int]  # Y-level -> count
    hotspots: List[Tuple[int, int, int, int]]  # (x, z, count, radius)


class ResourceFinder:
    """
    Classe pour détecter et analyser les ressources dans le monde Minecraft.
    """
    
    def __init__(self, world_path: str):
        """
        Initialise le détecteur de ressources.
        
        Args:
            world_path: Chemin vers le monde Minecraft
        """
        self.reader = ModernRegionReader(world_path)
        self.resource_locations: Dict[str, List[ResourceLocation]] = defaultdict(list)
    
    def find_resources(
        self,
        resource_name: str,
        x_range: Tuple[int, int] = None,
        z_range: Tuple[int, int] = None,
        y_range: Tuple[int, int] = None,
        show_progress: bool = True
    ) -> ResourceStats:
        """
        Recherche une ressource spécifique dans le monde.
        
        Args:
            resource_name: Nom de la ressource à chercher (ex: "diamond")
            x_range: Plage de chunks en X (min, max) ou None pour tout
            z_range: Plage de chunks en Z (min, max) ou None pour tout
            y_range: Plage de Y-levels (min, max) ou None pour utiliser la distribution naturelle
            show_progress: Afficher la progression
        
        Returns:
            Statistiques sur les ressources trouvées
        """
        # Récupérer les IDs de blocs pour cette ressource
        block_ids = get_resource_blocks(resource_name)
        
        # Déterminer la plage de Y-levels
        if y_range is None:
            y_min, y_max = RESOURCE_Y_DISTRIBUTION.get(resource_name, (-64, 320))
        else:
            y_min, y_max = y_range
        
        # Réinitialiser les emplacements pour cette ressource
        self.resource_locations[resource_name] = []
        
        # Parcourir tous les chunks
        for chunk, chunk_x, chunk_z in self.reader.iterate_chunks(show_progress=show_progress):
            # Filtrer par coordonnées de chunks si spécifié
            if x_range and not (x_range[0] <= chunk_x <= x_range[1]):
                continue
            if z_range and not (z_range[0] <= chunk_z <= z_range[1]):
                continue
            
            # Scanner le chunk pour les blocs recherchés
            found_blocks = self.reader.scan_chunk_for_blocks(
                chunk, block_ids, y_min, y_max
            )
            
            # Convertir en coordonnées absolues et enregistrer
            for x_local, y, z_local, block_id in found_blocks:
                absolute_x = chunk_x * 16 + x_local
                absolute_z = chunk_z * 16 + z_local
                
                location = ResourceLocation(
                    x=absolute_x,
                    y=y,
                    z=absolute_z,
                    block_id=block_id,
                    resource_type=resource_name
                )
                
                self.resource_locations[resource_name].append(location)
        
        # Générer les statistiques
        return self._generate_stats(resource_name)
    
    def _generate_stats(self, resource_name: str) -> ResourceStats:
        """
        Génère les statistiques pour une ressource.
        
        Args:
            resource_name: Nom de la ressource
        
        Returns:
            Objet ResourceStats avec les statistiques
        """
        locations = self.resource_locations[resource_name]
        
        # Distribution par Y-level
        y_distribution = defaultdict(int)
        for loc in locations:
            y_distribution[loc.y] += 1
        
        # Détection des zones riches (hotspots)
        hotspots = self._find_hotspots(locations)
        
        return ResourceStats(
            resource_type=resource_name,
            total_count=len(locations),
            locations=locations,
            y_distribution=dict(y_distribution),
            hotspots=hotspots
        )
    
    def _find_hotspots(
        self,
        locations: List[ResourceLocation],
        radius: int = None,
        threshold: int = None
    ) -> List[Tuple[int, int, int, int]]:
        """
        Détecte les zones riches en ressources (hotspots).
        
        Args:
            locations: Liste des emplacements de ressources
            radius: Rayon de recherche (défaut: depuis APP_CONFIG)
            threshold: Nombre minimum de blocs pour être un hotspot
        
        Returns:
            Liste de tuples (x_center, z_center, count, radius)
        """
        if not locations:
            return []
        
        if radius is None:
            radius = APP_CONFIG["hotspot_radius"]
        if threshold is None:
            threshold = APP_CONFIG["hotspot_threshold"]
        
        hotspots = []
        processed_centers = set()
        
        # Grille de recherche (tous les N blocs)
        grid_size = radius // 2
        
        # Trouver les coordonnées min/max
        x_coords = [loc.x for loc in locations]
        z_coords = [loc.z for loc in locations]
        
        x_min, x_max = min(x_coords), max(x_coords)
        z_min, z_max = min(z_coords), max(z_coords)
        
        # Scanner la grille
        for x_center in range(x_min, x_max + 1, grid_size):
            for z_center in range(z_min, z_max + 1, grid_size):
                center = (x_center, z_center)
                
                if center in processed_centers:
                    continue
                
                # Compter les blocs dans le rayon
                count = sum(
                    1 for loc in locations
                    if ((loc.x - x_center) ** 2 + (loc.z - z_center) ** 2) ** 0.5 <= radius
                )
                
                if count >= threshold:
                    hotspots.append((x_center, z_center, count, radius))
                    processed_centers.add(center)
        
        # Trier par nombre de blocs décroissant
        hotspots.sort(key=lambda h: h[2], reverse=True)
        
        return hotspots
    
    def get_locations(self, resource_name: str) -> List[ResourceLocation]:
        """
        Récupère les emplacements trouvés pour une ressource.
        
        Args:
            resource_name: Nom de la ressource
        
        Returns:
            Liste des emplacements
        """
        return self.resource_locations.get(resource_name, [])


if __name__ == "__main__":
    print("Module resource_finder chargé avec succès ✓")
