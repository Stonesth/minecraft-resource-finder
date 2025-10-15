#!/bin/bash
# Script pour synchroniser les fichiers de région depuis le serveur Hostinger (Docker)

# Configuration
VPS_HOST="82.25.117.8"
VPS_USER="root"
CONTAINER_NAME="minecraft-server"

# Couleurs
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "  Synchronisation Minecraft (Docker)"
echo "=========================================="
echo ""
echo "Serveur : $VPS_HOST"
echo "User    : $VPS_USER"
echo "Conteneur : $CONTAINER_NAME"
echo ""

# Créer le dossier de destination
mkdir -p world/region

echo -e "${CYAN}📡 Connexion au serveur...${NC}"

# Vérifier la connexion SSH
ssh -o ConnectTimeout=10 "$VPS_USER@$VPS_HOST" "echo '✓ Connexion SSH réussie'" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Impossible de se connecter au serveur${NC}"
    echo "Vérifiez votre connexion SSH"
    exit 1
fi

# Étape 1: Copier depuis le conteneur Docker vers l'hôte
echo ""
echo -e "${CYAN}📦 Copie depuis le conteneur Docker...${NC}"

ssh "$VPS_USER@$VPS_HOST" << 'ENDSSH'
# Vérifier que le conteneur existe et tourne
if ! docker ps | grep -q minecraft-server; then
    echo "❌ Le conteneur minecraft-server n'est pas en cours d'exécution"
    exit 1
fi

# Créer le dossier temporaire
mkdir -p ~/minecraft-backup

# Copier depuis le conteneur
echo "Copie depuis /data/world/region..."
docker cp minecraft-server:/data/world/region ~/minecraft-backup/

if [ $? -eq 0 ]; then
    echo "✓ Fichiers copiés sur l'hôte dans ~/minecraft-backup/region/"
else
    echo "❌ Erreur lors de la copie depuis le conteneur"
    exit 1
fi
ENDSSH

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erreur lors de la copie depuis Docker${NC}"
    exit 1
fi

# Étape 2: Télécharger vers votre Mac
echo ""
echo -e "${CYAN}⬇️  Téléchargement vers Mac...${NC}"
rsync -avz --progress "$VPS_USER@$VPS_HOST:~/minecraft-backup/region/" "./world/region/"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Synchronisation réussie !${NC}"
    
    # Compter les fichiers
    FILE_COUNT=$(ls -1 world/region/*.mca 2>/dev/null | wc -l | xargs)
    echo ""
    echo "📊 Statistiques :"
    echo "  • Fichiers téléchargés : $FILE_COUNT .mca"
    
    # Calculer la taille
    SIZE=$(du -sh world/region 2>/dev/null | cut -f1)
    echo "  • Taille totale : $SIZE"
    echo ""
    
    # Nettoyage sur le serveur
    echo -e "${YELLOW}🧹 Nettoyage du serveur...${NC}"
    ssh "$VPS_USER@$VPS_HOST" "rm -rf ~/minecraft-backup"
    echo "✓ Nettoyage terminé"
    echo ""
    
    echo -e "${GREEN}✅ Prêt à analyser !${NC}"
    echo ""
    echo "Commandes suggérées :"
    echo "  • Analyse simple     : python src/main.py --world-path ./world --resource diamond --stats"
    echo "  • Avec carte         : python src/main.py --world-path ./world --resource diamond --generate-map"
    echo "  • Analyse complète   : python src/main.py --world-path ./world --resource diamond --generate-map --heatmap --stats"
else
    echo ""
    echo -e "${RED}❌ Erreur lors de la synchronisation${NC}"
    echo ""
    echo "Vérifiez :"
    echo "  • La connexion SSH"
    echo "  • Que rsync est installé sur le serveur"
    echo "  • Les permissions d'accès"
    exit 1
fi
echo ""
