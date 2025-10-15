"""
Module de génération de cartes visuelles pour les ressources.
"""

from typing import List, Tuple, Optional
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from .resource_finder import ResourceLocation, ResourceStats
from .config import get_resource_color, APP_CONFIG


class MapGenerator:
    """
    Classe pour générer des cartes visuelles des ressources.
    """
    
    def __init__(self, output_dir: str = "output/maps"):
        """
        Initialise le générateur de cartes.
        
        Args:
            output_dir: Répertoire de sortie pour les cartes
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_2d_map(
        self,
        stats: ResourceStats,
        y_level: int = None,
        scale: int = None,
        show_hotspots: bool = True,
        title: str = None
    ) -> Path:
        """
        Génère une carte 2D des ressources à un Y-level spécifique.
        
        Args:
            stats: Statistiques des ressources
            y_level: Niveau Y pour la carte (None = tous les niveaux)
            scale: Échelle de la carte (1 pixel = N blocs)
            show_hotspots: Afficher les zones riches
            title: Titre personnalisé de la carte
        
        Returns:
            Chemin vers l'image générée
        """
        if scale is None:
            scale = APP_CONFIG["map_scale"]
        
        if y_level is None:
            y_level = APP_CONFIG["default_y_level"]
        
        # Filtrer les locations par Y-level si spécifié
        if y_level is not None:
            locations = [loc for loc in stats.locations if loc.y == y_level]
        else:
            locations = stats.locations
        
        if not locations:
            raise ValueError(f"Aucune ressource trouvée au niveau Y={y_level}")
        
        # Calculer les dimensions de la carte
        x_coords = [loc.x for loc in locations]
        z_coords = [loc.z for loc in locations]
        
        x_min, x_max = min(x_coords), max(x_coords)
        z_min, z_max = min(z_coords), max(z_coords)
        
        # Ajouter une marge
        margin = 50
        x_min -= margin
        x_max += margin
        z_min -= margin
        z_max += margin
        
        # Dimensions de l'image
        width = (x_max - x_min) // scale
        height = (z_max - z_min) // scale
        
        # Créer l'image (fond gris foncé)
        img = Image.new('RGB', (width, height), color=(40, 40, 40))
        draw = ImageDraw.Draw(img)
        
        # Dessiner les ressources
        resource_color = get_resource_color(stats.resource_type)
        
        for loc in locations:
            x_pixel = (loc.x - x_min) // scale
            z_pixel = (loc.z - z_min) // scale
            
            # Dessiner un petit carré pour chaque ressource
            size = max(1, scale // 2)
            draw.rectangle(
                [x_pixel - size, z_pixel - size, x_pixel + size, z_pixel + size],
                fill=resource_color
            )
        
        # Dessiner les hotspots
        if show_hotspots and stats.hotspots:
            for x_center, z_center, count, radius in stats.hotspots[:5]:  # Top 5
                x_pixel = (x_center - x_min) // scale
                z_pixel = (z_center - z_min) // scale
                radius_pixel = radius // scale
                
                # Cercle jaune semi-transparent
                draw.ellipse(
                    [
                        x_pixel - radius_pixel,
                        z_pixel - radius_pixel,
                        x_pixel + radius_pixel,
                        z_pixel + radius_pixel
                    ],
                    outline=(255, 255, 0),
                    width=2
                )
        
        # Ajouter un titre et des informations
        if title is None:
            title = f"{stats.resource_type.capitalize()} - Y={y_level}" if y_level else f"{stats.resource_type.capitalize()} - All Levels"
        
        # Créer une nouvelle image avec espace pour le titre
        final_img = Image.new('RGB', (width, height + 60), color=(20, 20, 20))
        final_img.paste(img, (0, 60))
        
        draw = ImageDraw.Draw(final_img)
        
        # Dessiner le titre et les stats
        try:
            # Essayer de charger une police
            font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
            font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except:
            font_title = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        draw.text((10, 10), title, fill=(255, 255, 255), font=font_title)
        draw.text((10, 35), f"Total: {stats.total_count} blocs | Hotspots: {len(stats.hotspots)}", 
                  fill=(200, 200, 200), font=font_small)
        
        # Sauvegarder l'image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{stats.resource_type}_map_{timestamp}.png"
        filepath = self.output_dir / filename
        
        final_img.save(filepath)
        
        return filepath
    
    def generate_height_distribution_chart(
        self,
        stats: ResourceStats,
        bin_size: int = 8
    ) -> Path:
        """
        Génère un graphique de distribution par hauteur.
        
        Args:
            stats: Statistiques des ressources
            bin_size: Taille des bins pour regrouper les Y-levels
        
        Returns:
            Chemin vers l'image du graphique
        """
        import matplotlib.pyplot as plt
        
        # Préparer les données
        y_levels = sorted(stats.y_distribution.keys())
        counts = [stats.y_distribution[y] for y in y_levels]
        
        # Regrouper par bins
        y_bins = range(min(y_levels), max(y_levels) + bin_size, bin_size)
        binned_counts = []
        
        for bin_start in y_bins:
            bin_count = sum(
                stats.y_distribution.get(y, 0)
                for y in range(bin_start, bin_start + bin_size)
            )
            binned_counts.append(bin_count)
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(12, 6))
        
        color = tuple(c / 255 for c in get_resource_color(stats.resource_type))
        ax.bar(y_bins, binned_counts, width=bin_size * 0.8, color=color, alpha=0.7)
        
        ax.set_xlabel('Y-Level', fontsize=12)
        ax.set_ylabel('Nombre de blocs', fontsize=12)
        ax.set_title(f'Distribution de {stats.resource_type.capitalize()} par hauteur', fontsize=14)
        ax.grid(True, alpha=0.3)
        
        # Sauvegarder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{stats.resource_type}_distribution_{timestamp}.png"
        filepath = self.output_dir / filename
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=150)
        plt.close()
        
        return filepath
    
    def generate_heatmap(
        self,
        stats: ResourceStats,
        grid_size: int = 16,
        y_level: int = None
    ) -> Path:
        """
        Génère une heatmap de densité des ressources.
        
        Args:
            stats: Statistiques des ressources
            grid_size: Taille de la grille pour la heatmap (en blocs)
            y_level: Niveau Y spécifique (None = tous)
        
        Returns:
            Chemin vers la heatmap
        """
        import matplotlib.pyplot as plt
        from matplotlib.colors import LinearSegmentedColormap
        
        # Filtrer par Y-level si nécessaire
        if y_level is not None:
            locations = [loc for loc in stats.locations if loc.y == y_level]
        else:
            locations = stats.locations
        
        if not locations:
            raise ValueError("Aucune ressource pour générer la heatmap")
        
        # Obtenir les coordonnées
        x_coords = [loc.x for loc in locations]
        z_coords = [loc.z for loc in locations]
        
        x_min, x_max = min(x_coords), max(x_coords)
        z_min, z_max = min(z_coords), max(z_coords)
        
        # Créer la grille
        x_bins = np.arange(x_min, x_max + grid_size, grid_size)
        z_bins = np.arange(z_min, z_max + grid_size, grid_size)
        
        # Calculer l'histogramme 2D
        heatmap, xedges, zedges = np.histogram2d(
            x_coords, z_coords,
            bins=[x_bins, z_bins]
        )
        
        # Créer la figure
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Colormap personnalisée
        colors = ['#000033', '#0000FF', '#00FFFF', '#FFFF00', '#FF0000']
        n_bins = 100
        cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)
        
        # Afficher la heatmap
        im = ax.imshow(
            heatmap.T,
            origin='lower',
            cmap=cmap,
            extent=[x_min, x_max, z_min, z_max],
            aspect='auto'
        )
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Densité', rotation=270, labelpad=20)
        
        ax.set_xlabel('X (blocs)', fontsize=12)
        ax.set_ylabel('Z (blocs)', fontsize=12)
        
        title = f'Heatmap de {stats.resource_type.capitalize()}'
        if y_level is not None:
            title += f' (Y={y_level})'
        ax.set_title(title, fontsize=14)
        
        # Sauvegarder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{stats.resource_type}_heatmap_{timestamp}.png"
        filepath = self.output_dir / filename
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=150)
        plt.close()
        
        return filepath


if __name__ == "__main__":
    print("Module map_generator chargé avec succès ✓")
