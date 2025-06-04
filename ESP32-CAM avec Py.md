<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Guide Complet d'Intégration de l'ESP32-CAM avec Python

L'ESP32-CAM représente une solution économique et polyvalente pour les projets de vision par ordinateur et de surveillance. Ce module, coûtant environ 10 dollars, combine les capacités Wi-Fi de l'ESP32 avec une caméra OV2640, offrant ainsi des possibilités étendues d'intégration avec Python[^4]. Il existe principalement deux approches pour utiliser Python avec l'ESP32-CAM : l'exécution directe de MicroPython sur le module ou l'utilisation d'Arduino sur l'ESP32-CAM couplé à un traitement Python sur ordinateur. Cette dernière approche s'avère particulièrement efficace pour des applications de vision par ordinateur nécessitant des bibliothèques comme OpenCV[^3]. Le module présente des caractéristiques techniques impressionnantes incluant un processeur 32-bit jusqu'à 160MHz, 520KB de SRAM, le support WiFi 802.11b/g/n, et la compatibilité avec plusieurs protocoles de communication[^4].

## Configuration Matérielle et Prérequis

### Composants Nécessaires

L'ESP32-CAM ne possède pas de connecteur USB intégré, ce qui nécessite l'utilisation d'un programmeur FTDI pour télécharger le code via les broches série U0R et U0T[^4]. Les composants essentiels comprennent le module ESP32-CAM avec caméra OV2640, un programmeur FTDI, des câbles de connexion femelle-femelle, et optionnellement une carte microSD pour le stockage d'images[^4]. Le module supporte les caméras OV2640 et OV7670 avec un flash LED intégré, ainsi qu'un slot pour carte TF[^4].

La connexion physique entre l'ESP32-CAM et le programmeur FTDI doit respecter un schéma de câblage spécifique. Pour la programmation, il est nécessaire de connecter la broche IO0 à la masse (GND) avant le téléchargement du code, puis de la déconnecter et redémarrer le module pour l'exécution normale[^2]. Cette procédure est cruciale pour basculer entre le mode programmation et le mode exécution.

### Installation de l'Environnement de Développement

Pour utiliser l'ESP32-CAM avec Arduino IDE, l'ajout du fichier JSON approprié dans les préférences est requis. Dans Arduino IDE, il faut aller dans Fichier > Préférences et ajouter l'URL du gestionnaire de cartes ESP32 dans la section "URLs de gestionnaire de cartes supplémentaires"[^2]. Ensuite, l'installation du package ESP32 via le gestionnaire de cartes permet de sélectionner "AI Thinker ESP32-CAM" comme carte cible[^2][^3].

L'environnement Python nécessite l'installation de plusieurs bibliothèques essentielles. Les commandes pip install numpy, pip install opencv-python, et pip install cvlib permettent d'installer les dépendances nécessaires pour le traitement d'images et la détection d'objets[^3]. L'installation de Python doit inclure l'ajout du PATH pour permettre l'exécution des commandes pip depuis l'invite de commande[^3].

## Approche MicroPython sur ESP32-CAM

### Installation du Firmware MicroPython

L'utilisation de MicroPython directement sur l'ESP32-CAM offre une alternative intéressante à Arduino pour les développeurs préférant Python. L'installation du firmware MicroPython nécessite d'abord l'effacement de la mémoire flash existante, puis le téléchargement d'un firmware MicroPython compatible avec l'ESP32-CAM[^1]. Cette approche permet d'écrire et d'exécuter du code Python directement sur le microcontrôleur, simplifiant ainsi le développement pour certaines applications.

Le processus d'installation implique l'utilisation d'outils comme esptool.py pour flasher le firmware. Une fois MicroPython installé, l'environnement de développement Thonny peut être utilisé pour écrire et exécuter des scripts Python directement sur l'ESP32-CAM[^1]. Cette configuration permet un accès direct aux fonctionnalités de la caméra et du Wi-Fi depuis Python.

### Contrôle de la Caméra en MicroPython

```python
import camera
import network
import time

# Configuration de la caméra
camera.init(0, format=camera.JPEG, framesize=camera.FRAME_VGA)

# Configuration du Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('VOTRE_SSID', 'VOTRE_PASSWORD')

# Attendre la connexion
while not wlan.isconnected():
    time.sleep(1)
    print('Connexion en cours...')

print('Connecté au Wi-Fi:', wlan.ifconfig())

# Capture d'image
def capture_image():
    try:
        buf = camera.capture()
        if buf:
            print('Image capturée, taille:', len(buf))
            return buf
        else:
            print('Erreur lors de la capture')
            return None
    except Exception as e:
        print('Erreur:', e)
        return None

# Fonction principale
def main():
    while True:
        image_data = capture_image()
        if image_data:
            # Traitement de l'image ou envoi réseau
            pass
        time.sleep(5)

if __name__ == "__main__":
    main()
```


