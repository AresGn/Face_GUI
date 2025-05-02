import os
import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QFormLayout, QSpinBox, QGroupBox, QMessageBox,
                             QProgressBar, QComboBox, QFrame, QGridLayout, QSizePolicy,
                             QFileDialog, QRadioButton, QButtonGroup)
from PyQt5.QtGui import QFont, QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QTimer
import cv2

# Importer les modules core et database
from core.dataset_creator import DatasetCreatorThread
from core.classifier import ClassifierTrainerThread
from database.db_manager import db_manager
from utils.video_training import VideoTrainerThread

# Configuration du logger
logging.basicConfig(filename='registration.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class RegistrationPage(QWidget):
    """Page d'enregistrement des employés"""
    
    def __init__(self):
        """Initialiser la page d'enregistrement"""
        super().__init__()
        
        # Initialiser les variables
        self.employee_id = None
        self.dataset_thread = None
        self.classifier_thread = None
        self.video_thread = None
        self.camera_preview_timer = None
        self.video_path = None
        
        # Initialiser l'interface utilisateur
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        # Créer le layout principal
        main_layout = QHBoxLayout()
        
        # Créer la section du formulaire
        form_layout = self.create_form_section()
        
        # Créer la section de capture d'image
        capture_layout = self.create_capture_section()
        
        # Ajouter les sections au layout principal
        main_layout.addLayout(form_layout, 1)  # 1 est le facteur d'étirement
        main_layout.addLayout(capture_layout, 1)
        
        # Définir le layout pour ce widget
        self.setLayout(main_layout)
    
    def create_form_section(self):
        """Créer la section du formulaire d'enregistrement"""
        form_layout = QVBoxLayout()
        
        # Titre de la section
        title_label = QLabel("Enregistrement d'un nouvel employé")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title_label)
        
        # Groupe pour les informations de l'employé
        employee_group = QGroupBox("Informations de l'employé")
        employee_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                margin-top: 40px;
                padding-top: 50px;
                border: 2px solid #3867d6;
                border-radius: 10px;
            }
            QGroupBox::title {
                color: white;
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 8px 30px;
                background-color: #3867d6;
                border-radius: 6px;
                min-width: 200px;
            }
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: white;
                margin: 5px;
            }
        """)
        employee_form = QFormLayout()
        employee_form.setContentsMargins(20, 20, 20, 20)
        
        # Champs du formulaire
        self.nom_input = QLineEdit()
        self.prenom_input = QLineEdit()
        self.matricule_input = QLineEdit()
        self.poste_input = QComboBox()
        
        # Ajouter quelques postes typiques
        self.poste_input.addItems(["Opérateur", "Technicien", "Ingénieur", "Administratif", "Manager", "Directeur", "Autre"])
        self.poste_input.setEditable(True)
        
        # Ajouter les champs au formulaire
        employee_form.addRow("Nom:", self.nom_input)
        employee_form.addRow("Prénom:", self.prenom_input)
        employee_form.addRow("Matricule:", self.matricule_input)
        employee_form.addRow("Poste:", self.poste_input)
        
        # Définir le layout pour le groupe
        employee_group.setLayout(employee_form)
        form_layout.addWidget(employee_group)
        
        # Groupe pour les actions
        actions_group = QGroupBox("Actions")
        actions_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                margin-top: 40px;
                padding-top: 50px;
                border: 2px solid #3867d6;
                border-radius: 10px;
            }
            QGroupBox::title {
                color: white;
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 8px 30px;
                background-color: #3867d6;
                border-radius: 6px;
                min-width: 150px;
            }
        """)
        actions_layout = QVBoxLayout()
        actions_layout.setContentsMargins(20, 20, 20, 20)
        
        # Boutons d'action
        self.register_btn = QPushButton("Enregistrer")
        self.capture_btn = QPushButton("Capturer les images")
        self.select_video_btn = QPushButton("Sélectionner une vidéo")
        self.reset_btn = QPushButton("Réinitialiser")
        
        # Désactiver les boutons de capture au départ
        self.capture_btn.setEnabled(False)
        self.select_video_btn.setEnabled(False)
        
        # Connecter les boutons aux fonctions
        self.register_btn.clicked.connect(self.register_employee)
        self.capture_btn.clicked.connect(self.start_capture)
        self.select_video_btn.clicked.connect(self.select_video)
        self.reset_btn.clicked.connect(self.reset_form)
        
        # Ajouter les boutons au layout des actions
        actions_layout.addWidget(self.register_btn)
        actions_layout.addWidget(self.capture_btn)
        actions_layout.addWidget(self.select_video_btn)
        actions_layout.addWidget(self.reset_btn)
        
        # Définir le layout pour le groupe des actions
        actions_group.setLayout(actions_layout)
        form_layout.addWidget(actions_group)
        
        # Ajouter un espace extensible
        form_layout.addStretch()
        
        return form_layout
    
    def create_capture_section(self):
        """Créer la section de capture d'image"""
        capture_layout = QVBoxLayout()
        
        # Titre de la section
        title_label = QLabel("Capture d'images")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        capture_layout.addWidget(title_label)
        
        # Groupe pour le mode de capture
        capture_mode_group = QGroupBox("Mode de capture")
        capture_mode_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                margin-top: 20px;
                padding-top: 40px;
                border: 2px solid #3867d6;
                border-radius: 10px;
            }
            QGroupBox::title {
                color: white;
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 6px 20px;
                background-color: #3867d6;
                border-radius: 6px;
                min-width: 150px;
            }
            QRadioButton {
                color: white;
                font-size: 14px;
                font-weight: bold;
                margin: 5px;
            }
        """)
        
        capture_mode_layout = QHBoxLayout()
        self.camera_radio = QRadioButton("Webcam")
        self.video_radio = QRadioButton("Vidéo")
        self.camera_radio.setChecked(True)
        
        # Groupe de boutons radio
        self.capture_mode_group = QButtonGroup()
        self.capture_mode_group.addButton(self.camera_radio, 1)
        self.capture_mode_group.addButton(self.video_radio, 2)
        
        capture_mode_layout.addWidget(self.camera_radio)
        capture_mode_layout.addWidget(self.video_radio)
        capture_mode_group.setLayout(capture_mode_layout)
        capture_layout.addWidget(capture_mode_group)
        
        # Cadre pour l'aperçu de la caméra
        self.camera_frame = QLabel()
        self.camera_frame.setAlignment(Qt.AlignCenter)
        self.camera_frame.setMinimumSize(320, 240)
        self.camera_frame.setFrameShape(QFrame.Box)
        self.camera_frame.setText("L'aperçu de la caméra sera affiché ici")
        self.camera_frame.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        capture_layout.addWidget(self.camera_frame)
        
        # Groupe pour les informations de capture
        capture_info_group = QGroupBox("Informations de capture")
        capture_info_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                margin-top: 40px;
                padding-top: 50px;
                border: 2px solid #3867d6;
                border-radius: 10px;
            }
            QGroupBox::title {
                color: white;
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 8px 30px;
                background-color: #3867d6;
                border-radius: 6px;
                min-width: 200px;
            }
        """)
        capture_info_layout = QFormLayout()
        capture_info_layout.setContentsMargins(20, 20, 20, 20)
        
        # Nombre d'images à capturer
        self.images_count = QSpinBox()
        self.images_count.setRange(50, 500)
        self.images_count.setValue(200)
        self.images_count.setSingleStep(10)
        capture_info_layout.addRow("Nombre d'images:", self.images_count)
        
        # Barre de progression
        self.capture_progress = QProgressBar()
        self.capture_progress.setRange(0, 100)
        self.capture_progress.setValue(0)
        capture_info_layout.addRow("Progression:", self.capture_progress)
        
        # Barre de progression pour l'entraînement
        self.training_progress = QProgressBar()
        self.training_progress.setRange(0, 100)
        self.training_progress.setValue(0)
        capture_info_layout.addRow("Entraînement:", self.training_progress)
        
        # Statut
        self.status_label = QLabel("En attente")
        self.status_label.setStyleSheet("color: white; font-weight: bold;")
        capture_info_layout.addRow("Statut:", self.status_label)
        
        # Définir le layout pour le groupe des informations de capture
        capture_info_group.setLayout(capture_info_layout)
        capture_layout.addWidget(capture_info_group)
        
        # Ajouter un espace extensible
        capture_layout.addStretch()
        
        # Connecter les boutons radio aux fonctions
        self.camera_radio.toggled.connect(self.update_capture_mode)
        self.video_radio.toggled.connect(self.update_capture_mode)
        
        return capture_layout
    
    def update_capture_mode(self):
        """Mettre à jour le mode de capture en fonction du bouton radio sélectionné"""
        if self.camera_radio.isChecked():
            self.capture_btn.setEnabled(self.employee_id is not None)
            self.select_video_btn.setEnabled(False)
        else:  # Mode vidéo
            self.capture_btn.setEnabled(False)
            self.select_video_btn.setEnabled(self.employee_id is not None)
            
        # Réinitialiser le chemin de la vidéo si on passe en mode webcam
        if self.camera_radio.isChecked():
            self.video_path = None
    
    def select_video(self):
        """Sélectionner une vidéo pour l'entraînement"""
        if self.employee_id is None:
            QMessageBox.warning(self, "Avertissement", "Vous devez d'abord enregistrer un employé.")
            return
        
        # Ouvrir un sélecteur de fichier
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Vidéos (*.mp4 *.avi *.mov *.mkv)")
        file_dialog.setViewMode(QFileDialog.Detail)
        
        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                self.video_path = file_paths[0]
                self.status_label.setText(f"Vidéo sélectionnée: {os.path.basename(self.video_path)}")
                
                # Permettre de lancer le traitement de la vidéo
                self.capture_btn.setEnabled(True)
                
                # Tester l'ouverture de la vidéo
                try:
                    cap = cv2.VideoCapture(self.video_path)
                    if not cap.isOpened():
                        QMessageBox.warning(self, "Erreur", "Impossible d'ouvrir la vidéo sélectionnée.")
                        self.video_path = None
                        self.capture_btn.setEnabled(False)
                        return
                    
                    # Récupérer la première image pour l'aperçu
                    ret, frame = cap.read()
                    if ret:
                        # Convertir l'image pour l'affichage dans Qt
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        h, w, ch = rgb_frame.shape
                        bytes_per_line = ch * w
                        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                        
                        # Afficher l'image dans le cadre
                        self.update_camera_preview(qt_image)
                    
                    # Libérer les ressources
                    cap.release()
                    
                except Exception as e:
                    QMessageBox.warning(self, "Erreur", f"Erreur lors de l'ouverture de la vidéo: {str(e)}")
                    self.video_path = None
                    self.capture_btn.setEnabled(False)
    
    def register_employee(self):
        """Enregistrer un nouvel employé dans la base de données"""
        # Récupérer les valeurs des champs
        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()
        matricule = self.matricule_input.text().strip()
        poste = self.poste_input.currentText().strip()
        
        # Vérifier que tous les champs sont remplis
        if not (nom and prenom and matricule and poste):
            QMessageBox.warning(self, "Avertissement", "Tous les champs sont obligatoires.")
            return
        
        # Enregistrer l'employé dans la base de données
        try:
            employee_id = db_manager.add_employee(nom, prenom, matricule, poste)
            if employee_id:
                self.employee_id = employee_id
                QMessageBox.information(self, "Succès", f"Employé enregistré avec succès (ID: {employee_id}).")
                
                # Activer le bouton approprié selon le mode de capture
                if self.camera_radio.isChecked():
                    self.capture_btn.setEnabled(True)
                else:
                    self.select_video_btn.setEnabled(True)
                
                # Désactiver le bouton d'enregistrement
                self.register_btn.setEnabled(False)
                
                # Journal
                logging.info(f"Employé enregistré: ID={employee_id}, Nom={nom}, Prénom={prenom}, Matricule={matricule}, Poste={poste}")
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement de l'employé.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement de l'employé: {str(e)}")
            logging.error(f"Erreur lors de l'enregistrement de l'employé: {e}")
    
    def start_capture(self):
        """Démarrer la capture d'images ou le traitement de la vidéo"""
        if self.employee_id is None:
            QMessageBox.warning(self, "Avertissement", "Vous devez d'abord enregistrer un employé.")
            return
        
        # Mode de capture
        if self.camera_radio.isChecked() and not self.video_path:
            # Mode webcam
            self.start_webcam_capture()
        else:
            # Mode vidéo
            self.start_video_processing()
    
    def start_webcam_capture(self):
        """Démarrer la capture d'images à partir de la webcam"""
        try:
            # Nombre d'images à capturer
            max_images = self.images_count.value()
            
            # Mettre à jour le statut
            self.status_label.setText("Capture en cours...")
            
            # Désactiver les boutons pendant la capture
            self.capture_btn.setEnabled(False)
            self.select_video_btn.setEnabled(False)
            self.register_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
            
            # Réinitialiser les barres de progression
            self.capture_progress.setValue(0)
            self.training_progress.setValue(0)
            
            # Créer et démarrer le thread de capture
            self.dataset_thread = DatasetCreatorThread(self.employee_id, max_images)
            
            # Connecter les signaux
            self.dataset_thread.progress_signal.connect(self.update_capture_progress)
            self.dataset_thread.finished_signal.connect(self.capture_finished)
            self.dataset_thread.error_signal.connect(self.show_error)
            self.dataset_thread.image_signal.connect(self.update_camera_preview)
            
            # Démarrer le thread
            self.dataset_thread.start()
            
            # Journal
            logging.info(f"Capture démarrée pour l'employé ID={self.employee_id}, {max_images} images")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du démarrage de la capture: {str(e)}")
            logging.error(f"Erreur lors du démarrage de la capture: {e}")
            
            # Réactiver les boutons
            self.capture_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)
    
    def start_video_processing(self):
        """Démarrer le traitement de la vidéo sélectionnée"""
        if not self.video_path:
            QMessageBox.warning(self, "Avertissement", "Vous devez d'abord sélectionner une vidéo.")
            return
        
        try:
            # Nombre d'images à extraire
            max_images = self.images_count.value()
            
            # Mettre à jour le statut
            self.status_label.setText("Traitement de la vidéo en cours...")
            
            # Désactiver les boutons pendant le traitement
            self.capture_btn.setEnabled(False)
            self.select_video_btn.setEnabled(False)
            self.register_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
            
            # Réinitialiser les barres de progression
            self.capture_progress.setValue(0)
            self.training_progress.setValue(0)
            
            # Créer et démarrer le thread de traitement vidéo
            self.video_thread = VideoTrainerThread(self.video_path, self.employee_id, max_images)
            
            # Connecter les signaux
            self.video_thread.progress_signal.connect(self.update_capture_progress)
            self.video_thread.finished_signal.connect(self.capture_finished)
            self.video_thread.error_signal.connect(self.show_error)
            self.video_thread.frame_signal.connect(self.update_camera_preview)
            
            # Démarrer le thread
            self.video_thread.start()
            
            # Journal
            logging.info(f"Traitement vidéo démarré pour l'employé ID={self.employee_id}, {max_images} images, vidéo: {self.video_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du démarrage du traitement vidéo: {str(e)}")
            logging.error(f"Erreur lors du démarrage du traitement vidéo: {e}")
            
            # Réactiver les boutons
            self.capture_btn.setEnabled(True)
            self.select_video_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)
    
    def update_capture_progress(self, count):
        """Mettre à jour la barre de progression de la capture"""
        max_count = self.images_count.value()
        progress = int((count / max_count) * 100)
        self.capture_progress.setValue(progress)
        self.status_label.setText(f"Capture en cours: {count}/{max_count} images")
    
    def capture_finished(self, count):
        """Traiter la fin de la capture d'images"""
        self.status_label.setText(f"Capture terminée: {count} images capturées")
        
        # Désactiver les boutons de capture
        self.capture_btn.setEnabled(False)
        self.select_video_btn.setEnabled(False)
        
        # Afficher un message de succès
        QMessageBox.information(self, "Succès", f"Capture terminée avec {count} images.")
        
        # Journal
        logging.info(f"Capture terminée pour l'employé ID={self.employee_id}, {count} images")
        
        # Lancer l'entraînement du modèle
        self.train_model()
    
    def train_model(self):
        """Entraîner le modèle de reconnaissance faciale"""
        if self.employee_id is None:
            QMessageBox.warning(self, "Avertissement", "Vous devez d'abord enregistrer un employé.")
            return
        
        try:
            # Mettre à jour le statut
            self.status_label.setText("Entraînement du modèle en cours...")
            
            # Réinitialiser la barre de progression
            self.training_progress.setValue(0)
            
            # Créer et démarrer le thread d'entraînement
            self.classifier_thread = ClassifierTrainerThread(self.employee_id)
            
            # Connecter les signaux
            self.classifier_thread.progress_signal.connect(self.update_training_progress)
            self.classifier_thread.finished_signal.connect(self.training_finished)
            self.classifier_thread.error_signal.connect(self.show_error)
            
            # Démarrer le thread
            self.classifier_thread.start()
            
            # Journal
            logging.info(f"Entraînement démarré pour l'employé ID={self.employee_id}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du démarrage de l'entraînement: {str(e)}")
            logging.error(f"Erreur lors du démarrage de l'entraînement: {e}")
            
            # Réactiver le bouton de réinitialisation
            self.reset_btn.setEnabled(True)
    
    def update_training_progress(self, progress):
        """Mettre à jour la barre de progression de l'entraînement"""
        self.training_progress.setValue(progress)
    
    def training_finished(self, success):
        """Traiter la fin de l'entraînement du modèle"""
        if success:
            self.status_label.setText("Entraînement terminé avec succès")
            
            # Afficher un message de succès
            QMessageBox.information(self, "Succès", "Entraînement du modèle terminé avec succès.")
            
            # Journal
            logging.info(f"Entraînement terminé avec succès pour l'employé ID={self.employee_id}")
        else:
            self.status_label.setText("Erreur lors de l'entraînement")
            
            # Afficher un message d'erreur
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'entraînement du modèle.")
            
            # Journal
            logging.error(f"Erreur lors de l'entraînement pour l'employé ID={self.employee_id}")
        
        # Réactiver le bouton de réinitialisation
        self.reset_btn.setEnabled(True)
    
    def show_error(self, error_message):
        """Afficher un message d'erreur"""
        # Mettre à jour le statut
        self.status_label.setText(f"Erreur: {error_message}")
        
        # Afficher un message d'erreur
        QMessageBox.critical(self, "Erreur", error_message)
        
        # Journal
        logging.error(f"Erreur: {error_message}")
        
        # Réactiver les boutons
        self.reset_btn.setEnabled(True)
    
    def reset_form(self):
        """Réinitialiser le formulaire et les variables"""
        # Stopper les threads en cours si nécessaire
        if self.dataset_thread and self.dataset_thread.isRunning():
            self.dataset_thread.stop()
            self.dataset_thread = None
        
        if self.classifier_thread and self.classifier_thread.isRunning():
            self.classifier_thread.stop()
            self.classifier_thread = None
            
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.stop()
            self.video_thread = None
        
        # Réinitialiser les champs du formulaire
        self.nom_input.clear()
        self.prenom_input.clear()
        self.matricule_input.clear()
        self.poste_input.setCurrentIndex(0)
        
        # Réinitialiser les barres de progression
        self.capture_progress.setValue(0)
        self.training_progress.setValue(0)
        
        # Réinitialiser le statut
        self.status_label.setText("En attente")
        
        # Réinitialiser les variables
        self.employee_id = None
        self.video_path = None
        
        # Réinitialiser l'aperçu de la caméra
        self.camera_frame.setText("L'aperçu de la caméra sera affiché ici")
        
        # Activer/désactiver les boutons
        self.register_btn.setEnabled(True)
        self.capture_btn.setEnabled(False)
        self.select_video_btn.setEnabled(False)
        
        # Réinitialiser le mode de capture
        self.camera_radio.setChecked(True)
        
        # Journal
        logging.info("Formulaire réinitialisé")
    
    def update_camera_preview(self, image):
        """Mettre à jour l'aperçu de la caméra"""
        # Redimensionner l'image pour l'adapter au cadre
        scaled_pixmap = QPixmap.fromImage(image).scaled(
            self.camera_frame.width(),
            self.camera_frame.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.camera_frame.setPixmap(scaled_pixmap)
    
    def closeEvent(self, event):
        """Gérer l'événement de fermeture de la page"""
        # Arrêter les threads en cours
        if self.dataset_thread and self.dataset_thread.isRunning():
            self.dataset_thread.stop()
        
        if self.classifier_thread and self.classifier_thread.isRunning():
            self.classifier_thread.stop()
            
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.stop()
        
        # Accepter l'événement
        event.accept() 