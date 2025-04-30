import os
import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QFormLayout, QSpinBox, QGroupBox, QMessageBox,
                             QProgressBar, QComboBox, QFrame, QGridLayout, QSizePolicy)
from PyQt5.QtGui import QFont, QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QTimer

# Importer les modules core et database
from core.dataset_creator import DatasetCreatorThread
from core.classifier import ClassifierTrainerThread
from database.db_manager import db_manager

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
        self.camera_preview_timer = None
        
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
        employee_form = QFormLayout()
        
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
        actions_layout = QVBoxLayout()
        
        # Boutons d'action
        self.register_btn = QPushButton("Enregistrer")
        self.capture_btn = QPushButton("Capturer les images")
        self.reset_btn = QPushButton("Réinitialiser")
        
        # Désactiver le bouton de capture au départ
        self.capture_btn.setEnabled(False)
        
        # Connecter les boutons aux fonctions
        self.register_btn.clicked.connect(self.register_employee)
        self.capture_btn.clicked.connect(self.start_capture)
        self.reset_btn.clicked.connect(self.reset_form)
        
        # Ajouter les boutons au layout des actions
        actions_layout.addWidget(self.register_btn)
        actions_layout.addWidget(self.capture_btn)
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
        capture_info_layout = QVBoxLayout()
        
        # Compteur d'images
        self.image_count_label = QLabel("Aucune image capturée")
        self.image_count_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        self.image_count_label.setAlignment(Qt.AlignCenter)
        capture_info_layout.addWidget(self.image_count_label)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)  # Utiliser une plage de 0-100 pour les pourcentages
        self.progress_bar.setValue(0)
        capture_info_layout.addWidget(self.progress_bar)
        
        # État de la capture
        self.status_label = QLabel("En attente de l'enregistrement d'un employé")
        self.status_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)
        capture_info_layout.addWidget(self.status_label)
        
        # Définir le layout pour le groupe des informations de capture
        capture_info_group.setLayout(capture_info_layout)
        capture_layout.addWidget(capture_info_group)
        
        # Ajouter un espace extensible
        capture_layout.addStretch()
        
        return capture_layout
    
    def register_employee(self):
        """Enregistrer un nouvel employé dans la base de données"""
        # Récupérer les valeurs des champs
        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()
        matricule = self.matricule_input.text().strip()
        poste = self.poste_input.currentText().strip()
        
        # Valider les champs
        if not nom or not prenom or not matricule or not poste:
            QMessageBox.warning(self, "Champs manquants", 
                               "Tous les champs sont obligatoires. Veuillez les remplir.")
            return
        
        # Vérifier si le matricule existe déjà
        # Cette vérification devrait être faite dans la base de données
        
        # Enregistrer l'employé dans la base de données
        self.employee_id = db_manager.add_employee(nom, prenom, matricule, poste)
        
        if self.employee_id:
            # Afficher un message de succès
            QMessageBox.information(self, "Enregistrement réussi", 
                                   f"L'employé {prenom} {nom} a été enregistré avec succès.")
            
            # Désactiver le bouton d'enregistrement et activer le bouton de capture
            self.register_btn.setEnabled(False)
            self.capture_btn.setEnabled(True)
            
            # Mettre à jour le statut
            self.status_label.setText(f"Employé enregistré. ID: {self.employee_id}")
            
            # Journal
            logging.info(f"Employé enregistré: ID={self.employee_id}, Nom={nom}, Prénom={prenom}")
        else:
            # Afficher un message d'erreur
            QMessageBox.critical(self, "Erreur d'enregistrement", 
                                "Une erreur s'est produite lors de l'enregistrement de l'employé.")
    
    def start_capture(self):
        """Démarrer la capture d'images pour l'employé enregistré"""
        if not self.employee_id:
            QMessageBox.warning(self, "Erreur", "Aucun employé enregistré. Veuillez d'abord enregistrer un employé.")
            return
        
        # Créer et démarrer le thread de capture
        self.dataset_thread = DatasetCreatorThread(self.employee_id)
        
        # Connecter les signaux
        self.dataset_thread.progress_signal.connect(self.update_capture_progress)
        self.dataset_thread.finished_signal.connect(self.capture_finished)
        self.dataset_thread.error_signal.connect(self.show_error)
        self.dataset_thread.image_signal.connect(self.update_camera_preview)
        
        # Désactiver les boutons pendant la capture
        self.capture_btn.setEnabled(False)
        self.register_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
        
        # Mettre à jour le statut
        self.status_label.setText("Capture d'images en cours...")
        
        # Démarrer le thread
        self.dataset_thread.start()
        
        # Journal
        logging.info(f"Début de la capture d'images pour l'employé ID={self.employee_id}")
    
    def update_capture_progress(self, count):
        """Mettre à jour la progression de la capture"""
        self.image_count_label.setText(f"{count} images capturées")
        
        # Mettre à jour la barre de progression (max 100%)
        if count <= 100:
            self.progress_bar.setValue(count)
        else:
            self.progress_bar.setValue(100)
    
    def capture_finished(self, count):
        """Traitement à effectuer lorsque la capture est terminée"""
        # Mettre à jour le statut
        self.status_label.setText(f"Capture terminée. {count} images capturées. Entraînement en cours...")
        
        # Activer seulement le bouton reset et désactiver capture
        self.reset_btn.setEnabled(True)
        self.capture_btn.setEnabled(False)
        
        # Journal
        logging.info(f"Capture d'images terminée pour l'employé ID={self.employee_id}. {count} images capturées.")
        
        # Lancer automatiquement l'entraînement du modèle
        self.train_model()
    
    def train_model(self):
        """Entraîner le modèle de reconnaissance faciale"""
        if not self.employee_id:
            return
        
        # Créer et démarrer le thread d'entraînement
        self.classifier_thread = ClassifierTrainerThread(self.employee_id)
        
        # Connecter les signaux
        self.classifier_thread.progress_signal.connect(self.update_training_progress)
        self.classifier_thread.finished_signal.connect(self.training_finished)
        self.classifier_thread.error_signal.connect(self.show_error)
        
        # Désactiver tous les boutons pendant l'entraînement
        self.capture_btn.setEnabled(False)
        self.register_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
        
        # Mettre à jour le statut
        self.status_label.setText("Entraînement du modèle en cours...")
        
        # Démarrer le thread
        self.classifier_thread.start()
        
        # Journal
        logging.info(f"Début de l'entraînement du modèle pour l'employé ID={self.employee_id}")
    
    def update_training_progress(self, progress):
        """Mettre à jour la progression de l'entraînement"""
        self.progress_bar.setValue(progress)
    
    def training_finished(self, success):
        """Traitement à effectuer lorsque l'entraînement est terminé"""
        # Activer le bouton de réinitialisation
        self.reset_btn.setEnabled(True)
        
        if success:
            # Mettre à jour le statut
            self.status_label.setText("Entraînement terminé avec succès.")
            
            # Journal
            logging.info(f"Entraînement terminé avec succès pour l'employé ID={self.employee_id}")
            
            # Afficher un message de succès
            QMessageBox.information(self, "Entraînement terminé", 
                                   "Le modèle de reconnaissance faciale a été entraîné avec succès.")
        else:
            # Mettre à jour le statut
            self.status_label.setText("Échec de l'entraînement.")
            
            # Journal
            logging.error(f"Échec de l'entraînement pour l'employé ID={self.employee_id}")
            
            # Afficher un message d'erreur
            QMessageBox.critical(self, "Erreur d'entraînement", 
                                "Une erreur s'est produite lors de l'entraînement du modèle.")
    
    def show_error(self, error_message):
        """Afficher un message d'erreur"""
        # Mettre à jour le statut
        self.status_label.setText(f"Erreur: {error_message}")
        
        # Journal
        logging.error(f"Erreur: {error_message}")
        
        # Afficher un message d'erreur
        QMessageBox.critical(self, "Erreur", error_message)
        
        # Activer le bouton de réinitialisation
        self.reset_btn.setEnabled(True)
    
    def reset_form(self):
        """Réinitialiser le formulaire et les ressources"""
        # Réinitialiser les champs
        self.nom_input.clear()
        self.prenom_input.clear()
        self.matricule_input.clear()
        self.poste_input.setCurrentIndex(0)
        
        # Réinitialiser les états
        self.employee_id = None
        self.image_count_label.setText("Aucune image capturée")
        self.progress_bar.setValue(0)
        self.status_label.setText("En attente de l'enregistrement d'un employé")
        self.camera_frame.setText("L'aperçu de la caméra sera affiché ici")
        
        # Réinitialiser les boutons
        self.register_btn.setEnabled(True)
        self.capture_btn.setEnabled(False)
        
        # Arrêter les threads si nécessaire
        if self.dataset_thread and self.dataset_thread.isRunning():
            self.dataset_thread.stop()
        
        if self.classifier_thread and self.classifier_thread.isRunning():
            self.classifier_thread.requestInterruption()
            self.classifier_thread.wait()
        
        # Journal
        logging.info("Formulaire d'enregistrement réinitialisé")
    
    def update_camera_preview(self, image):
        """Mettre à jour l'aperçu de la caméra avec l'image reçue"""
        # Redimensionner l'image pour qu'elle corresponde à la taille du widget
        pixmap = QPixmap.fromImage(image)
        scaled_pixmap = pixmap.scaled(
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
            self.classifier_thread.requestInterruption()
            self.classifier_thread.wait()
        
        event.accept() 