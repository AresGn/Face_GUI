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

:: Lancer l'application PyQt5
echo Lancement de l'application...
python app-gui-qt.py

:: Si l'application se termine avec une erreur
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors de l'exécution de l'application.
    pause
)

:: Désactiver l'environnement virtuel
call deactivate
exit /b 0 