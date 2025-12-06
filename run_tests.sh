#!/bin/bash
# Script pour lancer les tests unitaires DYAG sous Linux/Mac

echo "========================================"
echo "Tests Unitaires DYAG"
echo "========================================"
echo ""

# Vérifier si Poetry est installé
if command -v poetry &> /dev/null; then
    echo "[INFO] Utilisation de Poetry pour lancer les tests"
    echo ""

    # Demander quel type de test lancer
    echo "Choisissez une option:"
    echo "1. Lancer tous les tests"
    echo "2. Lancer les tests avec couverture"
    echo "3. Lancer les tests en mode verbeux"
    echo "4. Lancer les tests avec couverture HTML"
    echo ""

    read -p "Votre choix (1-4): " choice
    echo ""

    case $choice in
        1)
            echo "[INFO] Lancement de tous les tests..."
            poetry run pytest
            ;;
        2)
            echo "[INFO] Lancement des tests avec couverture..."
            poetry run pytest --cov=src/dyag --cov-report=term-missing
            ;;
        3)
            echo "[INFO] Lancement des tests en mode verbeux..."
            poetry run pytest -v
            ;;
        4)
            echo "[INFO] Lancement des tests avec couverture HTML..."
            poetry run pytest --cov=src/dyag --cov-report=html
            echo ""
            echo "[INFO] Rapport de couverture généré dans htmlcov/index.html"
            echo "[INFO] Ouverture du rapport..."

            # Ouvrir le rapport dans le navigateur par défaut
            if command -v xdg-open &> /dev/null; then
                xdg-open htmlcov/index.html
            elif command -v open &> /dev/null; then
                open htmlcov/index.html
            else
                echo "[INFO] Veuillez ouvrir manuellement htmlcov/index.html"
            fi
            ;;
        *)
            echo "[ERREUR] Choix invalide"
            exit 1
            ;;
    esac
else
    echo "[AVERTISSEMENT] Poetry n'est pas installé"
    echo "[INFO] Tentative d'utilisation de pytest directement..."
    echo ""

    if command -v pytest &> /dev/null; then
        echo "[INFO] Pytest trouvé, lancement des tests..."
        pytest
    else
        echo "[ERREUR] Pytest n'est pas installé"
        echo "[INFO] Installez les dépendances avec:"
        echo "  poetry install --with dev"
        echo "ou"
        echo "  pip install pytest pytest-cov pytest-mock"
        exit 1
    fi
fi

echo ""
echo "========================================"
echo "Tests terminés"
echo "========================================"
