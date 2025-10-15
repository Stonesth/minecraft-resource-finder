# Minecraft Resource Finder

## Description
Outil d'analyse des fichiers de région Minecraft pour détecter et cartographier les ressources (diamants, minerais, etc.) avec génération de cartes et statistiques.

## Objectifs
- ✅ **Phase 1** : Détection des filons de diamants
- 🔜 **Phase 2** : Extension à d'autres ressources (fer, or, redstone, émeraudes, etc.)
- 🔮 **Phase 3** : Statistiques avancées et heatmaps
- 🔮 **Phase 4** : Interface graphique (optionnel)

## Statut
✅ **Fonctionnel** - Détection de minerais opérationnelle avec précision de ±1-2 blocs

## Configuration
- **Minecraft Version** : Java Edition 1.21.9 (supporté)
- **Format de monde** : Anvil (fichiers .mca)
- **Environnement** : Serveur multijoueur (VPS Hostinger + Docker)
- **Précision** : ±1-2 blocs (validée sur 12 positions réelles)
- **Plateforme** : macOS (compatible Linux)

## Fonctionnalités

### ✅ Opérationnel
- ✅ **Détection de minerais** : Diamant, Or, Fer, Cuivre, Lapis, Redstone, Charbon, Émeraude
- ✅ **Précision** : ±1-2 blocs (formule validée : `x + z*16 + y*256`)
- ✅ **Synchronisation auto** : Script SSH avec mot de passe sécurisé
- ✅ **Scripts optimisés** : 
  - `find_diamonds_around.py` - Trouve les diamants par distance
  - `find_all_ores_around.py` - Scanner tous les minerais
  - `generate_ore_map_html.py` - Carte HTML interactive
- ✅ **Format Minecraft 1.21** : Décodage compact sans chevauchement

## Architecture Technique

### Approche
**Analyse hors-ligne des fichiers de région** avec parsing NBT custom pour Minecraft 1.21.

### Technologies
- **Langage** : Python 3.12+
- **Parsing NBT** : `nbt` + décodage custom
- **Format** : Support Minecraft 1.21 (format compact)
- **Synchronisation** : `rsync` + `sshpass` (optionnel)
- **Docker** : Support conteneur minecraft-server

### Algorithme de décodage

**Formule validée** : `indice = x + z*16 + y*256`

Minecraft 1.21 utilise un format "compact" où :
- Chaque `long` (64 bits) contient un nombre **entier** de blocs
- Pas de chevauchement entre longs
- `blocks_per_long = 64 // bits_per_block`
- Ordre des coordonnées : **X-Z-Y** (X varie le plus vite)

### Structure du Projet
```
minecraft-resource-finder/
├── README.md              # Documentation principale
├── Q&A.md                 # Questions/réponses de planification
├── requirements.txt       # Dépendances Python
├── .gitignore            # Fichiers à ignorer
├── src/
│   ├── __init__.py
│   ├── main.py           # Point d'entrée principal
│   ├── region_reader.py  # Lecture des fichiers de région
│   ├── resource_finder.py # Détection des ressources
│   ├── map_generator.py  # Génération de cartes
│   ├── statistics.py     # Calcul des statistiques
│   └── config.py         # Configuration
├── output/               # Dossier pour les cartes générées
│   ├── maps/
│   └── data/
├── tests/                # Tests unitaires
│   └── __init__.py
└── docs/                 # Documentation détaillée
    └── usage.md
```

## Installation

### Prérequis
- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)
- Accès aux fichiers de région du serveur Minecraft

### Étapes

1. **Cloner ou naviguer vers le projet**
```bash
cd /Users/thononpierre/Documents/Windsurf/CascadeProjects/windsurf-project/minecraft-resource-finder
```

2. **Créer un environnement virtuel (recommandé)**
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

## Utilisation

### Démarrage rapide

**1. Synchroniser le monde**
```bash
./sync_from_server.sh
```

**2. Trouver des diamants**
```bash
python3 find_diamonds_around.py
# Résultat: X=-72, Y=5, Z=24 (1.0m) 💎
```

**3. Scanner tous les minerais**
```bash
python3 find_all_ores_around.py
# 5570 minerais trouvés : Cuivre, Charbon, Fer, Diamant...
```

**4. Générer une carte HTML**
```bash
python3 generate_ore_map_html.py
# Ouvrir: output/carte_minerais.html
```

### Configuration SSH automatique

```bash
# Une seule fois
cp server_config.sh.example server_config.sh
nano server_config.sh  # Coller votre mot de passe
chmod 600 server_config.sh

# Installer sshpass
brew install hudochenkov/sshpass/sshpass

# Synchroniser sans mot de passe
./sync_from_server.sh
```

📚 **Guide complet** : `docs/SSH_CONFIG.md`

### Exemples de sortie

**Console** :
```
📊 RECHERCHE DE DIAMANTS AUTOUR DE X=-71, Z=24
   Rayon de recherche: 64 blocs

✓ 81 chunks scannés
💎 660 diamant(s) trouvé(s) !

📍 COORDONNÉES DES DIAMANTS (triées par distance)
  1. 💎 X= -72, Y=  5, Z=  24  (distance: 1.0m)
  2. ◇ X= -72, Y=  6, Z=  24  (distance: 1.0m)
  3. ◇ X= -72, Y=  5, Z=  23  (distance: 1.4m)

📊 STATISTIQUES
💎 Plus proche: X=-72, Y=5, Z=24 (1.0m)
📍 Hauteur la plus fréquente: Y=-51 (35 diamants)
📏 Hauteur moyenne: Y=-35.9

🎯 CONSEIL DE MINAGE
Allez à X=-72, Z=24, Y=5
C'est le diamant le plus proche (1.0 blocs) !
```

**Précision validée** : ±1-2 blocs sur 12 positions testées

## Roadmap

### ✅ Phase 1 - Détection de base (TERMINÉE)
- [x] Architecture du projet
- [x] Parsing NBT Minecraft 1.21
- [x] Décodage format compact
- [x] Détection de tous les minerais
- [x] Formule de coordonnées validée
- [x] Précision ±1-2 blocs confirmée
- [x] Scripts utilisables (diamants, tous minerais)
- [x] Synchronisation SSH automatique
- [x] Organisation du code (tests/, scripts/)

### 🔄 Phase 2 - Améliorations (EN COURS)
- [x] Carte HTML interactive
- [ ] Filtrage par hauteur (Y-level)
- [ ] Export JSON des coordonnées
- [ ] Heatmap de densité

### 🔮 Phase 3 - Avancé (FUTUR)
- [ ] Interface web complète
- [ ] Mode surveillance (watch)
- [ ] Intégration Discord
- [ ] Analyse de biomes
- [ ] Prédiction de zones riches par ML

## Contribution
Projet personnel pour aider sur le serveur familial.

## Notes Techniques

### Format des fichiers de région
- Extension : `.mca` (Minecraft Anvil)
- Contient : 32x32 chunks
- Chaque chunk : 16x384x16 blocs (hauteur -64 à +320 en 1.21)

### Performance
- Analyse typique : ~25-50 chunks/seconde (décodage NBT)
- Scanner 81 chunks : ~2-3 secondes
- RAM nécessaire : ~200-500MB
- Précision : ±1-2 blocs (validée)

### Résultats de validation

Test sur 12 positions réelles :
- Formule : `x + z*16 + y*256`
- Distance moyenne : **2.01m**
- Précision : 9/12 à ≤1.7m
- Meilleurs résultats : 1.0m

## Licence
Usage personnel
