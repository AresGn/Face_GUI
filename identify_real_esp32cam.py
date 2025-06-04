#!/usr/bin/env python3
"""
Script pour identifier la vraie ESP32-CAM parmi les caméras détectées
Distingue entre DroidCam virtuel et ESP32-CAM physique
"""

import cv2
import numpy as np
import time
import os
from datetime import datetime

def analyze_camera_properties(camera_index):
    """Analyse les propriétés d'une caméra pour l'identifier"""
    print(f"\n🔍 Analyse de la caméra {camera_index}...")
    
    try:
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            return None
        
        # Récupérer les propriétés de la caméra
        properties = {
            'index': camera_index,
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'backend': cap.get(cv2.CAP_PROP_BACKEND),
            'fourcc': cap.get(cv2.CAP_PROP_FOURCC),
        }
        
        # Capturer quelques frames pour analyser
        frames_captured = 0
        total_brightness = 0
        is_static = True
        prev_frame = None
        
        print(f"   Propriétés: {properties['width']}x{properties['height']}, FPS: {properties['fps']:.1f}")
        
        for i in range(10):
            ret, frame = cap.read()
            if ret and frame is not None:
                frames_captured += 1
                
                # Calculer la luminosité moyenne
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = np.mean(gray)
                total_brightness += brightness
                
                # Vérifier si l'image change (pour détecter les images statiques de DroidCam)
                if prev_frame is not None:
                    diff = cv2.absdiff(gray, prev_frame)
                    if np.mean(diff) > 5:  # Seuil de changement
                        is_static = False
                
                prev_frame = gray.copy()
                
                # Sauvegarder la première frame pour inspection visuelle
                if i == 0:
                    os.makedirs("camera_analysis", exist_ok=True)
                    cv2.imwrite(f"camera_analysis/camera_{camera_index}_sample.jpg", frame)
            
            time.sleep(0.1)
        
        cap.release()
        
        if frames_captured > 0:
            avg_brightness = total_brightness / frames_captured
            
            properties.update({
                'frames_captured': frames_captured,
                'avg_brightness': avg_brightness,
                'is_static': is_static,
                'sample_saved': True
            })
            
            # Analyser les caractéristiques pour identifier le type
            camera_type = "unknown"
            confidence = 0
            
            # DroidCam a tendance à avoir des images statiques avec du texte
            if is_static and avg_brightness < 50:
                camera_type = "droidcam_virtual"
                confidence = 0.8
            # ESP32-CAM physique aura des images qui changent
            elif not is_static and 30 < avg_brightness < 200:
                camera_type = "esp32cam_physical"
                confidence = 0.7
            # Webcam standard
            elif not is_static:
                camera_type = "standard_webcam"
                confidence = 0.6
            
            properties.update({
                'detected_type': camera_type,
                'confidence': confidence
            })
            
            print(f"   Type détecté: {camera_type} (confiance: {confidence:.1f})")
            print(f"   Luminosité moyenne: {avg_brightness:.1f}")
            print(f"   Image statique: {is_static}")
            print(f"   Échantillon sauvé: camera_analysis/camera_{camera_index}_sample.jpg")
            
            return properties
        else:
            print("   ❌ Aucune frame capturée")
            return None
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None

