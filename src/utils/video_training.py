import cv2
import os
import datetime
import logging
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
import time

# Configuration du logger
logging.basicConfig(filename='video_training.log', level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

class VideoTrainer:
    """Classe pour créer un dataset d'entraînement à partir d'une vidéo"""
    
    def __init__(self, face_cascade_path=None):
        """
        Initialiser le VideoTrainer
        
        Args:
            face_cascade_path (str): Chemin vers le classificateur en cascade pour la détection de visage
        """
        # Charger le classificateur en cascade pour la détection de visage
        if not face_cascade_path:
            face_cascade_path = os.path.join('data', 'haarcascade_frontalface_default.xml')
        
        # Vérifier si le fichier existe, sinon créer le répertoire data
        if not os.path.exists(face_cascade_path):
            os.makedirs(os.path.dirname(face_cascade_path), exist_ok=True)
            # Télécharger le classificateur si nécessaire
            try:
                from urllib.request import urlretrieve
                url = 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml'
                urlretrieve(url, face_cascade_path)
                logging.info(f"Classificateur téléchargé depuis: {url}")
            except Exception as e:
                logging.error(f"Erreur lors du téléchargement du classificateur: {e}")
        
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        
        # Paramètres optimisés pour améliorer la détection
        self.min_neighbors = 6  # Augmenté pour réduire les faux positifs
        self.scale_factor = 1.2  # Valeur équilibrée pour vitesse/précision
        self.min_size = (80, 80)  # Taille minimale du visage à détecter (augmentée)
    
    def check_false_detection(self, frame_height, frame_width, x, y, w, h):
        """
        Vérifie si une détection est probablement un faux positif
        
        Args:
            frame_height (int): Hauteur de l'image
            frame_width (int): Largeur de l'image
            x, y, w, h: Coordonnées et dimensions du rectangle
            
        Returns:
            bool: True si la détection est valide, False si c'est probablement un faux positif
        """
        # 1. Vérifier si le rectangle dépasse les limites de l'image
        if x < 0 or y < 0 or x + w > frame_width or y + h > frame_height:
            return False
        
        # 2. Vérifier les proportions du visage (hauteur/largeur)
        aspect_ratio = h / w
        if aspect_ratio < 0.8 or aspect_ratio > 1.8:  # Proportions normales entre 0.8 et 1.8
            return False
            
        # 3. Taille du visage par rapport à l'image
        face_area = w * h
        frame_area = frame_height * frame_width
        face_ratio = face_area / frame_area
        
        # Si le visage occupe plus de 60% ou moins de 1% de l'image, c'est suspect
        if face_ratio > 0.6 or face_ratio < 0.01:
            return False
        
        return True
    
    def create_dataset_from_video(self, video_path, employee_id, max_images=300, sampling_rate=10):
        """
        Créer un jeu de données de visages à partir d'une vidéo
        
        Args:
            video_path (str): Chemin vers le fichier vidéo
            employee_id (int): ID de l'employé
            max_images (int): Nombre maximal d'images à capturer
            sampling_rate (int): Nombre de frames à sauter entre chaque capture
            
        Returns:
            int: Nombre d'images capturées
        """
        # Vérifier si le fichier vidéo existe
        if not os.path.exists(video_path):
            logging.error(f"Le fichier vidéo n'existe pas: {video_path}")
            return 0
        
        # Créer le répertoire pour stocker les images
        output_dir = os.path.join('data', 'faces', str(employee_id))
        os.makedirs(output_dir, exist_ok=True)
        
        # Ouvrir la vidéo
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            logging.error(f"Impossible d'ouvrir la vidéo: {video_path}")
            return 0
        
        num_of_images = 0
        frame_count = 0
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Boucle de traitement de la vidéo
        while video.isOpened() and num_of_images < max_images:
            ret, frame = video.read()
            if not ret:
                break
            
            # Traiter une frame sur 'sampling_rate'
            frame_count += 1
            if frame_count % sampling_rate != 0:
                continue
            
            # Obtenir les dimensions de l'image
            frame_height, frame_width = frame.shape[:2]
            
            # Convertir l'image en niveaux de gris
            gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Améliorer le contraste
            gray_img = cv2.equalizeHist(gray_img)
            
            # Détecter les visages avec des paramètres optimisés
            faces = self.face_cascade.detectMultiScale(
                gray_img, 
                scaleFactor=self.scale_factor, 
                minNeighbors=self.min_neighbors,
                minSize=self.min_size
            )
            
            # Filtrer les fausses détections
            valid_faces = []
            for (x, y, w, h) in faces:
                if self.check_false_detection(frame_height, frame_width, x, y, w, h):
                    valid_faces.append((x, y, w, h))
            
            # Extraire et enregistrer chaque visage valide
            for (x, y, w, h) in valid_faces:
                # Dessiner un rectangle autour du visage (pour la visualisation)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Extraire la région du visage
                face_roi = frame[y:y+h, x:x+w]
                
                # Enregistrer l'image du visage
                image_path = os.path.join(output_dir, f"{num_of_images}_{timestamp}_{employee_id}.jpg")
                cv2.imwrite(image_path, face_roi)
                num_of_images += 1
                logging.info(f"Image {num_of_images} capturée pour l'employé ID={employee_id} à partir de la vidéo")
                
                # Afficher l'image avec les rectangles (optionnel)
                cv2.imshow("Traitement vidéo", frame)
                cv2.waitKey(1)
                
                # Sortir si le nombre maximal d'images est atteint
                if num_of_images >= max_images:
                    break
        
        # Libérer les ressources
        video.release()
        cv2.destroyAllWindows()
        
        logging.info(f"Jeu de données créé à partir de la vidéo pour l'employé ID={employee_id} avec {num_of_images} images")
        return num_of_images

class VideoTrainerThread(QThread):
    """Thread pour extraire des visages à partir d'une vidéo pour l'entraînement"""
    
    # Signaux
    progress_signal = pyqtSignal(int)        # Signal de progression (nombre d'images)
    finished_signal = pyqtSignal(int)        # Signal de fin (nombre total d'images)
    error_signal = pyqtSignal(str)           # Signal d'erreur (message)
    frame_signal = pyqtSignal(QImage)        # Signal pour l'aperçu du cadre vidéo
    
    def __init__(self, video_path, employee_id, max_images=200):
        """Initialiser le thread de traitement vidéo
        
        Args:
            video_path (str): Chemin vers le fichier vidéo
            employee_id (int): ID de l'employé
            max_images (int, optional): Nombre maximum d'images à extraire. Par défaut 200.
        """
        super().__init__()
        
        self.video_path = video_path
        self.employee_id = employee_id
        self.max_images = max_images
        self.running = True
        
        # Charger le modèle de détection de visage
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Intervalle minimum entre les images (en secondes)
        self.min_interval = 0.1
        
        # Répertoire de destination pour les images
        self.dataset_dir = os.path.join('data', 'faces', str(self.employee_id))
        
        # Créer le répertoire s'il n'existe pas
        os.makedirs(self.dataset_dir, exist_ok=True)
        
        logging.info(f"Initialisation de VideoTrainerThread: video={video_path}, employee_id={employee_id}, max_images={max_images}")
        logging.info(f"Répertoire de destination: {self.dataset_dir}")
    
    def stop(self):
        """Arrêter le thread"""
        self.running = False
        logging.info("Arrêt du thread VideoTrainer demandé")
    
    def run(self):
        """Exécuter le thread"""
        try:
            logging.info(f"Démarrage du traitement de la vidéo: {self.video_path}")
            
            # Vérifier que le répertoire de destination existe
            if not os.path.exists(self.dataset_dir):
                os.makedirs(self.dataset_dir, exist_ok=True)
                logging.info(f"Répertoire créé: {self.dataset_dir}")
            
            # Ouvrir la vidéo
            cap = cv2.VideoCapture(self.video_path)
            
            # Vérifier que la vidéo a été ouverte correctement
            if not cap.isOpened():
                error_msg = f"Impossible d'ouvrir la vidéo: {self.video_path}"
                logging.error(error_msg)
                self.error_signal.emit(error_msg)
                return
            
            # Obtenir les propriétés de la vidéo
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps
            
            logging.info(f"Propriétés de la vidéo: frames={total_frames}, fps={fps}, durée={duration:.2f}s")
            
            # Calculer le pas d'extraction (pour répartir les images sur toute la vidéo)
            if total_frames > self.max_images:
                step = total_frames // self.max_images
            else:
                step = 1
            
            logging.info(f"Pas d'extraction: {step} frames")
            
            # Variables pour suivre la progression
            count = 0
            last_time = time.time()
            frame_idx = 0
            
            # Parcourir les images de la vidéo
            while self.running and count < self.max_images and frame_idx < total_frames:
                # Lire l'image
                ret, frame = cap.read()
                
                # Si la fin de la vidéo est atteinte, sortir de la boucle
                if not ret:
                    break
                
                # Traiter une image tous les 'step' frames
                if frame_idx % step == 0:
                    # Convertir en niveaux de gris pour la détection de visage
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Détecter les visages
                    faces = self.face_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(30, 30),
                        flags=cv2.CASCADE_SCALE_IMAGE
                    )
                    
                    # S'il y a des visages et que l'intervalle minimum est écoulé
                    current_time = time.time()
                    if len(faces) > 0 and (current_time - last_time) >= self.min_interval:
                        for (x, y, w, h) in faces:
                            # Dessiner un rectangle autour du visage pour l'aperçu
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            
                            # Augmenter légèrement la zone du visage (pour inclure plus de contexte)
                            x_margin = int(w * 0.1)
                            y_margin = int(h * 0.1)
                            
                            x1 = max(0, x - x_margin)
                            y1 = max(0, y - y_margin)
                            x2 = min(frame.shape[1], x + w + x_margin)
                            y2 = min(frame.shape[0], y + h + y_margin)
                            
                            # Extraire le visage
                            face_img = frame[y1:y2, x1:x2]
                            
                            # Enregistrer l'image
                            # Format: "num_timestamp_employee_id.jpg" pour correspondre au format attendu par le classificateur
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            img_name = os.path.join(self.dataset_dir, f"{count}_{timestamp}_{self.employee_id}.jpg")
                            cv2.imwrite(img_name, face_img)
                            
                            # Incrémenter le compteur
                            count += 1
                            
                            # Mettre à jour la progression
                            self.progress_signal.emit(count)
                            
                            # Journal
                            logging.info(f"Image {count}/{self.max_images} extraite: {img_name}")
                            
                            # Ne traiter que le premier visage détecté
                            break
                        
                        # Mettre à jour le temps de la dernière capture
                        last_time = current_time
                    
                    # Convertir l'image pour l'aperçu (uniquement si des visages sont détectés)
                    if len(faces) > 0:
                        # Convertir l'image pour Qt
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        h, w, ch = rgb_frame.shape
                        bytes_per_line = ch * w
                        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                        
                        # Émettre le signal pour l'aperçu
                        self.frame_signal.emit(qt_image)
                
                # Incrémenter l'index de l'image
                frame_idx += 1
                
                # Pause pour éviter de surcharger l'interface
                QThread.msleep(10)
            
            # Libérer les ressources
            cap.release()
            
            # Émettre le signal de fin
            self.finished_signal.emit(count)
            
            # Journal
            logging.info(f"Traitement de la vidéo terminé: {count} images extraites")
            
        except Exception as e:
            error_msg = f"Erreur lors du traitement de la vidéo: {str(e)}"
            logging.error(error_msg)
            self.error_signal.emit(error_msg)

# Instance globale du VideoTrainer
video_trainer = VideoTrainer() 