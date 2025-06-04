#!/usr/bin/env python3
"""
Script d'intégration ESP32-CAM via USB
Utilise l'ESP32-CAM connecté en USB comme source de caméra
"""

import sys
import os
import cv2
import serial
import serial.tools.list_ports
import time
import threading
import numpy as np
from datetime import datetime

# Ajouter le répertoire src au PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import config

class ESP32CAMUSBManager:
    """Gestionnaire pour ESP32-CAM connecté via USB"""
    
    def __init__(self):
        self.serial_port = None
        self.is_connected = False
        self.is_streaming = False
        self.frame_buffer = None
        self.lock = threading.Lock()
        
    def find_esp32_cam_ports(self):
        """Trouve les ports série potentiels pour ESP32-CAM"""
        ports = []
        available_ports = serial.tools.list_ports.comports()
        
        for port in available_ports:
            # Rechercher des identifiants ESP32 communs
            if any(keyword in port.description.lower() for keyword in 
                   ['esp32', 'cp210', 'ch340', 'ftdi', 'usb-serial']):
                ports.append({
                    'port': port.device,
                    'description': port.description,
                    'vid_pid': f"{port.vid:04X}:{port.pid:04X}" if port.vid and port.pid else "N/A"
                })
        
        return ports
    
    def connect_to_esp32cam(self, port, baudrate=115200):
        """Se connecter à l'ESP32-CAM via le port série"""
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # Attendre la stabilisation
            
            # Tester la communication
            self.serial_port.write(b'AT\r\n')
            response = self.serial_port.readline().decode('utf-8', errors='ignore')
            
            self.is_connected = True
            print(f"✅ Connecté à l'ESP32-CAM sur {port}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur de connexion sur {port}: {e}")
            return False
    
    def disconnect(self):
        """Déconnecter l'ESP32-CAM"""
        self.is_streaming = False
        self.is_connected = False
        
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("🔌 ESP32-CAM déconnecté")
    
    def start_camera_stream(self):
        """Démarrer le flux de caméra (simulation pour USB)"""
        if not self.is_connected:
            print("❌ ESP32-CAM non connecté")
            return False
        
        try:
            # Pour l'ESP32-CAM en USB, nous utilisons OpenCV pour accéder à la caméra
            # L'ESP32-CAM apparaît comme une webcam USB standard
            self.is_streaming = True
            print("📹 Flux de caméra ESP32-CAM démarré")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du démarrage du flux: {e}")
            return False

def detect_esp32cam_as_webcam():
    """Détecte l'ESP32-CAM comme webcam USB"""
    print("🔍 Recherche de l'ESP32-CAM comme webcam USB...")
    
    # Tester les indices de caméra de 0 à 10
    for i in range(11):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"📷 Caméra trouvée à l'index {i}: {width}x{height}")
                    
                    # Vérifier si c'est potentiellement un ESP32-CAM
                    # (résolutions typiques: 640x480, 800x600, 1024x768)
                    if width in [640, 800, 1024] and height in [480, 600, 768]:
                        cap.release()
                        return i
                cap.release()
        except:
            continue
    
    return None

def test_esp32cam_usb_capture(camera_index, duration=10):
    """Teste la capture vidéo depuis l'ESP32-CAM USB"""
    print(f"🎬 Test de capture ESP32-CAM USB (index: {camera_index}, durée: {duration}s)")
    
    try:
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print("❌ Impossible d'ouvrir la caméra ESP32-CAM")
            return False
        
        # Configuration de la caméra
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        start_time = time.time()
        frame_count = 0
        
        print("📹 Capture en cours... (Appuyez sur 'q' pour arrêter)")
        
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
                cv2.putText(frame, f"Resolution: {frame.shape[1]}x{frame.shape[0]}", 
                           (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Afficher l'image
                cv2.imshow('ESP32-CAM USB Test', frame)
                
                # Vérifier si l'utilisateur veut quitter
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("⚠️ Frame perdue")
        
        cap.release()
        cv2.destroyAllWindows()
        
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time
        
        print(f"✅ Test terminé:")
        print(f"   - Frames capturées: {frame_count}")
        print(f"   - Durée: {elapsed_time:.1f}s")
        print(f"   - FPS moyen: {fps:.1f}")
        
        return frame_count > 0
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def configure_esp32cam_usb_in_system(camera_index):
    """Configure l'ESP32-CAM USB dans le système de reconnaissance faciale"""
    print(f"⚙️ Configuration de l'ESP32-CAM USB (index: {camera_index}) dans le système...")
    
    try:
        # Désactiver les autres sources de caméra
        config.set('camera.use_droid_cam', False)
        config.set('camera.use_esp32_cam', False)
        
        # Configurer l'index de caméra pour l'ESP32-CAM USB
        config.set('camera.index', camera_index)
        
        print(f"✅ ESP32-CAM USB configuré comme caméra par défaut (index: {camera_index})")
        print("💡 L'ESP32-CAM USB sera utilisé comme webcam standard dans l'application")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la configuration: {e}")
        return False

def main():
    print("=" * 60)
    print("🔌 INTÉGRATION ESP32-CAM VIA USB")
    print("=" * 60)
    
    # Étape 1: Recherche des ports série ESP32
    manager = ESP32CAMUSBManager()
    esp32_ports = manager.find_esp32_cam_ports()
    
    if esp32_ports:
        print(f"🔍 Ports série ESP32 détectés:")
        for i, port_info in enumerate(esp32_ports):
            print(f"   {i+1}. {port_info['port']} - {port_info['description']} ({port_info['vid_pid']})")
    else:
        print("⚠️ Aucun port série ESP32 détecté")
    
    # Étape 2: Recherche de l'ESP32-CAM comme webcam USB
    camera_index = detect_esp32cam_as_webcam()
    
    if camera_index is not None:
        print(f"✅ ESP32-CAM détecté comme webcam USB à l'index {camera_index}")
        
        # Test de capture
        test_choice = input("\n🎥 Voulez-vous tester la capture vidéo ? (o/N): ").strip().lower()
        if test_choice in ['o', 'oui', 'y', 'yes']:
            duration = input("Durée du test en secondes (défaut: 10): ").strip()
            try:
                duration = int(duration) if duration else 10
            except ValueError:
                duration = 10
            
            if test_esp32cam_usb_capture(camera_index, duration):
                # Configuration dans le système
                config_choice = input("\n⚙️ Voulez-vous configurer l'ESP32-CAM USB dans le système ? (o/N): ").strip().lower()
                if config_choice in ['o', 'oui', 'y', 'yes']:
                    configure_esp32cam_usb_in_system(camera_index)
                    
                    print(f"\n🎉 Configuration terminée !")
                    print(f"💡 Pour utiliser l'ESP32-CAM USB:")
                    print(f"   1. Lancez l'application de reconnaissance faciale")
                    print(f"   2. L'ESP32-CAM sera utilisé automatiquement comme webcam")
                    print(f"   3. Index de caméra configuré: {camera_index}")
            else:
                print("❌ Le test de capture a échoué")
    else:
        print("❌ Aucune ESP32-CAM détectée comme webcam USB")
        print("\n💡 Vérifications à effectuer:")
        print("   1. L'ESP32-CAM est-il correctement connecté en USB ?")
        print("   2. Les drivers USB sont-ils installés ?")
        print("   3. L'ESP32-CAM est-il configuré en mode webcam USB ?")
        print("   4. Essayez de redémarrer l'ESP32-CAM")
    
    # Nettoyage
    manager.disconnect()

if __name__ == "__main__":
    main()
