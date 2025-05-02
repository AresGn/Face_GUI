#!/usr/bin/env python3
"""
Script pour configurer DroidCam comme source de caméra
"""
import sys
import os

# Assurez-vous que le répertoire src est dans le PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.camera_config import configure_droidcam, list_available_cameras, set_default_camera

def main():
    print("=== Configuration de la source vidéo ===")
    print("\n1. Utiliser DroidCam (smartphone Android/iOS)")
    print("2. Utiliser la webcam du PC")
    print("3. Afficher les caméras disponibles")
    print("4. Quitter")
    
    choice = input("\nVotre choix (1-4): ").strip()
    
    if choice == "1":
        configure_droidcam_option()
    elif choice == "2":
        configure_webcam_option()
    elif choice == "3":
        show_available_cameras()
    elif choice == "4":
        print("Configuration annulée.")
        return
    else:
        print("Choix non valide. Veuillez réessayer.")
        main()

def configure_droidcam_option():
    print("\n=== Configuration de DroidCam ===")
    print("Veuillez installer et ouvrir l'application DroidCam sur votre smartphone.")
    print("Assurez-vous que votre smartphone et votre PC sont connectés au même réseau Wi-Fi.")
    
    ip_address = input("\nEntrez l'adresse IP affichée dans l'application DroidCam: ").strip()
    port = input("Entrez le port (4747 par défaut): ").strip() or "4747"
    
    try:
        port = int(port)
        success, message = configure_droidcam(ip_address, port, True)
        
        if success:
            print(f"\nSuccès: {message}")
            print("DroidCam est maintenant configuré comme source vidéo.")
            print("Redémarrez l'application pour appliquer les changements.")
        else:
            print(f"\nÉchec: {message}")
            print("Vérifiez que:")
            print("- L'application DroidCam est ouverte sur votre smartphone")
            print("- L'adresse IP et le port sont corrects")
            print("- Votre smartphone et votre PC sont sur le même réseau Wi-Fi")
            configure_droidcam_option()
    except ValueError:
        print("\nErreur: Le port doit être un nombre entier.")
        configure_droidcam_option()

def configure_webcam_option():
    print("\n=== Configuration de la webcam du PC ===")
    
    # Afficher les caméras disponibles
    available_cameras = list_available_cameras()
    
    if not available_cameras:
        print("Aucune caméra n'a été détectée sur votre PC.")
        return
    
    print("\nCaméras disponibles:")
    for idx in available_cameras:
        print(f"- Caméra {idx}")
    
    camera_idx = input("\nEntrez l'indice de la caméra à utiliser (0 par défaut): ").strip() or "0"
    
    try:
        camera_idx = int(camera_idx)
        success, message = set_default_camera(camera_idx)
        
        if success:
            print(f"\nSuccès: {message}")
            print("La webcam du PC est maintenant configurée comme source vidéo.")
            print("Redémarrez l'application pour appliquer les changements.")
        else:
            print(f"\nÉchec: {message}")
            configure_webcam_option()
    except ValueError:
        print("\nErreur: L'indice de la caméra doit être un nombre entier.")
        configure_webcam_option()

def show_available_cameras():
    print("\n=== Caméras disponibles ===")
    
    available_cameras = list_available_cameras()
    
    if not available_cameras:
        print("Aucune caméra n'a été détectée sur votre PC.")
    else:
        print("\nCaméras détectées:")
        for idx in available_cameras:
            print(f"- Caméra {idx}")
    
    input("\nAppuyez sur Entrée pour revenir au menu principal...")
    main()

if __name__ == "__main__":
    print("=== Utilitaire de configuration de la caméra ===")
    main() 