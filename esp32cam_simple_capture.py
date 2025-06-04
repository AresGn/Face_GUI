#!/usr/bin/env python3
"""
Test simple de capture ESP32-CAM via USB
Capture basique d'images et vidéo
"""

import cv2
import os
import time
from datetime import datetime

def test_camera_access():
    """Teste l'accès aux caméras disponibles"""
    print("🔍 Test d'accès aux caméras...")
    
    available_cameras = []
    
    for i in range(5):
        try:
            print(f"   Test caméra {i}...", end="")
            cap = cv2.VideoCapture(i)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    available_cameras.append({
                        'index': i,
                        'width': width,
                        'height': height
                    })
                    print(f" ✅ OK ({width}x{height})")
                else:
                    print(" ❌ Pas de frame")
                cap.release()
            else:
                print(" ❌ Non accessible")
        except Exception as e:
            print(f" ❌ Erreur: {e}")
    
    return available_cameras

def capture_single_photo(camera_index, filename=None):
    """Capture une seule photo"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"esp32cam_photo_{timestamp}.jpg"
    
    print(f"📸 Capture d'une photo avec la caméra {camera_index}...")
    
    try:
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print("❌ Impossible d'ouvrir la caméra")
            return False
        
        # Configuration de la caméra
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Attendre que la caméra se stabilise
        print("   Stabilisation de la caméra...")
        for i in range(5):
            ret, frame = cap.read()
            time.sleep(0.1)
        
        # Capturer la photo finale
        ret, frame = cap.read()
        cap.release()
        
        if ret and frame is not None:
            # Créer le dossier captures s'il n'existe pas
            os.makedirs("captures", exist_ok=True)
            filepath = os.path.join("captures", filename)
            
            # Sauvegarder l'image
            cv2.imwrite(filepath, frame)
            
            print(f"✅ Photo sauvegardée: {filepath}")
            print(f"   Résolution: {frame.shape[1]}x{frame.shape[0]}")
            return True
        else:
            print("❌ Impossible de capturer l'image")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la capture: {e}")
        return False

def live_preview(camera_index, duration=30):
    """Affichage en direct de la caméra"""
    print(f"🎥 Aperçu en direct de la caméra {camera_index} (durée: {duration}s)")
    print("   Appuyez sur 'q' pour quitter, 's' pour sauvegarder une photo")
    
    try:
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print("❌ Impossible d'ouvrir la caméra")
            return False
        
        # Configuration de la caméra
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        start_time = time.time()
        frame_count = 0
        photo_count = 0
        
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            
            if ret:
                frame_count += 1
                
                # Ajouter des informations sur l'image
                timestamp = datetime.now().strftime("%H:%M:%S")
                cv2.putText(frame, f"ESP32-CAM USB - {timestamp}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Frame: {frame_count}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Appuyez sur 's' pour sauvegarder", 
                           (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                # Afficher l'image
                cv2.imshow('ESP32-CAM Live Preview', frame)
                
                # Gestion des touches
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n🛑 Arrêt demandé par l'utilisateur")
                    break
                elif key == ord('s'):
                    # Sauvegarder une photo
                    photo_count += 1
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"esp32cam_live_{timestamp}.jpg"
                    
                    os.makedirs("captures", exist_ok=True)
                    filepath = os.path.join("captures", filename)
                    cv2.imwrite(filepath, frame)
                    print(f"📸 Photo sauvegardée: {filepath}")
            else:
                print("⚠️ Frame perdue")
        
        cap.release()
        cv2.destroyAllWindows()
        
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time if elapsed_time > 0 else 0
        
        print(f"\n📊 Statistiques:")
        print(f"   - Frames capturées: {frame_count}")
        print(f"   - Photos sauvegardées: {photo_count}")
        print(f"   - Durée: {elapsed_time:.1f}s")
        print(f"   - FPS moyen: {fps:.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'aperçu: {e}")
        return False

def record_video(camera_index, duration=10, filename=None):
    """Enregistre une vidéo"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"esp32cam_video_{timestamp}.avi"
    
    print(f"🎬 Enregistrement vidéo avec la caméra {camera_index} (durée: {duration}s)")
    
    try:
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print("❌ Impossible d'ouvrir la caméra")
            return False
        
        # Configuration de la caméra
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Configuration de l'enregistreur vidéo
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        os.makedirs("captures", exist_ok=True)
        filepath = os.path.join("captures", filename)
        out = cv2.VideoWriter(filepath, fourcc, 20.0, (640, 480))
        
        start_time = time.time()
        frame_count = 0
        
        print("   Enregistrement en cours...")
        
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            
            if ret:
                frame_count += 1
                out.write(frame)
                
                # Afficher le progrès
                elapsed = time.time() - start_time
                progress = (elapsed / duration) * 100
                print(f"\r   Progrès: {progress:.1f}% ({frame_count} frames)", end="")
            else:
                print("\n⚠️ Frame perdue")
        
        cap.release()
        out.release()
        
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time if elapsed_time > 0 else 0
        
        print(f"\n✅ Vidéo sauvegardée: {filepath}")
        print(f"   - Frames enregistrées: {frame_count}")
        print(f"   - Durée: {elapsed_time:.1f}s")
        print(f"   - FPS: {fps:.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement: {e}")
        return False

def main():
    print("=" * 60)
    print("📷 TEST SIMPLE ESP32-CAM USB - CAPTURES BASIQUES")
    print("=" * 60)
    
    # Étape 1: Détecter les caméras
    cameras = test_camera_access()
    
    if not cameras:
        print("\n❌ Aucune caméra détectée!")
        print("💡 Vérifiez que l'ESP32-CAM est bien connecté en USB")
        return
    
    print(f"\n✅ {len(cameras)} caméra(s) détectée(s):")
    for cam in cameras:
        print(f"   - Caméra {cam['index']}: {cam['width']}x{cam['height']}")
    
    # Utiliser la première caméra (probablement l'ESP32-CAM)
    camera_index = cameras[0]['index']
    print(f"\n🎯 Utilisation de la caméra {camera_index}")
    
    while True:
        print("\n" + "=" * 40)
        print("🎮 MENU DES TESTS:")
        print("1. Capturer une photo")
        print("2. Aperçu en direct (30s)")
        print("3. Enregistrer une vidéo (10s)")
        print("4. Changer de caméra")
        print("5. Quitter")
        
        choice = input("\nVotre choix (1-5): ").strip()
        
        if choice == "1":
            capture_single_photo(camera_index)
        
        elif choice == "2":
            live_preview(camera_index, 30)
        
        elif choice == "3":
            record_video(camera_index, 10)
        
        elif choice == "4":
            print("\nCaméras disponibles:")
            for i, cam in enumerate(cameras):
                print(f"   {i+1}. Caméra {cam['index']} ({cam['width']}x{cam['height']})")
            
            try:
                cam_choice = int(input("Choisissez une caméra (numéro): ")) - 1
                if 0 <= cam_choice < len(cameras):
                    camera_index = cameras[cam_choice]['index']
                    print(f"✅ Caméra {camera_index} sélectionnée")
                else:
                    print("❌ Choix invalide")
            except ValueError:
                print("❌ Veuillez entrer un numéro valide")
        
        elif choice == "5":
            print("\n👋 Au revoir!")
            break
        
        else:
            print("❌ Choix invalide, veuillez réessayer")

if __name__ == "__main__":
    main()