### Gestion Réseau et Installation de Packages

MicroPython sur ESP32-CAM permet l'installation de packages supplémentaires via upip. Pour installer des bibliothèques comme urequests, il est nécessaire de se connecter au réseau Wi-Fi puis d'utiliser upip.install()[^1]. Cependant, il est crucial de se déconnecter du réseau après l'installation pour éviter des problèmes de redémarrage[^1].

```python
import upip
import network

# Se connecter au Wi-Fi (code de connexion omis pour la brièveté)

# Installation de packages
upip.install('urequests')

# Important: se déconnecter après installation
wlan.disconnect()
```


## Approche Arduino/Python Hybride

### Configuration Arduino pour ESP32-CAM

L'approche hybride utilise Arduino pour programmer l'ESP32-CAM et Python sur un ordinateur pour le traitement avancé des images. Cette méthode exploite les forces de chaque plateforme : la simplicité d'Arduino pour la gestion matérielle et la puissance de Python pour l'analyse d'images[^3].

```cpp
#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"

// Configuration de la caméra AI Thinker
#define CAMERA_MODEL_AI_THINKER
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

const char* ssid = "VOTRE_SSID";
const char* password = "VOTRE_PASSWORD";

httpd_handle_t stream_httpd = NULL;

static esp_err_t stream_handler(httpd_req_t *req) {
    camera_fb_t * fb = NULL;
    esp_err_t res = ESP_OK;
    size_t _jpg_buf_len = 0;
    uint8_t * _jpg_buf = NULL;
    char * part_buf[^64];

    res = httpd_resp_set_type(req, "multipart/x-mixed-replace;boundary=frame");
    if(res != ESP_OK) return res;

    while(true) {
        fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("Erreur capture caméra");
            res = ESP_FAIL;
        } else {
            if(fb->width > 400){
                if(fb->format != PIXFORMAT_JPEG){
                    bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
                    esp_camera_fb_return(fb);
                    fb = NULL;
                    if(!jpeg_converted){
                        Serial.println("Erreur conversion JPEG");
                        res = ESP_FAIL;
                    }
                } else {
                    _jpg_buf_len = fb->len;
                    _jpg_buf = fb->buf;
                }
            }
        }
        
        if(res == ESP_OK){
            size_t hlen = snprintf((char *)part_buf, 64, 
                "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", 
                _jpg_buf_len);
            res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
        }
        
        if(res == ESP_OK){
            res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
        }
        
        if(res == ESP_OK){
            res = httpd_resp_send_chunk(req, "\r\n--frame\r\n", 13);
        }
        
        if(fb){
            esp_camera_fb_return(fb);
            fb = NULL;
            _jpg_buf = NULL;
        } else if(_jpg_buf){
            free(_jpg_buf);
            _jpg_buf = NULL;
        }
        
        if(res != ESP_OK) break;
    }
    return res;
}

void setup() {
    Serial.begin(115200);
    
    // Configuration caméra
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 10;
    config.fb_count = 1;

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Erreur initialisation caméra: 0x%x", err);
        return;
    }

    // Connexion Wi-Fi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("");
    Serial.println("WiFi connecté");
    Serial.print("Adresse IP: ");
    Serial.println(WiFi.localIP());

    // Démarrage serveur HTTP
    httpd_config_t config_httpd = HTTPD_DEFAULT_CONFIG();
    config_httpd.server_port = 80;

    httpd_uri_t stream_uri = {
        .uri       = "/stream",
        .method    = HTTP_GET,
        .handler   = stream_handler,
        .user_ctx  = NULL
    };

    if (httpd_start(&stream_httpd, &config_httpd) == ESP_OK) {
        httpd_register_uri_handler(stream_httpd, &stream_uri);
    }
}

void loop() {
    delay(1);
}
```


### Script Python pour Traitement d'Images

L'intégration côté Python permet d'exploiter des bibliothèques avancées comme OpenCV et cvlib pour la détection d'objets. Le script Python se connecte au flux vidéo de l'ESP32-CAM et applique des algorithmes de vision par ordinateur en temps réel[^3].

