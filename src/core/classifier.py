import numpy as np
import os
import cv2
import logging
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal

# Configuration du logger
logging.basicConfig(filename='classifier.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class FaceClassifier:
    def __init__(self):
        """Initialiser le classificateur de visage"""
        # S'assurer que le répertoire des classificateurs existe
        os.makedirs(os.path.join('data', 'classifiers'), exist_ok=True)
    
    def train_classifier(self, employee_id):
        """
        Entraîner un classificateur pour un employé spécifique
        
        Args:
            employee_id (int): ID de l'employé
            
        Returns:
            bool: True si l'entraînement a réussi, False sinon
        """
        try:
            # Chemin vers les images du visage de l'employé
            path = os.path.join('data', 'faces', str(employee_id))
            
            # Vérifier si le répertoire existe
            if not os.path.exists(path):
                logging.error(f"Le répertoire {path} n'existe pas")
                return False
            
            # Lister tous les fichiers d'images
            pictures = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            if not pictures:
                logging.error(f"Aucune image trouvée dans {path}")
                return False
            
            # Préparer les données d'entraînement
            faces = []
            ids = []
            
            # Charger chaque image et l'ajouter aux données d'entraînement
            for pic in pictures:
                img_path = os.path.join(path, pic)
                try:
                    # Charger et convertir l'image en niveaux de gris
                    img = Image.open(img_path).convert('L')
                    # Convertir l'image en tableau numpy
                    img_np = np.array(img, 'uint8')
                    
                    # Extraction de l'ID plus flexible
                    try:
                        # Essayer d'extraire l'ID à partir du nom du fichier
                        # Formats supportés: "num_timestamp_employee_id.jpg" ou "image_XXXX.jpg"
                        if '_' in pic:
                            # Format: "num_timestamp_employee_id.jpg"
                            face_id = int(pic.split('_')[0])
                        else:
                            # Format alternatif (ex: "image_0001.jpg")
                            face_id = employee_id
                    except (ValueError, IndexError):
                        # En cas d'erreur, utiliser l'ID de l'employé
                        logging.warning(f"Format de nom de fichier non reconnu: {pic}, utilisation de l'ID employé")
                        face_id = employee_id
                    
                    # Ajouter l'image et l'ID aux listes
                    faces.append(img_np)
                    ids.append(face_id)
                except Exception as e:
                    logging.error(f"Erreur lors du traitement de l'image {img_path}: {e}")
            
            # Vérifier si des données ont été chargées
            if not faces:
                logging.error("Aucune donnée d'entraînement valide")
                return False
            
            # Convertir la liste des IDs en tableau numpy
            ids = np.array(ids)
            
            # Créer et entraîner le classificateur
            try:
                logging.info(f"Début de l'entraînement avec {len(faces)} images et {len(ids)} IDs")
                logging.debug(f"Types de données: faces={type(faces[0])}, ids={type(ids[0])}")
                
                # Vérifier que toutes les images ont la même taille
                shapes = [face.shape for face in faces]
                if len(set(shapes)) > 1:
                    shapes_str = ', '.join([f"{s}" for s in set(shapes)])
                    logging.warning(f"Attention: images de tailles différentes: {shapes_str}")
                
                # Vérifier que les ids sont tous identiques
                unique_ids = set(ids)
                logging.info(f"IDs uniques: {unique_ids}")
                
                # Créer et entraîner le classificateur
                clf = cv2.face.LBPHFaceRecognizer_create()
                clf.train(faces, ids)
                
                # Enregistrer le classificateur
                classifier_path = os.path.join('data', 'classifiers', f'{employee_id}_classifier.xml')
                clf.write(classifier_path)
                
                logging.info(f"Classificateur entraîné et enregistré pour l'employé ID={employee_id}")
                return True
            except Exception as e:
                error_msg = f"Erreur pendant l'entraînement du modèle: {str(e)}"
                logging.error(error_msg)
                logging.exception("Détail de l'erreur:")
                return False
        
        except Exception as e:
            logging.error(f"Erreur lors de l'entraînement du classificateur: {e}")
            return False


class ClassifierTrainerThread(QThread):
    """Classe pour entraîner un classificateur dans un thread séparé"""
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool)
    error_signal = pyqtSignal(str)
    
    def __init__(self, employee_id):
        """
        Initialiser le thread d'entraînement du classificateur
        
        Args:
            employee_id (int): ID de l'employé
        """
        super().__init__()
        self.employee_id = employee_id
        self.classifier = FaceClassifier()
    
    def run(self):
        """Exécuter l'entraînement du classificateur dans un thread séparé"""
        try:
            # Émettre un signal pour indiquer le début de l'entraînement
            self.progress_signal.emit(0)
            
            # Chemin vers les images du visage de l'employé
            path = os.path.join('data', 'faces', str(self.employee_id))
            
            # Vérifier si le répertoire existe
            if not os.path.exists(path):
                error_msg = f"Le répertoire {path} n'existe pas"
                logging.error(error_msg)
                self.error_signal.emit(error_msg)
                self.finished_signal.emit(False)
                return
            
            # Lister tous les fichiers d'images
            pictures = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            if not pictures:
                error_msg = f"Aucune image trouvée dans {path}"
                logging.error(error_msg)
                self.error_signal.emit(error_msg)
                self.finished_signal.emit(False)
                return
            
            # Journaliser le nombre d'images trouvées
            logging.info(f"Nombre d'images trouvées: {len(pictures)}")
            logging.debug(f"Liste des images: {pictures[:5]}...")
            
            # Créer les répertoires nécessaires pour les classificateurs
            classifiers_dir = os.path.join('data', 'classifiers')
            os.makedirs(classifiers_dir, exist_ok=True)
            logging.info(f"Répertoire des classificateurs: {classifiers_dir}")
            
            # Préparer les données d'entraînement
            faces = []
            ids = []
            
            # Charger chaque image et l'ajouter aux données d'entraînement
            total_images = len(pictures)
            for i, pic in enumerate(pictures):
                img_path = os.path.join(path, pic)
                try:
                    # Charger et convertir l'image en niveaux de gris
                    img = Image.open(img_path).convert('L')
                    # Convertir l'image en tableau numpy
                    img_np = np.array(img, 'uint8')
                    
                    # Extraction de l'ID plus flexible
                    try:
                        # Essayer d'extraire l'ID à partir du nom du fichier
                        # Formats supportés: "num_timestamp_employee_id.jpg" ou "image_XXXX.jpg"
                        if '_' in pic:
                            # Format: "num_timestamp_employee_id.jpg"
                            face_id = int(pic.split('_')[0])
                        else:
                            # Format alternatif (ex: "image_0001.jpg")
                            face_id = self.employee_id
                    except (ValueError, IndexError):
                        # En cas d'erreur, utiliser l'ID de l'employé
                        logging.warning(f"Format de nom de fichier non reconnu: {pic}, utilisation de l'ID employé")
                        face_id = self.employee_id
                    
                    # Ajouter l'image et l'ID aux listes
                    faces.append(img_np)
                    ids.append(face_id)
                    
                    # Émettre un signal de progression
                    progress = int((i + 1) / total_images * 100)
                    self.progress_signal.emit(progress)
                except Exception as e:
                    logging.error(f"Erreur lors du traitement de l'image {img_path}: {e}")
            
            # Vérifier si des données ont été chargées
            if not faces:
                self.error_signal.emit("Aucune donnée d'entraînement valide")
                self.finished_signal.emit(False)
                return
            
            # Convertir la liste des IDs en tableau numpy
            ids = np.array(ids)
            
            # Créer et entraîner le classificateur
            try:
                logging.info(f"Début de l'entraînement avec {len(faces)} images et {len(ids)} IDs")
                logging.debug(f"Types de données: faces={type(faces[0])}, ids={type(ids[0])}")
                
                # Vérifier que toutes les images ont la même taille
                shapes = [face.shape for face in faces]
                if len(set(shapes)) > 1:
                    shapes_str = ', '.join([f"{s}" for s in set(shapes)])
                    logging.warning(f"Attention: images de tailles différentes: {shapes_str}")
                
                # Vérifier que les ids sont tous identiques
                unique_ids = set(ids)
                logging.info(f"IDs uniques: {unique_ids}")
                
                # Créer et entraîner le classificateur
                clf = cv2.face.LBPHFaceRecognizer_create()
                clf.train(faces, ids)
                
                # Enregistrer le classificateur
                classifier_path = os.path.join('data', 'classifiers', f'{self.employee_id}_classifier.xml')
                clf.write(classifier_path)
                
                logging.info(f"Classificateur entraîné et enregistré pour l'employé ID={self.employee_id}")
                self.finished_signal.emit(True)
            except Exception as e:
                error_msg = f"Erreur pendant l'entraînement du modèle: {str(e)}"
                logging.error(error_msg)
                logging.exception("Détail de l'erreur:")
                self.error_signal.emit(error_msg)
                self.finished_signal.emit(False)
                
        except Exception as e:
            error_msg = f"Erreur lors du traitement des images pour l'entraînement: {str(e)}"
            logging.error(error_msg)
            logging.exception("Détail de l'erreur:")
            self.error_signal.emit(error_msg)
            self.finished_signal.emit(False)

# Instance globale du classificateur
face_classifier = FaceClassifier() 