def identify_esp32cam():
    """Identifie quelle caméra est la vraie ESP32-CAM"""
    print("=" * 60)
    print("🔍 IDENTIFICATION DE LA VRAIE ESP32-CAM")
    print("=" * 60)
    
    cameras_info = []
    
    # Analyser les caméras 0, 1, 2
    for i in range(3):
        info = analyze_camera_properties(i)
        if info:
            cameras_info.append(info)
    
    if not cameras_info:
        print("\n❌ Aucune caméra analysée avec succès")
        return None
    
    print(f"\n📊 RÉSUMÉ DE L'ANALYSE:")
    print("-" * 60)
    
    esp32cam_candidates = []
    
    for info in cameras_info:
        print(f"Caméra {info['index']}:")
        print(f"   - Résolution: {info['width']}x{info['height']}")
        print(f"   - Type détecté: {info['detected_type']}")
        print(f"   - Confiance: {info['confidence']:.1f}")
        print(f"   - Luminosité: {info['avg_brightness']:.1f}")
        print(f"   - Statique: {info['is_static']}")
        print()
        
        if info['detected_type'] == 'esp32cam_physical':
            esp32cam_candidates.append(info)
    
    # Recommandation
    print("🎯 RECOMMANDATIONS:")
    
    if esp32cam_candidates:
        best_candidate = max(esp32cam_candidates, key=lambda x: x['confidence'])
        print(f"✅ ESP32-CAM probablement à l'index {best_candidate['index']}")
        return best_candidate['index']
    else:
        print("⚠️ Aucune ESP32-CAM physique détectée automatiquement")
        print("\n💡 Vérification manuelle recommandée:")
        print("   1. Regardez les images dans le dossier 'camera_analysis/'")
        print("   2. Identifiez visuellement quelle image vient de votre ESP32-CAM")
        print("   3. Notez l'index correspondant")
        
        # Demander à l'utilisateur de choisir manuellement
        print(f"\n📷 Caméras disponibles:")
        for info in cameras_info:
            print(f"   {info['index']}. Caméra {info['index']} - {info['detected_type']}")
        
        try:
            choice = input("\nQuel index correspond à votre ESP32-CAM physique ? (0-2): ")
            return int(choice)
        except ValueError:
            print("❌ Choix invalide")
            return None

def test_specific_camera(camera_index):
    """Teste une caméra spécifique avec aperçu"""
    print(f"\n🎥 Test de la caméra {camera_index} avec aperçu...")
    print("   Une fenêtre va s'ouvrir. Vérifiez si c'est votre ESP32-CAM.")
    print("   Appuyez sur 'q' pour fermer la fenêtre.")
    
    try:
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print("❌ Impossible d'ouvrir la caméra")
            return False
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            
            if ret:
                frame_count += 1
                
                # Ajouter des informations
                cv2.putText(frame, f"Camera {camera_index} - Frame {frame_count}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Est-ce votre ESP32-CAM ? (q pour fermer)", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                cv2.imshow(f'Test Camera {camera_index}', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("⚠️ Pas de frame")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Demander confirmation
        is_esp32cam = input(f"\nEst-ce que la caméra {camera_index} est votre ESP32-CAM ? (o/N): ").strip().lower()
        return is_esp32cam in ['o', 'oui', 'y', 'yes']
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    # Étape 1: Analyse automatique
    esp32cam_index = identify_esp32cam()
    
    if esp32cam_index is not None:
        print(f"\n🎯 Test de la caméra {esp32cam_index} identifiée...")
        
        # Étape 2: Vérification visuelle
        if test_specific_camera(esp32cam_index):
            print(f"\n✅ ESP32-CAM confirmée à l'index {esp32cam_index}")
            
            # Étape 3: Configuration
            config_choice = input("\nVoulez-vous configurer cette caméra dans le système ? (o/N): ").strip().lower()
            if config_choice in ['o', 'oui', 'y', 'yes']:
                # Importer et configurer
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                
                from src.utils.config import config
                
                config.set('camera.use_droid_cam', False)
                config.set('camera.use_esp32_cam', False)
                config.set('camera.index', esp32cam_index)
                
                print(f"✅ ESP32-CAM configurée à l'index {esp32cam_index}")
                print("💾 Configuration sauvegardée")
        else:
            print("\n🔄 Essayons les autres caméras...")
            for i in range(3):
                if i != esp32cam_index:
                    if test_specific_camera(i):
                        print(f"\n✅ ESP32-CAM trouvée à l'index {i}")
                        break
    
    print(f"\n📁 Vérifiez les images dans le dossier 'camera_analysis/' pour confirmation visuelle")

if __name__ == "__main__":
    main()
