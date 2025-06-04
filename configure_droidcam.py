#!/usr/bin/env python3
"""
Script pour configurer DroidCam comme source de caméra
"""
import sys
import os

# Assurez-vous que le répertoire src est dans le PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.camera_config import (configure_droidcam, list_available_cameras, set_default_camera,
                                    configure_esp32cam, test_esp32cam_connection, get_esp32cam_info)

def main():
    print("=== Configuration de la source vidéo ===")
    print("\n1. Utiliser DroidCam (smartphone Android/iOS)")
    print("2. Utiliser ESP32-CAM (module caméra Wi-Fi)")
    print("3. Utiliser la webcam du PC")
    print("4. Afficher les caméras disponibles")
    print("5. Quitter")

    choice = input("\nVotre choix (1-5): ").strip()

    if choice == "1":
        configure_droidcam_option()
    elif choice == "2":
        configure_esp32cam_option()
    elif choice == "3":
        configure_webcam_option()
    elif choice == "4":
        show_available_cameras()
    elif choice == "5":
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

def configure_esp32cam_option():
    """Configuration de l'ESP32-CAM"""
    print("\n=== Configuration ESP32-CAM ===")
    print("Assurez-vous que votre ESP32-CAM est connecté au même réseau Wi-Fi")
    print("et que le firmware ESP32-CAM_FaceRecognition.ino est installé.")

    # Demander l'adresse IP
    ip_address = input("\nAdresse IP de l'ESP32-CAM (ex: 192.168.1.100): ").strip()
    if not ip_address:
        print("Adresse IP requise.")
        return

    # Demander le port (optionnel)
    port_input = input("Port (défaut: 80): ").strip()
    port = 80
    if port_input:
        try:
            port = int(port_input)
        except ValueError:
            print("Port invalide, utilisation du port 80 par défaut.")
            port = 80

    # Demander le chemin du flux (optionnel)
    stream_path = input("Chemin du flux (défaut: /stream): ").strip()
    if not stream_path:
        stream_path = "/stream"

    # Demander la qualité JPEG (optionnel)
    quality_input = input("Qualité JPEG 1-63 (défaut: 10, plus bas = meilleure qualité): ").strip()
    quality = 10
    if quality_input:
        try:
            quality = int(quality_input)
            if quality < 1 or quality > 63:
                print("Qualité invalide, utilisation de 10 par défaut.")
                quality = 10
        except ValueError:
            print("Qualité invalide, utilisation de 10 par défaut.")
            quality = 10

    print(f"\nTest de connexion à l'ESP32-CAM...")
    print(f"URL: http://{ip_address}:{port}{stream_path}")

    # Tester la connexion
    success, message = test_esp32cam_connection(ip_address, port, stream_path)

    if success:
        print(f"✓ {message}")

        # Demander confirmation
        confirm = input("\nVoulez-vous enregistrer cette configuration ? (o/N): ").strip().lower()
        if confirm in ['o', 'oui', 'y', 'yes']:
            success, message = configure_esp32cam(ip_address, port, stream_path, quality, True)
            if success:
                print(f"✓ Configuration ESP32-CAM enregistrée avec succès!")
                print(f"  - IP: {ip_address}")
                print(f"  - Port: {port}")
                print(f"  - Flux: {stream_path}")
                print(f"  - Qualité: {quality}")
            else:
                print(f"✗ Erreur lors de l'enregistrement: {message}")
        else:
            print("Configuration annulée.")
    else:
        print(f"✗ {message}")
        print("\nVérifiez que:")
        print("- L'ESP32-CAM est allumé et connecté au Wi-Fi")
        print("- L'adresse IP est correcte")
        print("- Le firmware ESP32-CAM_FaceRecognition.ino est installé")
        print("- Votre PC et l'ESP32-CAM sont sur le même réseau")

    input("\nAppuyez sur Entrée pour continuer...")
    main()

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