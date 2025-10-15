# Tests et Scripts de Debug

Ce dossier contient tous les scripts de test et de validation du projet.

## 📁 Structure

### `debug/`
Scripts de débogage pour analyser le format Minecraft et les données NBT :
- `debug_chunks.py` - Analyse des chunks
- `debug_coordinate_order.py` - Test de l'ordre des coordonnées
- `debug_loaded_chunks.py` - Vérification des chunks chargés
- `debug_position.py` - Analyse d'une position spécifique
- `debug_raw_data.py` - Affichage des données NBT brutes
- `debug_region_raw.py` - Lecture brute des fichiers région
- `test_decode.py` - Test du décodage des block states
- `test_decode_detail.py` - Test détaillé du décodage
- `test_diamond_detection.py` - Test de détection des diamants
- `test_nbt_parse.py` - Test du parsing NBT
- `test_region.py` - Test de lecture des régions
- `test_z_coords.py` - Test des coordonnées Z

### `validation/`
Scripts de validation et rétro-ingénierie :
- `validate_coordinates.py` - Validation des coordonnées par rapport aux positions réelles
- `verify_coords.py` - Vérification des coordonnées
- `find_correct_formula.py` - Test de toutes les formules possibles
- `reverse_engineer_formula.py` - Rétro-ingénierie de la formule avec positions réelles
- `find_all_lapis_positions.py` - Test de positionnement du lapis

## 🎯 Usage

Ces scripts ont été utilisés pour :
1. Comprendre le format Minecraft 1.21
2. Identifier la bonne formule de coordonnées (`x + z*16 + y*256`)
3. Valider la précision du système (±1-2 blocs)

Ils sont conservés pour référence et débogage futur.
