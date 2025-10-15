#!/bin/bash
# Script d'installation et configuration du projet

echo "=========================================="
echo "  Minecraft Resource Finder - Setup"
echo "=========================================="
echo ""

# Vérifier Python
echo "🔍 Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    echo "   Installez Python 3.10+ depuis https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION détecté"
echo ""

# Créer l'environnement virtuel
echo "📦 Création de l'environnement virtuel..."
if [ -d "venv" ]; then
    echo "⚠️  L'environnement virtuel existe déjà"
    read -p "   Voulez-vous le recréer ? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✓ Environnement recréé"
    else
        echo "✓ Environnement existant conservé"
    fi
else
    python3 -m venv venv
    echo "✓ Environnement virtuel créé"
fi
echo ""

# Activer l'environnement
echo "⚡ Activation de l'environnement..."
source venv/bin/activate
echo "✓ Environnement activé"
echo ""

# Installer les dépendances
echo "📚 Installation des dépendances..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dépendances installées avec succès"
else
    echo "❌ Erreur lors de l'installation des dépendances"
    exit 1
fi
echo ""

# Créer les dossiers de sortie
echo "📁 Création des dossiers de sortie..."
mkdir -p output/maps
mkdir -p output/data
echo "✓ Dossiers créés"
echo ""

# Vérifier si un monde de test existe
echo "🌍 Vérification du monde Minecraft..."
if [ ! -d "world/region" ]; then
    echo "⚠️  Aucun monde trouvé dans ./world/region/"
    echo ""
    echo "   Pour utiliser l'outil, vous devez :"
    echo "   1. Récupérer les fichiers de région de votre serveur"
    echo "   2. Les placer dans ./world/region/"
    echo ""
    echo "   Exemple avec rsync :"
    echo "   rsync -avz user@vps:/chemin/minecraft/world/region ./world/"
    echo ""
else
    REGION_COUNT=$(ls -1 world/region/*.mca 2>/dev/null | wc -l)
    echo "✓ Monde trouvé avec $REGION_COUNT fichier(s) de région"
fi
echo ""

# Message final
echo "=========================================="
echo "  Installation terminée ! ✅"
echo "=========================================="
echo ""
echo "Prochaines étapes :"
echo ""
echo "1. Activer l'environnement :"
echo "   source venv/bin/activate"
echo ""
echo "2. Lancer une analyse :"
echo "   python src/main.py --world-path ./world --resource diamond --generate-map"
echo ""
echo "3. Consulter la documentation :"
echo "   cat docs/usage.md"
echo ""
echo "Bon minage ! ⛏️💎"
echo ""
