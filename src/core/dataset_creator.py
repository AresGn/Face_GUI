import cv2
import os
import logging
import datetime
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
from utils.config import config

# Configuration du logger
logging.basicConfig(filename='dataset_creation.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class DatasetCreator:
    def __init__(self):
        """Initialiser le créateur de jeu de données"""
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
        
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Paramètres optimisés pour améliorer la détection
        self.min_neighbors = 6  # Augmenté pour réduire les faux positifs
        self.scale_factor = 1.2  # Valeur équilibrée pour vitesse/précision
        self.min_size = (80, 80)  # Taille minimale du visage à détecter (augmentée)
    
    def get_camera_source(self):
        """Retourne la source de caméra appropriée en fonction de la configuration"""
        use_droid_cam = config.get('camera.use_droid_cam', False)
        droid_cam_url = config.get('camera.droid_cam_url', 'http://192.168.1.X:4747/video')
        camera_index = config.get('camera.index', 0)
        
        if use_droid_cam and droid_cam_url:
            logging.info(f"Utilisation de DroidCam comme source: {droid_cam_url}")
            return droid_cam_url
        else:
            logging.info(f"Utilisation de la webcam par défaut: index {camera_index}")
            return camera_index
    
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
    
    def create_dataset(self, employee_id, max_images=300):
        """
        Créer un jeu de données de visages pour un employé
        
        Args:
            employee_id (int): ID de l'employé
            max_images (int): Nombre maximal d'images à capturer
        
        Returns:
            int: Nombre d'images capturées
        """
        # Créer le répertoire pour stocker les images
        path = os.path.join('data', 'faces', str(employee_id))
        os.makedirs(path, exist_ok=True)
        logging.info(f"Répertoire créé: {path}")
        
        # Créer aussi le répertoire pour les classifieurs si nécessaire
        classifiers_dir = os.path.join('data', 'classifiers')
        os.makedirs(classifiers_dir, exist_ok=True)
        logging.info(f"Répertoire classificateurs créé: {classifiers_dir}")
        
        # Démarrer la capture vidéo avec la source appropriée
        camera_source = self.get_camera_source()
        vid = cv2.VideoCapture(camera_source)
        
        if not vid.isOpened():
            logging.error(f"Impossible d'ouvrir la caméra source: {camera_source}")
            return 0
        
        num_of_images = 0
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Boucle de capture d'images
        while True:
            ret, img = vid.read()
            if not ret:
                logging.error("Échec de la capture d'image")
                break
            
            # Obtenir les dimensions de l'image
            frame_height, frame_width = img.shape[:2]
            
            # Convertir l'image en niveaux de gris
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
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
            
            # Extraire et enregistrer le visage
            new_img = None
            for (x, y, w, h) in valid_faces:
                # Dessiner un rectangle autour du visage
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(img, "Visage détecté", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0))
                cv2.putText(img, f"{num_of_images} images capturées", (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0))
                
                # Extraire la région du visage
                new_img = img[y:y+h, x:x+w]
            
            # Afficher l'image
            cv2.imshow("Capture d'images", img)
            
            # Enregistrer l'image du visage si détectée
            try:
                if new_img is not None:
                    image_path = os.path.join(path, f"{num_of_images}_{timestamp}_{employee_id}.jpg")
                    cv2.imwrite(image_path, new_img)
                    num_of_images += 1
                    logging.info(f"Image {num_of_images} capturée pour l'employé ID={employee_id}")
            except Exception as e:
                logging.error(f"Erreur lors de l'enregistrement de l'image: {e}")
            
            # Sortir si 'q' est pressé ou si le nombre maximal d'images est atteint
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27 or num_of_images >= max_images:
                break
        
        # Libérer les ressources
        vid.release()
        cv2.destroyAllWindows()
        
        logging.info(f"Jeu de données créé pour l'employé ID={employee_id} avec {num_of_images} images")
        return num_of_images


