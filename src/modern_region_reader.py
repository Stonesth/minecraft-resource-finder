"""
Lecteur moderne de fichiers de région Minecraft 1.18+
Compatible avec le nouveau format de chunks (sans 'Level' tag)
"""

import struct
import gzip
import zlib
from pathlib import Path
from typing import Optional, List, Tuple, Generator, Any
from nbt import nbt
from tqdm import tqdm


class ModernRegionReader:
    """
    Lecteur de fichiers de région Minecraft pour versions 1.18+
    """
    
    def __init__(self, world_path: str):
        """
        Initialise le lecteur.
        
        Args:
            world_path: Chemin vers le monde Minecraft
        """
        self.world_path = Path(world_path)
        self.region_path = self.world_path / "region"
        
        if not self.region_path.exists():
            raise ValueError(f"Le dossier 'region' n'existe pas dans {world_path}")
    
    def list_region_files(self) -> List[Path]:
        """Liste tous les fichiers de région."""
        return sorted(self.region_path.glob("*.mca"))
    
    def get_region_coordinates(self, region_file: Path) -> Tuple[int, int]:
        """Extrait les coordonnées d'une région depuis son nom."""
        parts = region_file.stem.split('.')
        return int(parts[1]), int(parts[2])
    
    def read_chunk_data(self, region_file: Path, chunk_x: int, chunk_z: int) -> Optional[Any]:
        """
        Lit les données NBT d'un chunk spécifique.
        
        Args:
            region_file: Fichier de région
            chunk_x: Coordonnée X locale du chunk (0-31)
            chunk_z: Coordonnée Z locale du chunk (0-31)
        
        Returns:
            Données NBT du chunk ou None si vide
        """
        with open(region_file, 'rb') as f:
            # Lire l'offset table (1024 premiers octets)
            offset_index = 4 * ((chunk_x % 32) + (chunk_z % 32) * 32)
            f.seek(offset_index)
            offset_data = struct.unpack('>I', f.read(4))[0]
            
            if offset_data == 0:
                return None  # Chunk vide
            
            offset = (offset_data >> 8) * 4096
            sector_count = offset_data & 0xFF
            
            if offset == 0 or sector_count == 0:
                return None
            
            # Lire les données du chunk
            f.seek(offset)
            length = struct.unpack('>I', f.read(4))[0]
            compression_type = struct.unpack('B', f.read(1))[0]
            
            chunk_data = f.read(length - 1)
            
            # Décompresser selon le type
            if compression_type == 1:  # GZip
                chunk_data = gzip.decompress(chunk_data)
            elif compression_type == 2:  # Zlib
                chunk_data = zlib.decompress(chunk_data)
            # else: données non compressées
            
            # Parser le NBT manuellement (nbt.NBTFile ne fonctionne pas avec des données déjà décompressées)
            try:
                from io import BytesIO
                bio = BytesIO(chunk_data)
                
                # Lire l'en-tête NBT
                tag_type = struct.unpack('b', bio.read(1))[0]
                name_length = struct.unpack('>H', bio.read(2))[0]
                if name_length > 0:
                    bio.read(name_length)  # Skip le nom
                
                # Parser le TAG_Compound
                compound = nbt.TAG_Compound()
                compound._parse_buffer(bio)
                
                return compound
            except Exception as e:
                # Erreur de parsing - chunk invalide ou corrompu
                return None
    
    def get_block_id(self, nbt_data: Any, x: int, y: int, z: int) -> Optional[str]:
        """
        Récupère l'ID d'un bloc dans un chunk (format 1.18+).
        
        Args:
            nbt_data: Données NBT du chunk
            x: Coordonnée X locale (0-15)
            y: Coordonnée Y absolue (-64 à 319)
            z: Coordonnée Z locale (0-15)
        
        Returns:
            ID du bloc ou None
        """
        try:
            # Format 1.18+ : les sections sont dans 'sections'
            sections = nbt_data.get('sections')
            if not sections:
                return None
            
            # Trouver la bonne section (chaque section = 16 blocs de haut)
            section_y = y // 16
            
            for section in sections:
                if section.get('Y') and section['Y'].value == section_y:
                    # Trouver le bloc dans la palette
                    palette = section.get('block_states', {}).get('palette')
                    if not palette:
                        continue
                    
                    # Si la palette n'a qu'un seul élément, tous les blocs sont pareils
                    if len(palette) == 1:
                        return palette[0].get('Name', {}).value
                    
                    # Sinon, il faut lire les données
                    # Pour simplifier, on retourne le premier élément de la palette
                    # (cela ne donne pas le bloc exact mais permet de détecter les types)
                    for block_entry in palette:
                        block_name = block_entry.get('Name', {}).value
                        return block_name
            
            return None
            
        except Exception:
            return None
    
    def _decode_block_states(self, data_array: List[int], palette_size: int) -> List[int]:
        """
        Décode le tableau compacté de block states (format Minecraft 1.21).
        
        Minecraft 1.21 utilise un format "compact" où chaque long contient
        un nombre ENTIER de blocs (pas de chevauchement entre longs).
        
        Args:
            data_array: Tableau de longs (64 bits) contenant les indices de palette
            palette_size: Nombre d'éléments dans la palette
        
        Returns:
            Liste de 4096 indices de palette (16x16x16)
        """
        if not data_array:
            return [0] * 4096
        
        # Calculer le nombre de bits par bloc
        import math
        bits_per_block = max(4, math.ceil(math.log2(palette_size))) if palette_size > 1 else 4
        
        # Calculer combien de blocs par long (sans chevauchement)
        blocks_per_long = 64 // bits_per_block
        
        # Décoder les indices
        indices = []
        mask = (1 << bits_per_block) - 1
        
        for i in range(4096):  # 16x16x16 = 4096 blocs
            # Déterminer dans quel long se trouve ce bloc
            long_index = i // blocks_per_long
            # Position du bloc dans ce long
            block_in_long = i % blocks_per_long
            # Offset en bits dans le long
            bit_offset = block_in_long * bits_per_block
            
            if long_index >= len(data_array):
                indices.append(0)
                continue
            
            # Extraire l'indice (pas de chevauchement possible)
            value = (data_array[long_index] >> bit_offset) & mask
            indices.append(value)
        
        return indices
    
    def scan_chunk_for_blocks(
        self,
        nbt_data: Any,
        block_ids: List[str],
        y_min: int = -64,
        y_max: int = 320
    ) -> List[Tuple[int, int, int, str]]:
        """
        Scanne un chunk pour trouver des blocs spécifiques (format 1.18+).
        
        Args:
            nbt_data: Données NBT du chunk
            block_ids: Liste des IDs de blocs à rechercher
            y_min: Hauteur minimale
            y_max: Hauteur maximale
        
        Returns:
            Liste de tuples (x_local, y, z_local, block_id)
        """
        found_blocks = []
        
        try:
            sections = nbt_data.get('sections')
            if not sections:
                return found_blocks
            
            for section in sections:
                section_y = section.get('Y')
                if not section_y:
                    continue
                
                section_y_val = section_y.value
                base_y = section_y_val * 16
                
                # Vérifier si cette section est dans la plage Y
                if base_y + 15 < y_min or base_y > y_max:
                    continue
                
                # Récupérer la palette de la section
                block_states = section.get('block_states')
                if not block_states:
                    continue
                
                palette = block_states.get('palette')
                if not palette:
                    continue
                
                # Chercher nos blocs dans la palette
                target_indices = set()
                palette_names = {}
                for idx, block_entry in enumerate(palette):
                    block_name = block_entry.get('Name')
                    if block_name:
                        name_value = block_name.value
                        palette_names[idx] = name_value
                        if name_value in block_ids:
                            target_indices.add(idx)
                
                if not target_indices:
                    continue
                
                # Si la palette n'a qu'un seul bloc et c'est notre cible
                if len(palette) == 1 and 0 in target_indices:
                    # Tous les blocs de la section sont du type cible
                    block_name = palette_names[0]
                    for y_offset in range(16):
                        y = base_y + y_offset
                        if y_min <= y <= y_max:
                            for x in range(16):
                                for z in range(16):
                                    found_blocks.append((x, y, z, block_name))
                    continue
                
                # Décoder le tableau de données pour avoir les positions exactes
                data = block_states.get('data')
                if data:
                    # Vérifier si data contient des objets NBT ou des int directs
                    if hasattr(data[0], 'value'):
                        data_array = [long_val.value for long_val in data]
                    else:
                        data_array = list(data)
                    
                    # Décoder les indices
                    indices = self._decode_block_states(data_array, len(palette))
                    
                    # Parcourir chaque position et vérifier
                    for i, palette_idx in enumerate(indices):
                        if palette_idx in target_indices:
                            # Convertir l'indice linéaire en coordonnées 3D
                            # Format Minecraft 1.21: X varie le plus vite, puis Z, puis Y
                            # Formule: indice = x + z*16 + y*256
                            x_local = i % 16
                            z_local = (i // 16) % 16
                            y_offset = i // 256
                            
                            y = base_y + y_offset
                            if y_min <= y <= y_max:
                                block_name = palette_names[palette_idx]
                                found_blocks.append((x_local, y, z_local, block_name))
        
        except Exception as e:
            # Debug si nécessaire
            # print(f"Erreur scan_chunk: {e}")
            pass
        
        return found_blocks
    
    def iterate_chunks(
        self,
        region_file: Optional[Path] = None,
        show_progress: bool = True
    ) -> Generator[Tuple[Any, int, int], None, None]:
        """
        Itère sur tous les chunks.
        
        Args:
            region_file: Fichier de région spécifique ou None pour tous
            show_progress: Afficher la progression
        
        Yields:
            Tuple (nbt_data, chunk_x_abs, chunk_z_abs)
        """
        if region_file:
            region_files = [region_file]
        else:
            region_files = self.list_region_files()
        
        # Estimer le nombre total de chunks (32×32 par région)
        total_potential_chunks = len(region_files) * 32 * 32
        
        # Créer une barre de progression pour les chunks
        pbar = tqdm(total=total_potential_chunks, desc="Chunks analysés", disable=not show_progress, unit="chunks")
        
        for region_path in region_files:
            try:
                region_x, region_z = self.get_region_coordinates(region_path)
                
                for chunk_x in range(32):
                    for chunk_z in range(32):
                        try:
                            nbt_data = self.read_chunk_data(region_path, chunk_x, chunk_z)
                            
                            if nbt_data:
                                absolute_chunk_x = region_x * 32 + chunk_x
                                absolute_chunk_z = region_z * 32 + chunk_z
                                yield nbt_data, absolute_chunk_x, absolute_chunk_z
                            
                            # Mettre à jour la progression
                            pbar.update(1)
                        
                        except Exception:
                            pbar.update(1)
                            continue
            
            except Exception:
                # Sauter toute la région
                pbar.update(32 * 32)
                continue
        
        pbar.close()


if __name__ == "__main__":
    print("Module modern_region_reader chargé avec succès ✓")
