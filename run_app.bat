@echo off
echo Demarrage de l'application de reconnaissance faciale...
echo Activation de l'environnement Python...

:: Activer l'environnement virtuel
call venv\Scripts\activate.bat

:: Vérifier si l'activation a réussi
if %ERRORLEVEL% NEQ 0 (
    echo Erreur: Impossible d'activer l'environnement virtuel.
    echo Assurez-vous que l'environnement virtuel existe dans le dossier "venv".
    pause
    exit /b 1
)

:: Installer les packages de base
echo Installation des dépendances de base...
pip install python-docx pandas openpyxl

:: Installer PyQt5 avec des options spécifiques pour éviter les erreurs de compilation
echo Installation de PyQt5 (version binaire)...
pip install --only-binary=:all: PyQt5==5.15.9 PyQt5-Qt5==5.15.2 PyQt5-sip==12.12.2

:: Lancer l'application PyQt5
echo Lancement de l'application...
python src/app.py

:: Si l'application se termine avec une erreur
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors de l'exécution de l'application.
    pause
)

:: Désactiver l'environnement virtuel
call deactivate
exit /b 0 