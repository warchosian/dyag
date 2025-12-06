@echo off
REM Script pour lancer les tests unitaires DYAG sous Windows

echo ========================================
echo Tests Unitaires DYAG
echo ========================================
echo.

REM Vérifier si Poetry est installé
where poetry >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Utilisation de Poetry pour lancer les tests
    echo.

    REM Demander quel type de test lancer
    echo Choisissez une option:
    echo 1. Lancer tous les tests
    echo 2. Lancer les tests avec couverture
    echo 3. Lancer les tests en mode verbeux
    echo 4. Lancer les tests avec couverture HTML
    echo.

    set /p choice="Votre choix (1-4): "
    echo.

    if "%choice%"=="1" (
        echo [INFO] Lancement de tous les tests...
        poetry run pytest
    ) else if "%choice%"=="2" (
        echo [INFO] Lancement des tests avec couverture...
        poetry run pytest --cov=src/dyag --cov-report=term-missing
    ) else if "%choice%"=="3" (
        echo [INFO] Lancement des tests en mode verbeux...
        poetry run pytest -v
    ) else if "%choice%"=="4" (
        echo [INFO] Lancement des tests avec couverture HTML...
        poetry run pytest --cov=src/dyag --cov-report=html
        echo.
        echo [INFO] Rapport de couverture généré dans htmlcov/index.html
        echo [INFO] Ouverture du rapport...
        start htmlcov\index.html
    ) else (
        echo [ERREUR] Choix invalide
        pause
        exit /b 1
    )
) else (
    echo [AVERTISSEMENT] Poetry n'est pas installé
    echo [INFO] Tentative d'utilisation de pytest directement...
    echo.

    pytest --version >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [INFO] Pytest trouvé, lancement des tests...
        pytest
    ) else (
        echo [ERREUR] Pytest n'est pas installé
        echo [INFO] Installez les dépendances avec:
        echo   poetry install --with dev
        echo ou
        echo   pip install pytest pytest-cov pytest-mock
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Tests terminés
echo ========================================
pause