class DatasetCreatorThread(QThread):
    """Classe pour créer un jeu de données dans un thread séparé"""
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(int)
    error_signal = pyqtSignal(str)
    image_signal = pyqtSignal(QImage)  # Nouveau signal pour envoyer l'image à l'interface
    
    def __init__(self, employee_id, max_images=300):
        """
        Initialiser le thread de création de jeu de données
        
        Args:
            employee_id (int): ID de l'employé
            max_images (int): Nombre maximal d'images à capturer
        """
        super().__init__()
        self.employee_id = employee_id
        self.max_images = max_images
        self.creator = DatasetCreator()
        self.running = True
    
    def run(self):
        """Exécuter la création du jeu de données dans un thread séparé"""
        try:
            # Créer le répertoire pour stocker les images
            path = os.path.join('data', 'faces', str(self.employee_id))
            os.makedirs(path, exist_ok=True)
            logging.info(f"Répertoire créé: {path}")
            
            # Créer aussi le répertoire pour les classifieurs si nécessaire
            classifiers_dir = os.path.join('data', 'classifiers')
            os.makedirs(classifiers_dir, exist_ok=True)
            logging.info(f"Répertoire classificateurs créé: {classifiers_dir}")
            
            # Démarrer la capture vidéo avec la source appropriée
            camera_source = self.creator.get_camera_source()
            vid = cv2.VideoCapture(camera_source)
            
            if not vid.isOpened():
                self.error_signal.emit(f"Impossible d'ouvrir la caméra source: {camera_source}")
                return
            
            num_of_images = 0
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Boucle de capture d'images
            while self.running and not self.isInterruptionRequested():
                ret, img = vid.read()
                if not ret:
                    self.error_signal.emit("Échec de la capture d'image")
                    break
                
                # Obtenir les dimensions de l'image
                frame_height, frame_width = img.shape[:2]
                
                # Convertir l'image en niveaux de gris
                gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Améliorer le contraste
                gray_img = cv2.equalizeHist(gray_img)
                
                # Détecter les visages avec des paramètres optimisés
                faces = self.creator.face_cascade.detectMultiScale(
                    gray_img, 
                    scaleFactor=self.creator.scale_factor, 
                    minNeighbors=self.creator.min_neighbors,
                    minSize=self.creator.min_size
                )
                
                # Filtrer les fausses détections
                valid_faces = []
                for (x, y, w, h) in faces:
                    if self.creator.check_false_detection(frame_height, frame_width, x, y, w, h):
                        valid_faces.append((x, y, w, h))
                
                # Extraire et enregistrer le visage
                new_img = None
                for (x, y, w, h) in valid_faces:
                    # Dessiner un rectangle autour du visage
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(img, "Visage détecté", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0))
                    cv2.putText(img, f"{num_of_images} images capturées", (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0))
                    
                    # Extraire la région du visage
                    new_img = img[y:y+h, x:x+w]
                
                # Convertir l'image pour l'envoi à l'interface Qt
                h, w, ch = img.shape
                if ch == 3:  # Si l'image est en RGB
                    rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    qt_image = QImage(rgb_image.data, w, h, w * ch, QImage.Format_RGB888)
                    # Émettre le signal d'image
                    self.image_signal.emit(qt_image)
                
                # Enregistrer l'image du visage si détectée
                try:
                    if new_img is not None:
                        image_path = os.path.join(path, f"{num_of_images}_{timestamp}_{self.employee_id}.jpg")
                        cv2.imwrite(image_path, new_img)
                        num_of_images += 1
                        # Émettre le signal de progression
                        self.progress_signal.emit(num_of_images)
                except Exception as e:
                    self.error_signal.emit(f"Erreur lors de l'enregistrement de l'image: {e}")
                
                # Attendre un court instant
                cv2.waitKey(30)
                
                # Sortir si le nombre maximal d'images est atteint
                if num_of_images >= self.max_images:
                    break
            
            # Libérer les ressources
            vid.release()
            
            # Émettre le signal de fin
            self.finished_signal.emit(num_of_images)
        
        except Exception as e:
            self.error_signal.emit(f"Erreur inattendue: {e}")
    
    def stop(self):
        """Arrêter la capture d'images"""
        self.running = False
        self.requestInterruption()
        self.wait()

# Instance globale du créateur de jeu de données
dataset_creator = DatasetCreator() 