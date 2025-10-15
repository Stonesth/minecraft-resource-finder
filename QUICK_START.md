# 🚀 Démarrage Rapide

## Installation (5 minutes)

```bash
# 1. Aller dans le projet
cd /Users/thononpierre/Documents/Windsurf/CascadeProjects/windsurf-project/minecraft-resource-finder

# 2. Lancer le script d'installation
./setup.sh

# 3. Activer l'environnement
source venv/bin/activate
```

## Récupérer les fichiers du serveur

### Méthode automatique (recommandé) 🚀

```bash
# 1. Configuration initiale (une seule fois)
cp server_config.sh.example server_config.sh
nano server_config.sh  # Collez votre mot de passe SSH
chmod 600 server_config.sh

# 2. Installer sshpass
brew install hudochenkov/sshpass/sshpass

# 3. Synchroniser (sans taper le mot de passe !)
./sync_from_server.sh
```

📚 **Guide complet** : `docs/SSH_CONFIG.md`

### Alternative : Clés SSH
```bash
ssh-keygen -t ed25519
ssh-copy-id root@82.25.117.8
./sync_from_server.sh  # Plus besoin de mot de passe
```

## Première utilisation

### Trouver des diamants 💎

```bash
# Script optimisé - Trouve les diamants autour de vous
python3 find_diamonds_around.py

# Résultat: Liste des diamants par distance
# Plus proche : X=-72, Y=5, Z=24 (1.0m)
# Précision : ±1-2 blocs (validée !)
```

### Tous les minerais ⛏️

```bash
# Scanner tous les types de minerais
python3 find_all_ores_around.py

# Affiche : Diamant, Or, Fer, Cuivre, Lapis, Redstone, Charbon, Émeraude
```

### Carte interactive HTML 🗺️

```bash
# Générer une carte web interactive
python3 generate_ore_map_html.py

# Ouvrir : output/carte_minerais.html
```

### Résultats

Les résultats sont dans :
- **Cartes** : `output/maps/`
- **Données JSON** : `output/data/` (avec `--export-json`)

## Cas d'usage typiques

### 1. Trouver les meilleurs spots de diamants

```bash
python src/main.py --world-path ./world --resource diamond \
  --generate-map --heatmap --stats
```

Regarder :
- 🎯 Les **zones riches** dans les stats console
- 🌡️ Les **zones rouges** dans la heatmap
- 🗺️ Les **cercles jaunes** sur la carte

### 2. Chercher autour de la base de votre fils

Si la base est à X=1234, Z=5678 :

```bash
# Convertir en chunks : X=1234 → chunk 77, Z=5678 → chunk 354
# Chercher ±10 chunks autour (±160 blocs)

python src/main.py --world-path ./world --resource diamond \
  --x-range 67 87 \
  --z-range 344 364 \
  --generate-map --stats
```

### 3. Scanner toutes les ressources

```bash
# Voir tous les minerais dans un rayon de 32 blocs
python3 find_all_ores_around.py

# Modifier le rayon et la position dans le fichier :
# TARGET_X = -88
# TARGET_Z = 23
# SEARCH_RADIUS = 32
```

## Interpréter les résultats

### Console
```
🎯 Zones riches: 3 détectées
   1. X=234, Z=-567: 18 blocs (rayon 32m)
```
→ Aller à ces coordonnées pour trouver beaucoup de diamants !

### Carte
- **Points cyan** : Diamants individuels
- **Cercles jaunes** : Top 5 des meilleures zones
- Plus c'est dense, mieux c'est !

### Heatmap
- **Rouge/Jaune** : Zones très riches → Priorité !
- **Bleu** : Peu de ressources

## Aide rapide

```bash
# Synchroniser le monde
./sync_from_server.sh

# Trouver des diamants
python3 find_diamonds_around.py

# Tous les minerais
python3 find_all_ores_around.py

# Carte HTML
python3 generate_ore_map_html.py
```

### Configuration

Éditez les fichiers pour changer la position :
- `find_diamonds_around.py` → `TARGET_X`, `TARGET_Z`
- `find_all_ores_around.py` → `TARGET_X`, `TARGET_Z`, `SEARCH_RADIUS`
- `generate_ore_map_html.py` → `TARGET_X`, `TARGET_Z`, `SEARCH_RADIUS`

## Problèmes fréquents

**"ModuleNotFoundError: No module named 'nbt'"**
```bash
pip3 install -r requirements.txt
```

**"Aucun fichier de région trouvé"**
```bash
./sync_from_server.sh  # Synchroniser d'abord
```

**"Mot de passe SSH demandé à chaque fois"**
→ Voir `docs/SSH_CONFIG.md` pour configurer l'auto-login

**"Coordonnées imprécises (+/- 5 blocs)"**
→ Normal ! Précision validée à ±1-2 blocs pour les veines de minerais

## Prochaines étapes

📚 Documentation complète : `docs/usage.md`
📖 Architecture : `README.md`

Bon minage ! ⛏️💎