```python
import cv2
import numpy as np
import cvlib as cv
from cvlib.object_detection import draw_bbox
import requests
from threading import Thread
import time

class ESP32CAMProcessor:
    def __init__(self, esp32_ip, stream_port=80):
        self.esp32_ip = esp32_ip
        self.stream_port = stream_port
        self.stream_url = f"http://{esp32_ip}:{stream_port}/stream"
        self.cap = None
        self.running = False
        self.frame = None
        
    def connect_camera(self):
        """Connexion au flux vidéo ESP32-CAM"""
        try:
            self.cap = cv2.VideoCapture(self.stream_url)
            if self.cap.isOpened():
                print(f"Connexion réussie à {self.stream_url}")
                return True
            else:
                print("Erreur de connexion à la caméra")
                return False
        except Exception as e:
            print(f"Erreur lors de la connexion: {e}")
            return False
    
    def capture_frame(self):
        """Thread pour capture continue d'images"""
        while self.running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.frame = frame
                else:
                    print("Erreur lecture frame")
                    time.sleep(0.1)
            time.sleep(0.03)  # ~30 FPS
    
    def detect_objects(self, frame):
        """Détection d'objets avec cvlib"""
        try:
            bbox, label, conf = cv.detect_common_objects(frame)
            output_image = draw_bbox(frame, bbox, label, conf)
            return output_image, label, conf
        except Exception as e:
            print(f"Erreur détection d'objets: {e}")
            return frame, [], []
    
    def process_video_stream(self):
        """Traitement principal du flux vidéo"""
        if not self.connect_camera():
            return
        
        self.running = True
        capture_thread = Thread(target=self.capture_frame, daemon=True)
        capture_thread.start()
        
        # Attendre première frame
        while self.frame is None and self.running:
            time.sleep(0.1)
        
        try:
            while self.running:
                if self.frame is not None:
                    # Copie de la frame courante
                    current_frame = self.frame.copy()
                    
                    # Détection d'objets
                    processed_frame, labels, confidences = self.detect_objects(current_frame)
                    
                    # Affichage des résultats
                    if labels:
                        print(f"Objets détectés: {labels}")
                        for i, label in enumerate(labels):
                            print(f"  {label}: {confidences[i]:.2f}")
                    
                    # Affichage de l'image
                    cv2.imshow('ESP32-CAM Object Detection', processed_frame)
                    
                    # Gestion des événements clavier
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('s'):
                        # Sauvegarde de l'image
                        timestamp = int(time.time())
                        filename = f"capture_{timestamp}.jpg"
                        cv2.imwrite(filename, processed_frame)
                        print(f"Image sauvegardée: {filename}")
                
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("Arrêt demandé par l'utilisateur")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Nettoyage des ressources"""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Ressources libérées")

def main():
    # Configuration
    ESP32_IP = "192.168.1.100"  # Remplacer par l'IP de votre ESP32-CAM
    
    # Vérification de connexion
    try:
        response = requests.get(f"http://{ESP32_IP}", timeout=5)
        print(f"ESP32-CAM accessible à l'adresse {ESP32_IP}")
    except requests.exceptions.RequestException:
        print(f"Impossible de joindre l'ESP32-CAM à {ESP32_IP}")
        print("Vérifiez l'adresse IP et la connexion réseau")
        return
    
    # Démarrage du processeur
    processor = ESP32CAMProcessor(ESP32_IP)
    
    print("Démarrage du traitement vidéo...")
    print("Appuyez sur 'q' pour quitter, 's' pour sauvegarder une image")
    
    processor.process_video_stream()

if __name__ == "__main__":
    main()
```


## Applications Avancées et Optimisations

### Détection de Mouvement et Alertes

L'intégration d'un capteur PIR avec l'ESP32-CAM permet de créer un système de surveillance intelligent. Lorsque le capteur détecte un mouvement, l'ESP32-CAM peut automatiquement capturer une image et l'envoyer via le réseau pour analyse[^2]. Cette approche économise l'énergie et les ressources réseau en ne transmettant des données que lorsque nécessaire.

```python
import cv2
import numpy as np
import time
from datetime import datetime

class MotionDetector:
    def __init__(self, esp32_processor):
        self.processor = esp32_processor
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()
        self.motion_threshold = 1000
        self.last_motion_time = 0
        self.motion_cooldown = 5  # secondes
        
    def detect_motion(self, frame):
        """Détection de mouvement dans la frame"""
        # Application du soustracteur de fond
        fg_mask = self.background_subtractor.apply(frame)
        
        # Nettoyage du masque
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        
        # Calcul de la quantité de mouvement
        motion_area = cv2.countNonZero(fg_mask)
        
        current_time = time.time()
        motion_detected = (motion_area > self.motion_threshold and 
                          current_time - self.last_motion_time > self.motion_cooldown)
        
        if motion_detected:
            self.last_motion_time = current_time
            self.save_motion_capture(frame)
            
        return motion_detected, motion_area, fg_mask
    
    def save_motion_capture(self, frame):
        """Sauvegarde automatique lors de détection de mouvement"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"motion_capture_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Mouvement détecté! Image sauvegardée: {filename}")
```


### Optimisation des Performances

L'optimisation des performances dans l'intégration ESP32-CAM/Python implique plusieurs considérations techniques. La qualité JPEG de l'ESP32-CAM peut être ajustée pour équilibrer qualité d'image et vitesse de transmission. Une qualité de 10-15 offre généralement un bon compromis pour la plupart des applications de vision par ordinateur[^3].

