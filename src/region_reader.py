"""
Module de lecture des fichiers de région Minecraft.
Utilise la bibliothèque anvil-parser pour lire les fichiers .mca
"""

import os
from pathlib import Path
from typing import List, Generator, Tuple, Optional
import anvil
from tqdm import tqdm


class RegionReader:
    """
    Classe pour lire les fichiers de région Minecraft (.mca).
    """
    
    def __init__(self, world_path: str):
        """
        Initialise le lecteur de région.
        
        Args:
            world_path: Chemin vers le dossier du monde Minecraft
        
        Raises:
            FileNotFoundError: Si le chemin n'existe pas
            ValueError: Si le dossier region n'existe pas
        """
        self.world_path = Path(world_path)
        
        if not self.world_path.exists():
            raise FileNotFoundError(f"Le chemin {world_path} n'existe pas")
        
        # Chemin vers le dossier region
        self.region_path = self.world_path / "region"
        
        if not self.region_path.exists():
            raise ValueError(f"Le dossier 'region' n'existe pas dans {world_path}")
    
    def list_region_files(self) -> List[Path]:
        """
        Liste tous les fichiers de région (.mca) disponibles.
        
        Returns:
            Liste des chemins vers les fichiers .mca
        """
        return sorted(self.region_path.glob("*.mca"))
    
    def get_region_coordinates(self, region_file: Path) -> Tuple[int, int]:
        """
        Extrait les coordonnées d'une région depuis son nom de fichier.
        Format: r.X.Z.mca
        
        Args:
            region_file: Chemin vers le fichier de région
        
        Returns:
            Tuple (x, z) des coordonnées de la région
        """
        # Format: r.X.Z.mca
        parts = region_file.stem.split('.')
        return int(parts[1]), int(parts[2])
    
    def load_region(self, region_file: Path) -> anvil.Region:
        """
        Charge un fichier de région.
        
        Args:
            region_file: Chemin vers le fichier de région
        
        Returns:
            Objet Region d'anvil-parser
        """
        return anvil.Region.from_file(str(region_file))
    
    def iterate_chunks(
        self,
        region_file: Optional[Path] = None,
        show_progress: bool = True
    ) -> Generator[Tuple[anvil.Chunk, int, int], None, None]:
        """
        Itère sur tous les chunks d'une région ou de toutes les régions.
        
        Args:
            region_file: Fichier de région spécifique (None = toutes les régions)
            show_progress: Afficher une barre de progression
        
        Yields:
            Tuple (chunk, chunk_x, chunk_z) pour chaque chunk
        """
        # Déterminer les fichiers à traiter
        if region_file:
            region_files = [region_file]
        else:
            region_files = self.list_region_files()
        
        if not region_files:
            raise ValueError("Aucun fichier de région trouvé")
        
        # Itérer sur chaque fichier de région
        for region_path in tqdm(region_files, desc="Régions", disable=not show_progress):
            try:
                region = self.load_region(region_path)
                region_x, region_z = self.get_region_coordinates(region_path)
                
                # Une région contient 32x32 chunks
                for chunk_x in range(32):
                    for chunk_z in range(32):
                        try:
                            # Coordonnées absolues du chunk
                            absolute_chunk_x = region_x * 32 + chunk_x
                            absolute_chunk_z = region_z * 32 + chunk_z
                            
                            # Charger le chunk
                            chunk = region.get_chunk(chunk_x, chunk_z)
                            
                            yield chunk, absolute_chunk_x, absolute_chunk_z
                            
                        except anvil.EmptyChunk:
                            # Chunk vide, on continue
                            continue
                        except Exception as e:
                            # Erreur sur un chunk spécifique, on continue
                            if show_progress:
                                tqdm.write(f"Erreur chunk ({chunk_x}, {chunk_z}): {e}")
                            continue
            
            except Exception as e:
                if show_progress:
                    tqdm.write(f"Erreur région {region_path.name}: {e}")
                continue
    
    def get_block_at(
        self,
        chunk: anvil.Chunk,
        x: int,
        y: int,
        z: int
    ) -> Optional[anvil.Block]:
        """
        Récupère un bloc à des coordonnées spécifiques dans un chunk.
        
        Args:
            chunk: Le chunk Minecraft
            x: Coordonnée X locale (0-15)
            y: Coordonnée Y absolue (-64 à 319 en 1.21)
            z: Coordonnée Z locale (0-15)
        
        Returns:
            Objet Block ou None si le bloc n'existe pas
        """
        try:
            return chunk.get_block(x, y, z)
        except Exception:
            return None
    
    def scan_chunk_for_blocks(
        self,
        chunk: anvil.Chunk,
        block_ids: List[str],
        y_min: int = -64,
        y_max: int = 320
    ) -> List[Tuple[int, int, int, str]]:
        """
        Scanne un chunk pour trouver des blocs spécifiques.
        
        Args:
            chunk: Le chunk à scanner
            block_ids: Liste des IDs de blocs à rechercher
            y_min: Hauteur minimale de recherche
            y_max: Hauteur maximale de recherche
        
        Returns:
            Liste de tuples (x_local, y, z_local, block_id) pour chaque bloc trouvé
        """
        found_blocks = []
        
        # Parcourir le chunk (16x16 en XZ)
        for x in range(16):
            for z in range(16):
                # Parcourir les Y-levels
                for y in range(y_min, y_max + 1):
                    block = self.get_block_at(chunk, x, y, z)
                    
                    if block and block.id in block_ids:
                        found_blocks.append((x, y, z, block.id))
        
        return found_blocks


def test_region_reader():
    """
    Fonction de test pour le RegionReader.
    """
    print("Test du RegionReader...")
    
    # Exemple d'utilisation (nécessite un monde Minecraft valide)
    world_path = "test_world"  # Remplacer par un chemin valide
    
    if not os.path.exists(world_path):
        print(f"❌ Le chemin {world_path} n'existe pas")
        print("ℹ️  Pour tester, spécifiez un chemin vers un monde Minecraft")
        return
    
    try:
        reader = RegionReader(world_path)
        regions = reader.list_region_files()
        print(f"✓ {len(regions)} fichiers de région trouvés")
        
        if regions:
            print(f"ℹ️  Premier fichier: {regions[0].name}")
            coords = reader.get_region_coordinates(regions[0])
            print(f"ℹ️  Coordonnées: {coords}")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    test_region_reader()
