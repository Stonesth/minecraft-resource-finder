# Guide d'utilisation - Minecraft Resource Finder

## Table des matières
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Utilisation de base](#utilisation-de-base)
4. [Options avancées](#options-avancées)
5. [Interprétation des résultats](#interprétation-des-résultats)
6. [Dépannage](#dépannage)

## Installation

### 1. Prérequis
- Python 3.10 ou supérieur
- pip installé
- Accès aux fichiers du serveur Minecraft

### 2. Installation des dépendances

```bash
cd /Users/thononpierre/Documents/Windsurf/CascadeProjects/windsurf-project/minecraft-resource-finder

# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## Configuration

### Récupérer les fichiers du serveur Hostinger (Docker)

**Important** : Votre serveur Minecraft tourne dans un **conteneur Docker** sur Hostinger. Les fichiers sont stockés dans un volume Docker nommé `minecraft_data`.

#### 📍 Emplacement des fichiers

Dans le conteneur Docker :
```
/data/world/region/     ← Les fichiers .mca sont ici !
```

Sur l'hôte (volume Docker) :
```
/var/lib/docker/volumes/minecraft_data/_data/world/region/
```

---

#### Option 1: SSH + Docker Copy (Recommandé) ✅

**Étape 1 : Se connecter au VPS**
```bash
ssh user@votre-serveur-hostinger.com
```

**Étape 2 : Vérifier que le conteneur est en cours d'exécution**
```bash
docker ps | grep minecraft
# Vous devriez voir : minecraft-server
```

**Étape 3 : Copier localement les fichiers depuis le conteneur**
```bash
# Sur le serveur, créer un dossier temporaire
mkdir -p ~/minecraft-backup

# Copier depuis le conteneur vers l'hôte
docker cp minecraft-server:/data/world/region ~/minecraft-backup/

# Compresser pour le transfert
cd ~/minecraft-backup
tar -czf minecraft-region.tar.gz region/
```

**Étape 4 : Télécharger sur votre Mac**
```bash
# Sur votre Mac (dans un nouveau terminal)
cd /Users/thononpierre/Documents/Windsurf/CascadeProjects/windsurf-project/minecraft-resource-finder

# Télécharger l'archive
scp user@votre-serveur-hostinger.com:~/minecraft-backup/minecraft-region.tar.gz .

# Extraire
tar -xzf minecraft-region.tar.gz -C ./world/

# Vérifier
ls -lh ./world/region/*.mca
```

---

#### Option 2: Script Automatisé One-Shot 🚀

Créez un script `sync_from_hostinger.sh` dans le projet :

```bash
#!/bin/bash
# Synchronisation depuis Hostinger Docker

# ⚠️ CONFIGURATION - À PERSONNALISER
VPS_HOST="votre-serveur-hostinger.com"
VPS_USER="votre-user"
CONTAINER_NAME="minecraft-server"

# Couleurs
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "  Synchronisation Minecraft (Docker)"
echo "=========================================="
echo ""

# Créer dossier local
mkdir -p ./world/region

echo -e "${CYAN}📡 Connexion au serveur...${NC}"
echo "Host: $VPS_HOST"
echo ""

# Étape 1: Copier depuis le conteneur vers l'hôte
echo -e "${CYAN}📦 Copie depuis le conteneur Docker...${NC}"
ssh "$VPS_USER@$VPS_HOST" << 'ENDSSH'
mkdir -p ~/minecraft-backup
docker cp minecraft-server:/data/world/region ~/minecraft-backup/
echo "✓ Fichiers copiés sur l'hôte"
ENDSSH

# Étape 2: Télécharger vers votre Mac
echo ""
echo -e "${CYAN}⬇️  Téléchargement vers Mac...${NC}"
rsync -avz --progress "$VPS_USER@$VPS_HOST:~/minecraft-backup/region/" "./world/region/"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Synchronisation réussie !${NC}"
    
    FILE_COUNT=$(ls -1 ./world/region/*.mca 2>/dev/null | wc -l | xargs)
    echo ""
    echo "Fichiers téléchargés : $FILE_COUNT"
    
    SIZE=$(du -sh ./world/region 2>/dev/null | cut -f1)
    echo "Taille totale : $SIZE"
    echo ""
    echo "Prêt à analyser !"
    echo "Commande : python src/main.py --world-path ./world --resource diamond --generate-map"
else
    echo ""
    echo "❌ Erreur lors de la synchronisation"
    exit 1
fi

# Nettoyage sur le serveur
echo ""
echo -e "${YELLOW}🧹 Nettoyage du serveur...${NC}"
ssh "$VPS_USER@$VPS_HOST" "rm -rf ~/minecraft-backup"
echo "✓ Nettoyage terminé"
echo ""
```

**Utilisation** :
```bash
# Rendre exécutable
chmod +x sync_from_hostinger.sh

# Personnaliser le script avec vos identifiants
nano sync_from_hostinger.sh

# Lancer la synchronisation
./sync_from_hostinger.sh
```

---

#### Option 3: Commande Directe (Une seule ligne)

```bash
ssh user@votre-serveur-hostinger.com "docker cp minecraft-server:/data/world/region /tmp/mc-region && tar -czf - /tmp/mc-region" | tar -xzf - -C ./world/ --strip-components=2
```

---

#### Option 4: Panel Hostinger + SFTP

Si SSH n'est pas disponible :

1. **Se connecter au panel Hostinger**
2. **Accéder au terminal web** ou **File Manager**
3. **Exécuter dans le terminal** :
   ```bash
   docker cp minecraft-server:/data/world/region ~/public_html/minecraft-backup/
   ```
4. **Télécharger via SFTP** :
   ```bash
   # Sur votre Mac
   sftp user@votre-serveur-hostinger.com
   get -r public_html/minecraft-backup/region ./world/
   ```

---

### ⚠️ Notes Importantes

- **Le conteneur doit être en cours d'exécution** pour pouvoir copier les fichiers
- Les fichiers sont **copiés** (snapshot), pas synchronisés en temps réel
- Pour avoir les **dernières données**, relancez la copie avant chaque analyse
- Le volume Docker `minecraft_data` est **persistant** même si le conteneur est recréé
- **Taille typique** : 50-500 MB selon la taille du monde exploré

### ✅ Vérification après téléchargement

```bash
# Vérifier que les fichiers sont présents
ls -lh ./world/region/*.mca

# Compter les fichiers de région
ls -1 ./world/region/*.mca | wc -l

# Vérifier la structure
tree -L 2 ./world/
```

Vous devriez voir des fichiers nommés comme `r.0.0.mca`, `r.-1.2.mca`, etc.

## Utilisation de base

### Commande simple

```bash
python src/main.py --world-path ./world --resource diamond
```

Cette commande va :
- ✅ Scanner tout le monde
- ✅ Trouver tous les diamants
- ✅ Afficher un résumé dans la console

### Avec génération de carte

```bash
python src/main.py --world-path ./world --resource diamond --generate-map
```

Résultat : Une carte PNG sera créée dans `output/maps/`

### Avec statistiques détaillées

```bash
python src/main.py --world-path ./world --resource diamond --stats
```

Affiche :
- Distribution par hauteur
- Top des zones riches
- Centre géométrique
- Densité globale

## Options avancées

### Analyser une zone spécifique

```bash
# Zone de chunks (chaque chunk = 16x16 blocs)
python src/main.py --world-path ./world --resource diamond \
  --x-range -10 10 \
  --z-range -10 10
```

Cela analyse une zone de 20x20 chunks (320x320 blocs) centrée sur l'origine.

### Filtrer par hauteur

```bash
# Chercher uniquement dans les couches profondes
python src/main.py --world-path ./world --resource diamond \
  --y-range -64 -32
```

### Générer tous les outputs

```bash
python src/main.py --world-path ./world --resource diamond \
  --generate-map \
  --heatmap \
  --height-chart \
  --export-json output/data/diamonds.json \
  --include-locations \
  --stats
```

Cela génère :
- 🗺️ Carte 2D avec zones riches
- 🌡️ Heatmap de densité
- 📈 Graphique de distribution par hauteur
- 💾 Fichier JSON avec toutes les données
- 📊 Statistiques complètes dans la console

### Carte à un Y-level spécifique

```bash
# Carte au niveau Y=-54 (optimal pour diamants)
python src/main.py --world-path ./world --resource diamond \
  --generate-map \
  --y-level -54
```

### Autres ressources

```bash
# Fer
python src/main.py --world-path ./world --resource iron --generate-map

# Or
python src/main.py --world-path ./world --resource gold --generate-map

# Émeraudes (montagnes uniquement)
python src/main.py --world-path ./world --resource emerald --generate-map
```

Ressources disponibles :
- `diamond` : Diamant
- `iron` : Fer
- `gold` : Or
- `copper` : Cuivre
- `coal` : Charbon
- `lapis` : Lapis-lazuli
- `redstone` : Redstone
- `emerald` : Émeraude

## Interprétation des résultats

### Console

```
💎 Total trouvé: 142 diamants

📊 Distribution par hauteur:
   • Y moyen: -52.34
   • Y le plus fréquent: -54 (23 blocs)
   • Plage: Y -64 à -12

   Top 3 tranches:
   • Y -64 à -49: 89 blocs (62.7%)
   • Y -48 à -33: 42 blocs (29.6%)
   • Y -32 à -17: 11 blocs (7.7%)

🎯 Zones riches: 3 détectées

   Top 3 zones:
   1. X=234, Z=-567: 18 blocs (rayon 32m)
   2. X=-123, Z=456: 14 blocs (rayon 32m)
   3. X=789, Z=123: 12 blocs (rayon 32m)

📍 Centre géométrique: X=234.56, Z=-123.45
```

**Interprétation** :
- La majorité des diamants (62.7%) sont entre Y -64 et -49 ✓
- La zone la plus riche est à X=234, Z=-567 → Aller creuser là !
- 18 diamants dans un rayon de 32 blocs = excellent spot

### Carte 2D

- **Points cyan** : Emplacements des diamants
- **Cercles jaunes** : Top 5 des zones riches
- **Fond gris foncé** : Terrain standard

### Heatmap

- **Bleu foncé** : Peu de ressources
- **Jaune/Orange** : Densité moyenne
- **Rouge** : Zones très riches → Priorité !

### Export JSON

Structure du fichier JSON :
```json
{
  "ressource": "diamond",
  "total_blocs": 142,
  "timestamp": "2025-10-15T11:30:00",
  "distribution_hauteur": { ... },
  "zones_riches": { ... },
  "statistiques_spatiales": { ... },
  "emplacements": [
    {
      "x": 234,
      "y": -54,
      "z": -567,
      "block_id": "minecraft:deepslate_diamond_ore"
    },
    ...
  ]
}
```

## Dépannage

### Erreur : "Le chemin ... n'existe pas"
- Vérifier que le chemin vers le monde est correct
- S'assurer que le dossier `region/` existe dans le monde

### Erreur : "Aucun fichier de région trouvé"
- Le dossier world doit contenir un sous-dossier `region/`
- Structure attendue : `world/region/*.mca`

### Aucune ressource trouvée
- Vérifier la version de Minecraft (l'outil supporte 1.13+)
- Essayer d'élargir la zone de recherche
- Vérifier que le monde contient bien des ressources générées

### L'analyse est très lente
- Réduire la zone avec `--x-range` et `--z-range`
- Le serveur VPS peut avoir beaucoup de régions générées
- Utiliser `--no-progress` pour éviter l'overhead de la barre

### Erreur de mémoire
- Le monde est trop grand, analyser par zones
- Fermer d'autres applications
- Augmenter la RAM disponible

### Les cartes sont vides ou incorrectes
- Vérifier le Y-level avec `--y-level`
- Les diamants sont entre Y -64 et Y 16
- Essayer sans spécifier de Y-level pour voir tous les niveaux

## Conseils d'utilisation

### Pour aider votre fils

1. **Première analyse complète**
```bash
python src/main.py --world-path ./world --resource diamond \
  --generate-map --heatmap --stats
```

2. **Analyser la zone autour de sa base**
```bash
# Si sa base est à X=1000, Z=2000
# Analyser les chunks autour (1 chunk = 16 blocs)
# X=1000 → chunk 62, chercher de 52 à 72 (± 10 chunks = ± 160 blocs)
python src/main.py --world-path ./world --resource diamond \
  --x-range 52 72 \
  --z-range 115 135 \
  --generate-map --stats
```

3. **Trouver le meilleur spot proche**
- Regarder les zones riches dans les stats
- Utiliser la heatmap pour visualiser
- Donner les coordonnées exactes depuis le JSON

### Automatisation

Créer un script shell `scan_resources.sh` :
```bash
#!/bin/bash

WORLD_PATH="./world"

echo "Scanning diamond..."
python src/main.py --world-path $WORLD_PATH --resource diamond --generate-map --stats

echo "Scanning iron..."
python src/main.py --world-path $WORLD_PATH --resource iron --generate-map

echo "Scanning gold..."
python src/main.py --world-path $WORLD_PATH --resource gold --generate-map

echo "Done!"
```

Rendre exécutable et lancer :
```bash
chmod +x scan_resources.sh
./scan_resources.sh
```

## Support

Pour des questions ou problèmes :
- Vérifier d'abord la section Dépannage
- Consulter le README.md principal
- Regarder les exemples de sortie

Bon minage ! ⛏️💎