La gestion de la mémoire constitue un aspect critique, particulièrement lors du traitement de flux vidéo continus. L'utilisation de threads séparés pour la capture et le traitement d'images permet d'éviter les blocages et maintient un flux régulier. La mise en place d'un buffer circulaire peut également améliorer la fluidité du traitement.

```python
from collections import deque
import threading

class OptimizedFrameBuffer:
    def __init__(self, buffer_size=10):
        self.buffer = deque(maxlen=buffer_size)
        self.lock = threading.Lock()
        
    def add_frame(self, frame):
        with self.lock:
            self.buffer.append(frame.copy())
    
    def get_latest_frame(self):
        with self.lock:
            return self.buffer[-1] if self.buffer else None
    
    def get_frame_count(self):
        with self.lock:
            return len(self.buffer)
```


## Conclusion

L'intégration de l'ESP32-CAM avec Python offre des possibilités considérables pour le développement d'applications de vision par ordinateur et d'IoT. Les deux approches présentées - MicroPython direct sur l'ESP32-CAM et la solution hybride Arduino/Python - répondent à des besoins différents selon la complexité du traitement requis et les contraintes matérielles[^1][^3]. L'approche MicroPython convient parfaitement aux applications simples nécessitant un contrôle direct de la caméra, tandis que la solution hybride exploite pleinement les capacités de traitement avancées disponibles sur ordinateur.

Les exemples de code fournis constituent une base solide pour le développement d'applications personnalisées. L'optimisation des performances, la gestion du mouvement, et l'intégration de bibliothèques comme OpenCV démontrent la flexibilité de cette plateforme pour des projets allant de la surveillance domestique aux systèmes industriels de vision par ordinateur. La capacité de l'ESP32-CAM à transmettre des flux vidéo de qualité à un coût réduit en fait une solution particulièrement attractive pour les développeurs cherchant à intégrer des fonctionnalités de vision dans leurs projets Python.

<div style="text-align: center">⁂</div>

[^1]: https://www.youtube.com/watch?v=TDgM8eMTpIw

[^2]: https://www.youtube.com/watch?v=hSr557hppwY

[^3]: https://www.digikey.es/en/maker/projects/simple-esp32-cam-object-detection-using-open-cv/d5fd7eaa783e49908da936a85b086eae

[^4]: https://randomnerdtutorials.com/esp32-cam-video-streaming-face-recognition-arduino-ide/

[^5]: https://www.aranacorp.com/fr/programmez-un-esp32-avec-micropython/

[^6]: https://github.com/shariltumin/esp32-cam-micropython-2022

[^7]: https://www.upesy.com/blogs/tutorials/install-micropython-on-esp32-quickly-with-thonny-ide

[^8]: https://www.instructables.com/How-to-Use-ESP32-CAM-With-MicroPython/

[^9]: https://www.upesy.fr/blogs/tutorials/install-micropython-on-esp32-quickly-with-thonny-ide

[^10]: https://www.upesy.fr/blogs/tutorials/esp32-quickstart-installation-programming-guide

[^11]: https://github.com/lemariva/micropython-camera-driver

[^12]: https://randomnerdtutorials.com/getting-started-thonny-micropython-python-ide-esp32-esp8266/

[^13]: https://www.hackster.io/onedeadmatch/esp32-cam-python-stream-opencv-example-1cc205

[^14]: https://disciplines.ac-toulouse.fr/sii/system/files/2021-12/Tuto-ESP32Cam-PriseenMain.pdf

[^15]: https://bhave.sh/micropython-install-esp32/

[^16]: https://www.reddit.com/r/esp32/comments/1839wn1/esp32_cam_with_micropython_help/

[^17]: https://www.diyengineers.com/2023/04/13/esp32-cam-complete-guide/

[^18]: https://lemariva.com/blog/2020/06/micropython-support-cameras-m5camera-esp32-cam-etc

[^19]: https://gist.github.com/youjunjer/79e5dad5f47ee5757fcb9d401a95e76b

[^20]: https://en.vittascience.com/learn/tutorial.php?id=1111%2Fflasher-le-firmware-micropython-dans-l-esp32cam

[^21]: https://github.com/t0mer/espcam-secserver

[^22]: https://www.reddit.com/r/microcontrollers/comments/1afu08r/esp32cam_and_micropython_tutorial/?tl=fr

[^23]: https://fr.vittascience.com/learn/tutorial.php?id=1112%2Fmon-1er-programme-avec-l-esp32cam

[^24]: https://fr.vittascience.com/learn/tutorial.php?id=1111%2Fflasher-le-firmware-micropython-dans-l-esp32cam

