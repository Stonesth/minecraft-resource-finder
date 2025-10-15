#!/bin/bash
# Script pour recréer l'environnement avec Python 3.12

echo "=========================================="
echo "  Fix Python Version (3.13 → 3.12)"
echo "=========================================="
echo ""

# Vérifier si Python 3.12 est installé
if ! command -v python3.12 &> /dev/null; then
    echo "❌ Python 3.12 n'est pas installé"
    echo ""
    echo "Installation via Homebrew:"
    echo "  brew install python@3.12"
    echo ""
    exit 1
fi

echo "✓ Python 3.12 détecté"
echo ""

# Sauvegarder l'ancien venv
if [ -d "venv" ]; then
    echo "🗑️  Suppression de l'ancien environnement virtuel..."
    rm -rf venv
    echo "✓ Ancien venv supprimé"
fi

# Créer le nouveau venv avec Python 3.12
echo ""
echo "📦 Création du nouvel environnement avec Python 3.12..."
python3.12 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la création du venv"
    exit 1
fi

echo "✓ Environnement créé"
echo ""

# Activer et installer
echo "📚 Installation des dépendances..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dépendances installées"
    echo ""
    echo "=========================================="
    echo "  ✅ Configuration terminée !"
    echo "=========================================="
    echo ""
    echo "Prochaines étapes:"
    echo "  1. Activer l'environnement : source venv/bin/activate"
    echo "  2. Analyser : python src/main.py --world-path ./world --resource diamond --generate-map"
    echo ""
else
    echo "❌ Erreur lors de l'installation des dépendances"
    exit 1
fi
