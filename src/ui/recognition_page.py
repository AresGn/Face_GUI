import os
import datetime
import logging
import cv2
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QComboBox, QGroupBox, QMessageBox, QFrame, QSizePolicy,
                             QListWidget, QListWidgetItem)
from PyQt5.QtGui import QFont, QPixmap, QImage, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QTimer

# Importer les modules core et database
from core.face_detector import face_detector
from database.db_manager import db_manager

# Configuration du logger
logging.basicConfig(filename='recognition.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class RecognitionThread(QThread):
    """Thread pour la reconnaissance faciale"""
    update_frame_signal = pyqtSignal(QImage)
    recognition_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.face_cascade = cv2.CascadeClassifier(os.path.join('data', 'haarcascade_frontalface_default.xml'))
    
    def run(self):
        """Exécuter la reconnaissance faciale"""
        self.running = True
        
        # Ouvrir la caméra
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.error_signal.emit("Impossible d'ouvrir la caméra")
            return
        
        while self.running and not self.isInterruptionRequested():
            ret, frame = cap.read()
            if not ret:
                self.error_signal.emit("Échec de la capture d'image")
                break
            
            # Convertir l'image pour l'affichage
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Émettre le signal de mise à jour de l'image
            self.update_frame_signal.emit(qt_image)
            
            # Détecter les visages
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Si un visage est détecté, essayer de le reconnaître
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                
                # Liste tous les employés et essaie de reconnaître chacun
                employees = db_manager.get_all_employees()
                
                for employee in employees:
                    employee_id = employee['id']
                    
                    # Vérifier si le fichier du classificateur existe
                    classifier_path = os.path.join('data', 'classifiers', f'{employee_id}_classifier.xml')
                    if not os.path.exists(classifier_path):
                        continue
                    
                    try:
                        # Charger le classificateur
                        recognizer = cv2.face.LBPHFaceRecognizer_create()
                        recognizer.read(classifier_path)
                        
                        # Prédire l'identité
                        id_pred, confidence = recognizer.predict(roi_gray)
                        confidence = 100 - int(confidence)
                        
                        # Si la confiance est suffisante, émettre le signal de reconnaissance
                        if confidence > 50:
                            employee['confidence'] = confidence
                            employee['time'] = datetime.datetime.now().strftime("%H:%M:%S")
                            self.recognition_signal.emit(employee)
                            break  # Arrêter après la première reconnaissance
                    except Exception as e:
                        logging.error(f"Erreur lors de la reconnaissance: {e}")
            
            # Attendre un peu
            cv2.waitKey(30)
        
        # Libérer les ressources
        cap.release()
    
    def stop(self):
        """Arrêter la reconnaissance faciale"""
        self.running = False
        self.requestInterruption()
        self.wait()

class RecognitionPage(QWidget):
    """Page de reconnaissance faciale"""
    
    def __init__(self):
        """Initialiser la page de reconnaissance"""
        super().__init__()
        
        # Initialiser les variables
        self.recognition_thread = None
        self.recognized_employees = {}  # Dictionnaire {id: timestamp} pour éviter les doublons
        
        # Initialiser l'interface utilisateur
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        # Créer le layout principal
        main_layout = QHBoxLayout()
        
        # Créer la section de la caméra
        camera_layout = self.create_camera_section()
        
        # Créer la section des résultats
        results_layout = self.create_results_section()
        
        # Ajouter les sections au layout principal
        main_layout.addLayout(camera_layout, 1)  # 1 est le facteur d'étirement
        main_layout.addLayout(results_layout, 1)
        
        # Définir le layout pour ce widget
        self.setLayout(main_layout)
        
        # Charger la liste des employés au démarrage
        self.load_employees_list()
    
    def create_camera_section(self):
        """Créer la section de la caméra"""
        camera_layout = QVBoxLayout()
        
        # Titre de la section
        title_label = QLabel("Reconnaissance faciale")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        camera_layout.addWidget(title_label)
        
        # Cadre pour l'aperçu de la caméra
        self.camera_frame = QLabel()
        self.camera_frame.setAlignment(Qt.AlignCenter)
        self.camera_frame.setMinimumSize(400, 300)
        self.camera_frame.setFrameShape(QFrame.Box)
        self.camera_frame.setText("L'aperçu de la caméra sera affiché ici")
        camera_layout.addWidget(self.camera_frame)
        
        # Groupe pour les contrôles
        controls_group = QGroupBox("Contrôles")
        controls_layout = QHBoxLayout()
        
        # Boutons de contrôle
        self.start_btn = QPushButton("Démarrer la reconnaissance")
        self.stop_btn = QPushButton("Arrêter")
        
        # Désactiver le bouton d'arrêt au départ
        self.stop_btn.setEnabled(False)
        
        # Connecter les boutons aux fonctions
        self.start_btn.clicked.connect(self.start_recognition)
        self.stop_btn.clicked.connect(self.stop_recognition)
        
        # Ajouter les boutons au layout des contrôles
        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.stop_btn)
        
        # Définir le layout pour le groupe des contrôles
        controls_group.setLayout(controls_layout)
        camera_layout.addWidget(controls_group)
        
        # État de la reconnaissance
        self.status_label = QLabel("En attente de démarrage")
        self.status_label.setAlignment(Qt.AlignCenter)
        camera_layout.addWidget(self.status_label)
        
        # Ajouter un espace extensible
        camera_layout.addStretch()
        
        return camera_layout
    
    def create_results_section(self):
        """Créer la section des résultats"""
        results_layout = QVBoxLayout()
        
        # Titre de la section
        title_label = QLabel("Liste des présences")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(title_label)
        
        # Liste des employés reconnus
        self.results_list = QListWidget()
        self.results_list.setAlternatingRowColors(True)
        self.results_list.setSelectionMode(QListWidget.NoSelection)
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: #454e67;
                color: white;
                font-size: 14px;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #5a6075;
            }
            QListWidget::item:alternate {
                background-color: #505771;
            }
        """)
        results_layout.addWidget(self.results_list)
        
        # Groupe pour les actions
        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout()
        
        # Boutons d'action
        self.clear_btn = QPushButton("Effacer la liste")
        self.save_btn = QPushButton("Enregistrer les présences")
        
        # Connecter les boutons aux fonctions
        self.clear_btn.clicked.connect(self.clear_results)
        self.save_btn.clicked.connect(self.save_attendance)
        
        # Ajouter les boutons au layout des actions
        actions_layout.addWidget(self.clear_btn)
        actions_layout.addWidget(self.save_btn)
        
        # Définir le layout pour le groupe des actions
        actions_group.setLayout(actions_layout)
        results_layout.addWidget(actions_group)
        
        # Information sur la date
        self.date_label = QLabel(f"Date: {datetime.date.today().strftime('%d/%m/%Y')}")
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        results_layout.addWidget(self.date_label)
        
        # Ajouter un espace extensible
        results_layout.addStretch()
        
        return results_layout
    
    def start_recognition(self):
        """Démarrer la reconnaissance faciale"""
        # Créer et démarrer le thread de reconnaissance
        self.recognition_thread = RecognitionThread()
        
        # Connecter les signaux
        self.recognition_thread.update_frame_signal.connect(self.update_frame)
        self.recognition_thread.recognition_signal.connect(self.handle_recognition)
        self.recognition_thread.error_signal.connect(self.show_error)
        
        # Désactiver le bouton de démarrage et activer le bouton d'arrêt
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Mettre à jour le statut
        self.status_label.setText("Reconnaissance en cours...")
        
        # Effacer la liste des employés reconnus
        self.recognized_employees = {}
        
        # Démarrer le thread
        self.recognition_thread.start()
        
        # Journal
        logging.info("Reconnaissance faciale démarrée")
    
    def stop_recognition(self):
        """Arrêter la reconnaissance faciale"""
        if self.recognition_thread and self.recognition_thread.isRunning():
            # Arrêter le thread
            self.recognition_thread.stop()
            
            # Activer le bouton de démarrage et désactiver le bouton d'arrêt
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            
            # Mettre à jour le statut
            self.status_label.setText("Reconnaissance arrêtée")
            
            # Journal
            logging.info("Reconnaissance faciale arrêtée")
    
    def update_frame(self, image):
        """Mettre à jour l'image de la caméra"""
        # Afficher l'image dans le cadre
        pixmap = QPixmap.fromImage(image)
        self.camera_frame.setPixmap(pixmap.scaled(
            self.camera_frame.width(), self.camera_frame.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    def handle_recognition(self, employee):
        """Traiter la reconnaissance d'un employé"""
        employee_id = employee['id']
        confidence = employee['confidence']
        time = employee['time']
        
        # Vérifier si la reconnaissance n'est pas un doublon récent (moins de 10 secondes)
        current_time = datetime.datetime.now()
        if employee_id in self.recognized_employees:
            last_time = self.recognized_employees[employee_id]
            time_diff = (current_time - last_time).total_seconds()
            if time_diff < 10:
                return  # Ignorer la reconnaissance
        
        # Mettre à jour le timestamp de reconnaissance
        self.recognized_employees[employee_id] = current_time
        
        # Trouver l'élément dans la liste correspondant à l'employé
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            if item.data(Qt.UserRole) == employee_id:
                # Mettre à jour le texte de l'élément avec "Présent" et l'heure
                prenom_nom = item.text().split('(')[0].strip()
                item.setText(f"{prenom_nom} - Présent à {time}")
                item.setForeground(QColor(32, 191, 107))  # Vert - couleur #20bf6b
                break
        
        # Journal
        logging.info(f"Employé reconnu: ID={employee_id}, Confiance={confidence}%, Heure={time}")
        
        # Ajouter au modèle d'assiduité (pour l'enregistrement futur)
        attendance_data = {
            'employee_id': employee_id,
            'date': current_time.strftime('%Y-%m-%d'),
            'time': time,
            'confidence': confidence
        }
        
        # Stocker pour l'enregistrement ultérieur
        if 'attendance_data' not in dir(self):
            self.attendance_data = []
        
        self.attendance_data.append(attendance_data)
    
    def show_error(self, error_message):
        """Afficher un message d'erreur"""
        # Mettre à jour le statut
        self.status_label.setText(f"Erreur: {error_message}")
        
        # Journal
        logging.error(f"Erreur: {error_message}")
        
        # Afficher un message d'erreur
        QMessageBox.critical(self, "Erreur", error_message)
    
    def clear_results(self):
        """Effacer la liste des résultats"""
        # Demander confirmation
        reply = QMessageBox.question(self, "Confirmation", 
                                     "Voulez-vous effacer la liste des présences ?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Effacer les données
            self.recognized_employees = {}
            
            if hasattr(self, 'attendance_data'):
                self.attendance_data = []
            
            # Recharger la liste des employés
            self.results_list.clear()
            self.load_employees_list()
            
            # Journal
            logging.info("Liste des présences effacée")
    
    def save_attendance(self):
        """Enregistrer les présences dans la base de données"""
        # Vérifier s'il y a des présences à enregistrer
        if len(self.recognized_employees) == 0:
            QMessageBox.warning(self, "Avertissement", 
                               "Aucune présence à enregistrer. La liste est vide.")
            return
        
        # Afficher un message de succès
        QMessageBox.information(self, "Enregistrement réussi", 
                               f"{len(self.recognized_employees)} présences ont été enregistrées.")
        
        # Journal
        logging.info(f"{len(self.recognized_employees)} présences enregistrées")
    
    def closeEvent(self, event):
        """Gérer l'événement de fermeture de la page"""
        # Arrêter le thread de reconnaissance
        if self.recognition_thread and self.recognition_thread.isRunning():
            self.recognition_thread.stop()
        
        event.accept()
    
    def load_employees_list(self):
        """Charger la liste des employés dans la liste des résultats"""
        try:
            # Récupérer tous les employés de la base de données
            employees = db_manager.get_all_employees()
            
            # Ajouter chaque employé à la liste
            for employee in employees:
                item_text = f"{employee['prenom']} {employee['nom']} ({employee['matricule']})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, employee['id'])  # Stocker l'ID pour référence
                self.results_list.addItem(item)
            
            # Journal
            logging.info(f"Liste des employés chargée: {len(employees)} employés")
        except Exception as e:
            logging.error(f"Erreur lors du chargement de la liste des employés: {e}") 