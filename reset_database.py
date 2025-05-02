#!/usr/bin/env python3
"""
Script pour réinitialiser la base de données et le jeu de données
"""
import sys
import os

# Assurez-vous que le répertoire src est dans le PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.reset_db import reset_database

if __name__ == "__main__":
    print("ATTENTION: Cette opération va supprimer toutes les données de la base de données!")
    print("Toutes les données des employés, les images de visage et les présences seront effacées.")
    confirmation = input("Êtes-vous sûr de vouloir continuer? (oui/non): ").strip().lower()
    
    if confirmation == "oui":
        success, message = reset_database()
        print(message)
        
        if success:
            print("La base de données a été réinitialisée avec succès.")
            print("Vous pouvez maintenant redémarrer l'application.")
        else:
            print("Une erreur s'est produite lors de la réinitialisation de la base de données.")
            print("Veuillez vérifier les journaux pour plus d'informations.")
    else:
        print("Opération annulée. La base de données reste inchangée.") 