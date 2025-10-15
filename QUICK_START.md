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

### Via SFTP/rsync (recommandé)

```bash
# Remplacer par vos informations de connexion
rsync -avz --progress user@votre-vps-hostinger.com:/chemin/vers/minecraft/world/region ./world/
```

### Via panel Hostinger
1. Aller sur le panel Hostinger
2. File Manager → Dossier Minecraft
3. Télécharger `world/region/` localement
4. Déplacer dans `./world/region/`

## Première utilisation

### Trouver des diamants

```bash
# Analyse simple
python src/main.py --world-path ./world --resource diamond

# Avec carte
python src/main.py --world-path ./world --resource diamond --generate-map

# Analyse complète
python src/main.py --world-path ./world --resource diamond \
  --generate-map --heatmap --height-chart --stats
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
./example_scan.sh
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
# Voir toutes les options
python src/main.py --help

# Ressources disponibles
diamond, iron, gold, copper, coal, lapis, redstone, emerald
```

## Problèmes fréquents

**"Aucun fichier de région trouvé"**
→ Vérifier que `world/region/*.mca` existe

**"Aucune ressource trouvée"**
→ Essayer sans `--y-level` ou élargir la zone

**Lent**
→ Utiliser `--x-range` et `--z-range` pour limiter la zone

## Prochaines étapes

📚 Documentation complète : `docs/usage.md`
📖 Architecture : `README.md`

Bon minage ! ⛏️💎
