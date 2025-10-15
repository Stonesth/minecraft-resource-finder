#!/bin/bash
# Script d'exemple pour scanner les ressources

# Configuration
WORLD_PATH="./world"
OUTPUT_DIR="./output"

# Couleurs pour le terminal
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Minecraft Resource Scanner"
echo "=========================================="
echo ""

# Vérifier que l'environnement est activé
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  L'environnement virtuel n'est pas activé"
    echo "   Exécutez : source venv/bin/activate"
    exit 1
fi

# Vérifier que le monde existe
if [ ! -d "$WORLD_PATH/region" ]; then
    echo "❌ Monde non trouvé : $WORLD_PATH"
    echo "   Placez les fichiers de région dans $WORLD_PATH/region/"
    exit 1
fi

# Scanner les diamants
echo -e "${CYAN}🔍 Analyse des diamants...${NC}"
python src/main.py --world-path $WORLD_PATH --resource diamond \
    --generate-map \
    --heatmap \
    --height-chart \
    --export-json $OUTPUT_DIR/data/diamonds.json \
    --include-locations \
    --stats

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Diamants analysés${NC}"
else
    echo "❌ Erreur lors de l'analyse des diamants"
fi
echo ""

# Scanner le fer (optionnel, décommenter si souhaité)
# echo -e "${CYAN}🔍 Analyse du fer...${NC}"
# python src/main.py --world-path $WORLD_PATH --resource iron \
#     --generate-map \
#     --export-json $OUTPUT_DIR/data/iron.json \
#     --stats

# Scanner l'or (optionnel, décommenter si souhaité)
# echo -e "${CYAN}🔍 Analyse de l'or...${NC}"
# python src/main.py --world-path $WORLD_PATH --resource gold \
#     --generate-map \
#     --export-json $OUTPUT_DIR/data/gold.json \
#     --stats

echo "=========================================="
echo "  Scan terminé ! ✅"
echo "=========================================="
echo ""
echo "Résultats disponibles dans :"
echo "  • Cartes : $OUTPUT_DIR/maps/"
echo "  • Données : $OUTPUT_DIR/data/"
echo ""
