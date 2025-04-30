import cv2
import os
import logging
import datetime
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

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
            # Télécharger le classificateur si nécessaire (à implémenter)
            logging.warning(f"Le fichier {cascade_path} n'existe pas. Vous devez le télécharger.")
        
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
    
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
        
        # Démarrer la capture vidéo
        vid = cv2.VideoCapture(0)
        if not vid.isOpened():
            logging.error("Impossible d'ouvrir la caméra")
            return 0
        
        num_of_images = 0
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Boucle de capture d'images
        while True:
            ret, img = vid.read()
            if not ret:
                logging.error("Échec de la capture d'image")
                break
            
            # Convertir l'image en niveaux de gris
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Détecter les visages
            faces = self.face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5)
            
            # Extraire et enregistrer le visage
            new_img = None
            for (x, y, w, h) in faces:
                # Dessiner un rectangle autour du visage
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 0), 2)
                cv2.putText(img, "Visage détecté", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255))
                cv2.putText(img, f"{num_of_images} images capturées", (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255))
                
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
            
            # Démarrer la capture vidéo
            vid = cv2.VideoCapture(0)
            if not vid.isOpened():
                self.error_signal.emit("Impossible d'ouvrir la caméra")
                return
            
            num_of_images = 0
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Boucle de capture d'images
            while self.running and not self.isInterruptionRequested():
                ret, img = vid.read()
                if not ret:
                    self.error_signal.emit("Échec de la capture d'image")
                    break
                
                # Convertir l'image en niveaux de gris
                gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Détecter les visages
                faces = self.creator.face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5)
                
                # Extraire et enregistrer le visage
                new_img = None
                for (x, y, w, h) in faces:
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