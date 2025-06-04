#!/usr/bin/env python3
"""
Configuration rapide de la caméra 1 comme ESP32-CAM
"""

import sys
import os
import cv2

# Ajouter le répertoire src au PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import config

def configure_camera1_as_esp32cam():
    """Configure la caméra 1 comme ESP32-CAM"""
    print("🔧 Configuration de la caméra 1 comme ESP32-CAM...")
    
    # Tester d'abord la caméra 1
    try:
        cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            print("❌ Impossible d'ouvrir la caméra 1")
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if ret and frame is not None:
            height, width = frame.shape[:2]
            print(f"✅ Caméra 1 accessible: {width}x{height}")
            
            # Sauvegarder une image de test
            os.makedirs("test_final", exist_ok=True)
            cv2.imwrite("test_final/esp32cam_camera1_test.jpg", frame)
            print("📁 Image de test sauvée: test_final/esp32cam_camera1_test.jpg")
        else:
            print("❌ Impossible de capturer une image de la caméra 1")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test de la caméra 1: {e}")
        return False
    
    # Configurer dans le système
    try:
        config.set('camera.use_droid_cam', False)
        config.set('camera.use_esp32_cam', False)
        config.set('camera.index', 1)
        
        print("✅ Configuration mise à jour:")
        print("   - use_droid_cam: False")
        print("   - use_esp32_cam: False") 
        print("   - camera.index: 1")
        print("💾 Configuration sauvegardée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la configuration: {e}")
        return False

def test_live_preview():
    """Test avec aperçu en direct"""
    print("\n🎥 Test avec aperçu en direct de la caméra 1...")
    print("   Appuyez sur 'q' pour quitter")
    
    try:
        cap = cv2.VideoCapture(1)
        
        if not cap.isOpened():
            print("❌ Impossible d'ouvrir la caméra 1")
            return False
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            
            if ret:
                frame_count += 1
                
                cv2.putText(frame, f"ESP32-CAM Camera 1 - Frame {frame_count}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Appuyez sur 'q' pour quitter", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                cv2.imshow('ESP32-CAM Test - Camera 1', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("⚠️ Pas de frame")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"✅ Test terminé ({frame_count} frames)")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("=" * 50)
    print("🎯 CONFIGURATION CAMÉRA 1 COMME ESP32-CAM")
    print("=" * 50)
    
    # Configuration
    if configure_camera1_as_esp32cam():
        print("\n" + "=" * 50)
        
        # Test optionnel
        test_choice = input("Voulez-vous faire un test avec aperçu en direct ? (o/N): ").strip().lower()
        if test_choice in ['o', 'oui', 'y', 'yes']:
            test_live_preview()
        
        print("\n🎉 Configuration terminée !")
        print("💡 Votre ESP32-CAM est maintenant configurée à l'index 1")
        print("💡 Vous pouvez maintenant utiliser l'application de reconnaissance faciale")
        
    else:
        print("\n❌ Échec de la configuration")

if __name__ == "__main__":
    main()
