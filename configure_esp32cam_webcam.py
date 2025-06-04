#!/usr/bin/env python3
"""
Configuration rapide ESP32-CAM comme webcam
"""

import sys
import os

# Ajouter le répertoire src au PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import config
from src.utils.camera_config import list_available_cameras

def configure_esp32cam_as_webcam():
    """Configure l'ESP32-CAM comme webcam par défaut"""
    print("🔧 Configuration ESP32-CAM comme webcam...")
    
    # Détecter les caméras disponibles
    cameras = list_available_cameras()
    print(f"📷 Caméras détectées: {cameras}")
    
    if not cameras:
        print("❌ Aucune caméra détectée")
        return False
    
    # Utiliser la première caméra (index 0) qui devrait être l'ESP32-CAM
    esp32_index = cameras[0]
    
    # Configurer comme webcam par défaut
    config.set('camera.use_droid_cam', False)
    config.set('camera.use_esp32_cam', False)  # Désactiver le mode Wi-Fi
    config.set('camera.index', esp32_index)
    
    print(f"✅ ESP32-CAM configuré comme webcam à l'index {esp32_index}")
    print("💾 Configuration sauvegardée")
    
    return True

def show_current_config():
    """Affiche la configuration actuelle"""
    print("\n📋 Configuration actuelle:")
    print(f"   - use_droid_cam: {config.get('camera.use_droid_cam', False)}")
    print(f"   - use_esp32_cam: {config.get('camera.use_esp32_cam', False)}")
    print(f"   - camera.index: {config.get('camera.index', 0)}")

if __name__ == "__main__":
    print("=" * 50)
    print("⚙️ CONFIGURATION ESP32-CAM WEBCAM")
    print("=" * 50)
    
    show_current_config()
    
    print("\n" + "-" * 50)
    
    if configure_esp32cam_as_webcam():
        print("\n" + "-" * 50)
        show_current_config()
        
        print("\n🎉 Configuration terminée !")
        print("💡 Redémarrez l'application pour voir les changements")
    else:
        print("\n❌ Échec de la configuration")
