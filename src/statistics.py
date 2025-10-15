"""
Module de calcul de statistiques avancées sur les ressources.
"""

from typing import Dict, List, Tuple
from collections import Counter
import json
from pathlib import Path
from datetime import datetime

from .resource_finder import ResourceStats, ResourceLocation


class StatisticsCalculator:
    """
    Classe pour calculer des statistiques détaillées sur les ressources.
    """
    
    def __init__(self):
        """Initialise le calculateur de statistiques."""
        pass
    
    def calculate_y_distribution_stats(self, stats: ResourceStats) -> Dict:
        """
        Calcule des statistiques détaillées sur la distribution en hauteur.
        
        Args:
            stats: Statistiques des ressources
        
        Returns:
            Dictionnaire avec les statistiques de distribution
        """
        if not stats.y_distribution:
            return {}
        
        y_levels = list(stats.y_distribution.keys())
        counts = list(stats.y_distribution.values())
        
        # Calculer le Y-level moyen (pondéré par le nombre de blocs)
        total_blocks = sum(counts)
        weighted_y = sum(y * count for y, count in zip(y_levels, counts)) / total_blocks
        
        # Y-level le plus fréquent
        most_common_y = max(stats.y_distribution.items(), key=lambda x: x[1])
        
        # Plage de Y-levels
        y_min = min(y_levels)
        y_max = max(y_levels)
        
        # Distribution par tranches de 16 blocs
        bins = self._bin_y_levels(stats.y_distribution, bin_size=16)
        
        return {
            "y_moyen": round(weighted_y, 2),
            "y_plus_frequent": most_common_y[0],
            "count_y_plus_frequent": most_common_y[1],
            "y_min": y_min,
            "y_max": y_max,
            "etendue_y": y_max - y_min,
            "distribution_par_tranches": bins
        }
    
    def _bin_y_levels(
        self,
        y_distribution: Dict[int, int],
        bin_size: int = 16
    ) -> Dict[str, int]:
        """
        Regroupe la distribution en tranches.
        
        Args:
            y_distribution: Distribution originale
            bin_size: Taille des tranches
        
        Returns:
            Distribution par tranches
        """
        bins = {}
        
        for y, count in y_distribution.items():
            # Calculer la tranche
            bin_start = (y // bin_size) * bin_size
            bin_end = bin_start + bin_size - 1
            bin_label = f"Y {bin_start} à {bin_end}"
            
            bins[bin_label] = bins.get(bin_label, 0) + count
        
        return bins
    
    def calculate_hotspot_stats(self, stats: ResourceStats) -> Dict:
        """
        Calcule des statistiques sur les zones riches.
        
        Args:
            stats: Statistiques des ressources
        
        Returns:
            Dictionnaire avec les statistiques des hotspots
        """
        if not stats.hotspots:
            return {
                "nombre_hotspots": 0,
                "top_hotspots": []
            }
        
        top_hotspots = []
        for x, z, count, radius in stats.hotspots[:10]:  # Top 10
            top_hotspots.append({
                "centre_x": x,
                "centre_z": z,
                "nombre_blocs": count,
                "rayon": radius,
                "densite": round(count / (3.14159 * radius * radius), 4)
            })
        
        return {
            "nombre_hotspots": len(stats.hotspots),
            "top_hotspots": top_hotspots,
            "hotspot_le_plus_riche": top_hotspots[0] if top_hotspots else None
        }
    
    def calculate_spatial_stats(self, stats: ResourceStats) -> Dict:
        """
        Calcule des statistiques spatiales (dispersion, etc.).
        
        Args:
            stats: Statistiques des ressources
        
        Returns:
            Dictionnaire avec les statistiques spatiales
        """
        if not stats.locations:
            return {}
        
        x_coords = [loc.x for loc in stats.locations]
        z_coords = [loc.z for loc in stats.locations]
        
        # Centre géométrique
        center_x = sum(x_coords) / len(x_coords)
        center_z = sum(z_coords) / len(z_coords)
        
        # Zone couverte
        x_min, x_max = min(x_coords), max(x_coords)
        z_min, z_max = min(z_coords), max(z_coords)
        
        area = (x_max - x_min) * (z_max - z_min)
        density = stats.total_count / area if area > 0 else 0
        
        return {
            "centre_geometrique": {
                "x": round(center_x, 2),
                "z": round(center_z, 2)
            },
            "zone_couverte": {
                "x_min": x_min,
                "x_max": x_max,
                "z_min": z_min,
                "z_max": z_max,
                "largeur": x_max - x_min,
                "longueur": z_max - z_min,
                "surface": area
            },
            "densite_globale": round(density, 6)
        }
    
    def generate_full_report(self, stats: ResourceStats) -> Dict:
        """
        Génère un rapport complet avec toutes les statistiques.
        
        Args:
            stats: Statistiques des ressources
        
        Returns:
            Dictionnaire complet des statistiques
        """
        return {
            "ressource": stats.resource_type,
            "total_blocs": stats.total_count,
            "timestamp": datetime.now().isoformat(),
            "distribution_hauteur": self.calculate_y_distribution_stats(stats),
            "zones_riches": self.calculate_hotspot_stats(stats),
            "statistiques_spatiales": self.calculate_spatial_stats(stats)
        }
    
    def export_to_json(
        self,
        stats: ResourceStats,
        output_path: str,
        include_locations: bool = False
    ) -> Path:
        """
        Exporte les statistiques en JSON.
        
        Args:
            stats: Statistiques des ressources
            output_path: Chemin du fichier de sortie
            include_locations: Inclure la liste complète des emplacements
        
        Returns:
            Chemin du fichier créé
        """
        report = self.generate_full_report(stats)
        
        if include_locations:
            report["emplacements"] = [
                {
                    "x": loc.x,
                    "y": loc.y,
                    "z": loc.z,
                    "block_id": loc.block_id
                }
                for loc in stats.locations
            ]
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def print_summary(self, stats: ResourceStats):
        """
        Affiche un résumé des statistiques dans la console.
        
        Args:
            stats: Statistiques des ressources
        """
        report = self.generate_full_report(stats)
        
        print(f"\n{'='*60}")
        print(f"  RAPPORT - {stats.resource_type.upper()}")
        print(f"{'='*60}\n")
        
        print(f"💎 Total trouvé: {stats.total_count} blocs\n")
        
        # Distribution en hauteur
        if "distribution_hauteur" in report:
            y_stats = report["distribution_hauteur"]
            print("📊 Distribution par hauteur:")
            print(f"   • Y moyen: {y_stats.get('y_moyen', 'N/A')}")
            print(f"   • Y le plus fréquent: {y_stats.get('y_plus_frequent', 'N/A')} "
                  f"({y_stats.get('count_y_plus_frequent', 0)} blocs)")
            print(f"   • Plage: Y {y_stats.get('y_min', 'N/A')} à {y_stats.get('y_max', 'N/A')}\n")
            
            # Top tranches
            if "distribution_par_tranches" in y_stats:
                print("   Top 3 tranches:")
                sorted_bins = sorted(
                    y_stats["distribution_par_tranches"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                for bin_label, count in sorted_bins:
                    percentage = (count / stats.total_count) * 100
                    print(f"   • {bin_label}: {count} blocs ({percentage:.1f}%)")
                print()
        
        # Zones riches
        if "zones_riches" in report:
            hotspot_stats = report["zones_riches"]
            print(f"🎯 Zones riches: {hotspot_stats['nombre_hotspots']} détectées\n")
            
            if hotspot_stats["top_hotspots"]:
                print("   Top 3 zones:")
                for i, hotspot in enumerate(hotspot_stats["top_hotspots"][:3], 1):
                    print(f"   {i}. X={hotspot['centre_x']}, Z={hotspot['centre_z']}: "
                          f"{hotspot['nombre_blocs']} blocs "
                          f"(rayon {hotspot['rayon']}m)")
                print()
        
        # Statistiques spatiales
        if "statistiques_spatiales" in report:
            spatial = report["statistiques_spatiales"]
            if "centre_geometrique" in spatial:
                center = spatial["centre_geometrique"]
                print(f"📍 Centre géométrique: X={center['x']}, Z={center['z']}\n")
            
            if "zone_couverte" in spatial:
                zone = spatial["zone_couverte"]
                print(f"🗺️  Zone couverte:")
                print(f"   • Largeur: {zone['largeur']} blocs")
                print(f"   • Longueur: {zone['longueur']} blocs")
                print(f"   • Surface: {zone['surface']:,} blocs²")
                print(f"   • Densité: {spatial['densite_globale']:.6f} blocs/bloc²\n")
        
        print(f"{'='*60}\n")


if __name__ == "__main__":
    print("Module statistics chargé avec succès ✓")
