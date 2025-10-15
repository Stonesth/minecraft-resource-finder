#!/usr/bin/env python3
"""
Point d'entrée principal de l'application Minecraft Resource Finder.
Interface en ligne de commande (CLI) pour analyser les ressources.
"""

import argparse
import sys
import os
from pathlib import Path
from colorama import init, Fore, Style

# Ajouter le dossier parent au PYTHONPATH pour permettre les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.resource_finder import ResourceFinder
from src.map_generator import MapGenerator
from src.statistics import StatisticsCalculator
from src.config import RESOURCE_GROUPS

# Initialiser colorama pour les couleurs dans le terminal
init(autoreset=True)


def print_header():
    """Affiche le header de l'application."""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}  ⛏️  MINECRAFT RESOURCE FINDER")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def print_success(message: str):
    """Affiche un message de succès."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Affiche un message d'erreur."""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Affiche un message d'information."""
    print(f"{Fore.YELLOW}ℹ {message}{Style.RESET_ALL}")


def parse_arguments():
    """
    Parse les arguments de la ligne de commande.
    
    Returns:
        Namespace avec les arguments parsés
    """
    parser = argparse.ArgumentParser(
        description="Analyse des ressources dans les mondes Minecraft",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  # Analyser les diamants dans tout le monde
  python main.py --world-path /path/to/world --resource diamond
  
  # Générer une carte des diamants
  python main.py --world-path /path/to/world --resource diamond --generate-map
  
  # Analyser une zone spécifique
  python main.py --world-path /path/to/world --resource diamond --x-range -10 10 --z-range -10 10
  
  # Exporter les données en JSON
  python main.py --world-path /path/to/world --resource diamond --export-json output/diamonds.json
  
Ressources disponibles: {}
        """.format(", ".join(RESOURCE_GROUPS.keys()))
    )
    
    # Arguments obligatoires
    parser.add_argument(
        "--world-path",
        type=str,
        required=True,
        help="Chemin vers le dossier du monde Minecraft"
    )
    
    parser.add_argument(
        "--resource",
        type=str,
        required=True,
        choices=list(RESOURCE_GROUPS.keys()),
        help="Type de ressource à rechercher"
    )
    
    # Filtres de zone
    parser.add_argument(
        "--x-range",
        type=int,
        nargs=2,
        metavar=("MIN", "MAX"),
        help="Plage de chunks en X (ex: --x-range -10 10)"
    )
    
    parser.add_argument(
        "--z-range",
        type=int,
        nargs=2,
        metavar=("MIN", "MAX"),
        help="Plage de chunks en Z (ex: --z-range -10 10)"
    )
    
    parser.add_argument(
        "--y-range",
        type=int,
        nargs=2,
        metavar=("MIN", "MAX"),
        help="Plage de Y-levels (ex: --y-range -64 16)"
    )
    
    # Options de sortie
    parser.add_argument(
        "--generate-map",
        action="store_true",
        help="Générer une carte 2D des ressources"
    )
    
    parser.add_argument(
        "--heatmap",
        action="store_true",
        help="Générer une heatmap de densité"
    )
    
    parser.add_argument(
        "--height-chart",
        action="store_true",
        help="Générer un graphique de distribution par hauteur"
    )
    
    parser.add_argument(
        "--export-json",
        type=str,
        metavar="PATH",
        help="Exporter les résultats en JSON"
    )
    
    parser.add_argument(
        "--include-locations",
        action="store_true",
        help="Inclure la liste complète des emplacements dans l'export JSON"
    )
    
    # Options d'affichage
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Désactiver la barre de progression"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Afficher des statistiques détaillées"
    )
    
    parser.add_argument(
        "--y-level",
        type=int,
        metavar="Y",
        help="Y-level spécifique pour la carte 2D (défaut: -54 pour diamants)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Répertoire de sortie pour les cartes et exports (défaut: output/)"
    )
    
    return parser.parse_args()


def main():
    """Fonction principale de l'application."""
    print_header()
    
    # Parser les arguments
    args = parse_arguments()
    
    # Vérifier que le monde existe
    world_path = Path(args.world_path)
    if not world_path.exists():
        print_error(f"Le chemin {args.world_path} n'existe pas")
        sys.exit(1)
    
    print_info(f"Monde: {world_path}")
    print_info(f"Ressource: {args.resource}")
    
    if args.x_range:
        print_info(f"Zone X: chunks {args.x_range[0]} à {args.x_range[1]}")
    if args.z_range:
        print_info(f"Zone Z: chunks {args.z_range[0]} à {args.z_range[1]}")
    if args.y_range:
        print_info(f"Hauteur: Y {args.y_range[0]} à {args.y_range[1]}")
    
    print()
    
    try:
        # Initialiser le finder
        print(f"{Fore.CYAN}🔍 Initialisation...{Style.RESET_ALL}")
        finder = ResourceFinder(str(world_path))
        
        # Rechercher les ressources
        print(f"{Fore.CYAN}🔎 Analyse en cours...{Style.RESET_ALL}\n")
        stats = finder.find_resources(
            resource_name=args.resource,
            x_range=tuple(args.x_range) if args.x_range else None,
            z_range=tuple(args.z_range) if args.z_range else None,
            y_range=tuple(args.y_range) if args.y_range else None,
            show_progress=not args.no_progress
        )
        
        print()
        
        # Afficher les résultats de base
        if stats.total_count == 0:
            print_error("Aucune ressource trouvée")
            sys.exit(0)
        
        print_success(f"{stats.total_count} {args.resource}(s) trouvé(s) !")
        
        # Calculer et afficher les statistiques
        calc = StatisticsCalculator()
        
        if args.stats:
            calc.print_summary(stats)
        else:
            # Affichage simplifié
            print(f"\n{Fore.YELLOW}📊 Résumé:{Style.RESET_ALL}")
            print(f"   • Total: {stats.total_count} blocs")
            print(f"   • Zones riches détectées: {len(stats.hotspots)}")
            
            if stats.hotspots:
                top_hotspot = stats.hotspots[0]
                print(f"   • Zone la plus riche: X={top_hotspot[0]}, Z={top_hotspot[1]} "
                      f"({top_hotspot[2]} blocs)\n")
        
        # Générer les outputs demandés
        output_dir = Path(args.output_dir)
        
        if args.generate_map:
            print(f"{Fore.CYAN}🗺️  Génération de la carte...{Style.RESET_ALL}")
            map_gen = MapGenerator(str(output_dir / "maps"))
            map_path = map_gen.generate_2d_map(
                stats,
                y_level=args.y_level,
                show_hotspots=True
            )
            print_success(f"Carte générée: {map_path}")
        
        if args.heatmap:
            print(f"{Fore.CYAN}🌡️  Génération de la heatmap...{Style.RESET_ALL}")
            map_gen = MapGenerator(str(output_dir / "maps"))
            heatmap_path = map_gen.generate_heatmap(
                stats,
                y_level=args.y_level
            )
            print_success(f"Heatmap générée: {heatmap_path}")
        
        if args.height_chart:
            print(f"{Fore.CYAN}📈 Génération du graphique de distribution...{Style.RESET_ALL}")
            map_gen = MapGenerator(str(output_dir / "maps"))
            chart_path = map_gen.generate_height_distribution_chart(stats)
            print_success(f"Graphique généré: {chart_path}")
        
        if args.export_json:
            print(f"{Fore.CYAN}💾 Export JSON...{Style.RESET_ALL}")
            json_path = calc.export_to_json(
                stats,
                args.export_json,
                include_locations=args.include_locations
            )
            print_success(f"Données exportées: {json_path}")
        
        print(f"\n{Fore.GREEN}✅ Analyse terminée avec succès !{Style.RESET_ALL}\n")
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Analyse interrompue par l'utilisateur{Style.RESET_ALL}")
        sys.exit(1)
    
    except Exception as e:
        print_error(f"Erreur: {e}")
        if "--debug" in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
