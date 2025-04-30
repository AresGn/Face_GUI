import cv2
import os
import logging
from time import time
from PyQt5.QtWidgets import QMessageBox

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
            # Télécharger le classificateur si nécessaire (à implémenter)
            logging.warning(f"Le fichier {cascade_path} n'existe pas. Vous devez le télécharger.")
        
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
    
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
        
        # Ouvrir la caméra
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.error("Impossible d'ouvrir la caméra")
            if parent:
                QMessageBox.critical(parent, "Erreur", "Impossible d'ouvrir la caméra.")
            return False
        
        pred = False
        start_time = time()
        
        # Boucle principale de reconnaissance
        while True:
            ret, frame = cap.read()
            if not ret:
                logging.error("Échec de la capture d'image")
                break
            
            # Convertir l'image en niveaux de gris
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Détecter les visages
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                # Région d'intérêt (ROI) pour la reconnaissance
                roi_gray = gray[y:y+h, x:x+w]
                
                # Prédire l'identité
                id_pred, confidence = self.recognizer.predict(roi_gray)
                confidence = 100 - int(confidence)
                
                # Vérifier si le visage est reconnu
                if confidence > 50:
                    pred = True
                    text = 'Reconnu: ID=' + str(employee_id)
                    font = cv2.FONT_HERSHEY_PLAIN
                    frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    frame = cv2.putText(frame, text, (x, y-4), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
                else:
                    pred = False
                    text = "Visage inconnu"
                    font = cv2.FONT_HERSHEY_PLAIN
                    frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    frame = cv2.putText(frame, text, (x, y-4), font, 1, (0, 0, 255), 1, cv2.LINE_AA)
            
            # Afficher l'image
            cv2.imshow("Reconnaissance faciale", frame)
            
            # Vérifier si le délai d'expiration est atteint
            elapsed_time = time() - start_time
            if elapsed_time >= timeout:
                logging.info(f"Délai d'expiration atteint. Résultat: {'Reconnu' if pred else 'Non reconnu'}")
                break
            
            # Sortir si 'q' est pressé
            if cv2.waitKey(20) & 0xFF == ord('q'):
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