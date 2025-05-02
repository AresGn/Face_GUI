import cv2
import os
import logging
import numpy as np
from time import time
from PyQt5.QtWidgets import QMessageBox
from utils.config import config

# Configuration du logger
logging.basicConfig(filename='face_detection.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class FaceDetector:
    def __init__(self):
        """Initialiser le détecteur de visage"""
        # Charger le classificateur en cascade pour la détection de visage
        cascade_path = os.path.join('data', 'haarcascade_frontalface_default.xml')
        
        # Vérifier si le fichier existe, sinon créer le répertoire data
        if not os.path.exists(cascade_path):
            os.makedirs(os.path.dirname(cascade_path), exist_ok=True)
            # Télécharger le classificateur si nécessaire
            try:
                from urllib.request import urlretrieve
                url = 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml'
                urlretrieve(url, cascade_path)
                logging.info(f"Classificateur téléchargé depuis: {url}")
            except Exception as e:
                logging.error(f"Erreur lors du téléchargement du classificateur: {e}")
                logging.warning(f"Le fichier {cascade_path} n'existe pas. Vous devez le télécharger.")
        
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Paramètres optimisés pour améliorer la détection
        self.min_neighbors = 6  # Augmenté pour réduire les faux positifs
        self.scale_factor = 1.2  # Valeur équilibrée pour vitesse/précision
        self.min_size = (80, 80)  # Taille minimale du visage à détecter (augmentée)
        
        # Couleurs pour les rectangles (format BGR)
        self.green_color = (0, 255, 0)  # Visage reconnu
        self.red_color = (0, 0, 255)    # Visage inconnu
        
        # Paramètres pour les caméras
        self.use_droid_cam = config.get('camera.use_droid_cam', False)
        self.droid_cam_url = config.get('camera.droid_cam_url', 'http://192.168.1.X:4747/video')
        self.camera_index = config.get('camera.index', 0)
    
    def get_camera_source(self):
        """Retourne la source de caméra appropriée en fonction de la configuration"""
        if self.use_droid_cam and self.droid_cam_url:
            logging.info(f"Utilisation de DroidCam comme source: {self.droid_cam_url}")
            return self.droid_cam_url
        else:
            logging.info(f"Utilisation de la webcam par défaut: index {self.camera_index}")
            return self.camera_index
    
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
    
    def recognize_face(self, employee_id, parent=None, timeout=30):
        """
        Fonction principale pour reconnaître un visage
        
        Args:
            employee_id (int): ID de l'employé à reconnaître
            parent (QWidget): Widget parent pour les boîtes de dialogue
            timeout (int): Délai d'expiration en secondes
            
        Returns:
            bool: True si le visage est reconnu, False sinon
        """
        # Vérifier si le classificateur pour cet employé existe
        classifier_path = os.path.join('data', 'classifiers', f'{employee_id}_classifier.xml')
        if not os.path.exists(classifier_path):
            if parent:
                QMessageBox.warning(parent, "Avertissement", 
                                   f"Aucun modèle trouvé pour l'employé ID={employee_id}. Veuillez d'abord entraîner le modèle.")
            return False
        
        # Charger le classificateur
        self.recognizer.read(classifier_path)
        
        # Ouvrir la caméra avec la source appropriée
        camera_source = self.get_camera_source()
        cap = cv2.VideoCapture(camera_source)
        
        if not cap.isOpened():
            logging.error(f"Impossible d'ouvrir la caméra source: {camera_source}")
            if parent:
                QMessageBox.critical(parent, "Erreur", f"Impossible d'ouvrir la caméra source: {camera_source}")
            return False
        
        # Réduire la résolution pour accélérer le traitement
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        pred = False
        start_time = time()
        frame_count = 0
        successful_frames = 0  # Compteur de frames avec reconnaissance réussie
        
        # Boucle principale de reconnaissance
        while True:
            ret, frame = cap.read()
            if not ret:
                logging.error("Échec de la capture d'image")
                break
            
            # Obtenir les dimensions de l'image
            frame_height, frame_width = frame.shape[:2]
            
            # Convertir l'image en niveaux de gris
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Améliorer le contraste pour une meilleure détection
            gray = cv2.equalizeHist(gray)
            
            # Traiter une frame sur deux pour améliorer les performances
            frame_count += 1
            if frame_count % 2 != 0:
                cv2.imshow("Reconnaissance faciale", frame)
                if cv2.waitKey(5) & 0xFF == ord('q'):
                    break
                continue
            
            # Détecter les visages avec des paramètres optimisés
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=self.scale_factor, 
                minNeighbors=self.min_neighbors,
                minSize=self.min_size
            )
            
            # Filtrer les fausses détections
            valid_faces = []
            for (x, y, w, h) in faces:
                if self.check_false_detection(frame_height, frame_width, x, y, w, h):
                    valid_faces.append((x, y, w, h))
            
            for (x, y, w, h) in valid_faces:
                # Région d'intérêt (ROI) pour la reconnaissance
                roi_gray = gray[y:y+h, x:x+w]
                
                # Prédire l'identité
                id_pred, confidence = self.recognizer.predict(roi_gray)
                confidence = 100 - int(confidence)
                
                # Vérifier si le visage est reconnu avec un seuil plus élevé pour la fiabilité
                if confidence > 60:
                    pred = True
                    successful_frames += 1
                    text = 'Reconnu: ID=' + str(employee_id)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    # Rectangle vert pour un visage reconnu
                    cv2.rectangle(frame, (x, y), (x + w, y + h), self.green_color, 2)
                    cv2.putText(frame, text, (x, y-10), font, 0.5, self.green_color, 2)
                    # Afficher le niveau de confiance
                    confidence_text = f"Confiance: {confidence}%"
                    cv2.putText(frame, confidence_text, (x, y+h+20), font, 0.5, self.green_color, 1)
                else:
                    pred = False
                    text = "Visage inconnu"
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    # Rectangle rouge pour un visage inconnu
                    cv2.rectangle(frame, (x, y), (x + w, y + h), self.red_color, 2)
                    cv2.putText(frame, text, (x, y-10), font, 0.5, self.red_color, 2)
                    # Afficher le niveau de confiance
                    confidence_text = f"Confiance: {confidence}%"
                    cv2.putText(frame, confidence_text, (x, y+h+20), font, 0.5, self.red_color, 1)
            
            # Afficher l'image
            cv2.imshow("Reconnaissance faciale", frame)
            
            # Vérifier si le délai d'expiration est atteint
            elapsed_time = time() - start_time
            
            # Exiger plusieurs frames positives pour une reconnaissance fiable
            if successful_frames >= 5:  # Au moins 5 frames positives pour confirmer
                logging.info(f"Reconnaissance confirmée après {successful_frames} frames positives")
                break
                
            if elapsed_time >= timeout:
                pred = (successful_frames >= 5)  # Confirme seulement si assez de frames positives
                logging.info(f"Délai d'expiration atteint. Résultat: {'Reconnu' if pred else 'Non reconnu'}")
                break
            
            # Sortir si 'q' est pressé
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
        
        # Libérer les ressources
        cap.release()
        cv2.destroyAllWindows()
        
        # Afficher le résultat
        if parent:
            if pred:
                QMessageBox.information(parent, "Succès", "Visage reconnu avec succès !")
            else:
                QMessageBox.warning(parent, "Avertissement", "Visage non reconnu. Veuillez réessayer.")
        
        return pred

# Instance globale du détecteur de visage
face_detector = FaceDetector() 