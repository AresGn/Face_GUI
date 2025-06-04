import os
import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QComboBox, QGroupBox, QMessageBox, QFormLayout, QLineEdit,
                             QSpinBox, QTabWidget, QCheckBox, QRadioButton, QButtonGroup)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

# Importer les modules utils
from utils.camera_config import (configure_droidcam, list_available_cameras, set_default_camera,
                                configure_esp32cam, test_esp32cam_connection)
from utils.config import config

# Configuration du logger
logging.basicConfig(filename='settings.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class SettingsPage(QWidget):
    """Page des paramètres de l'application"""
    
    def __init__(self):
        """Initialiser la page des paramètres"""
        super().__init__()
        
        # Initialiser l'interface utilisateur
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        # Créer le layout principal
        main_layout = QVBoxLayout()
        
        # Titre de la page
        title_label = QLabel("Paramètres du système")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Créer un widget à onglets pour organiser les paramètres
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #5a6075;
                border-radius: 6px;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #454e67;
                color: white;
                border: 1px solid #5a6075;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 10px 15px;
                min-width: 120px;
                font-size: 14px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3867d6;
            }
            QTabBar::tab:hover:!selected {
                background-color: #5a6075;
            }
        """)
        
        # Créer les onglets
        camera_tab = self.create_camera_tab()
        app_tab = self.create_app_tab()
        
        # Ajouter les onglets au widget
        tab_widget.addTab(camera_tab, "Caméra")
        tab_widget.addTab(app_tab, "Application")
        
        # Ajouter le widget à onglets au layout principal
        main_layout.addWidget(tab_widget)
        
        # Définir le layout pour ce widget
        self.setLayout(main_layout)
    
    def create_camera_tab(self):
        """Créer l'onglet des paramètres de caméra"""
        camera_widget = QWidget()
        camera_layout = QVBoxLayout()
        
        # Groupe pour la sélection de la source de caméra
        camera_source_group = QGroupBox("Source de caméra")
        camera_source_layout = QVBoxLayout()
        
        # Boutons radio pour choisir entre DroidCam, ESP32-CAM et webcam
        self.camera_source_group = QButtonGroup()

        self.droid_cam_radio = QRadioButton("Utiliser DroidCam (smartphone Android/iOS)")
        self.esp32_cam_radio = QRadioButton("Utiliser ESP32-CAM (module caméra Wi-Fi)")
        self.webcam_radio = QRadioButton("Utiliser la webcam du PC")

        # Vérifier la configuration actuelle
        if config.get('camera.use_esp32_cam', False):
            self.esp32_cam_radio.setChecked(True)
        elif config.get('camera.use_droid_cam', False):
            self.droid_cam_radio.setChecked(True)
        else:
            self.webcam_radio.setChecked(True)

        self.camera_source_group.addButton(self.droid_cam_radio)
        self.camera_source_group.addButton(self.esp32_cam_radio)
        self.camera_source_group.addButton(self.webcam_radio)

        camera_source_layout.addWidget(self.droid_cam_radio)
        camera_source_layout.addWidget(self.esp32_cam_radio)
        camera_source_layout.addWidget(self.webcam_radio)
        
        # Formulaire pour les paramètres DroidCam
        self.droid_cam_form = QWidget()
        droid_cam_form_layout = QFormLayout()
        
        self.ip_address_input = QLineEdit()
        current_url = config.get('camera.droid_cam_url', 'http://192.168.1.X:4747/video')
        # Extraire l'IP et le port de l'URL
        try:
            ip_part = current_url.split('://')[1].split(':')[0]
            port_part = current_url.split(':')[2].split('/')[0]
            self.ip_address_input.setText(ip_part)
        except:
            self.ip_address_input.setText("192.168.1.X")
        
        self.port_input = QSpinBox()
        self.port_input.setRange(1000, 10000)
        try:
            self.port_input.setValue(int(port_part))
        except:
            self.port_input.setValue(4747)
        
        self.test_droid_cam_btn = QPushButton("Tester la connexion")
        self.test_droid_cam_btn.clicked.connect(self.test_droid_cam)
        
        droid_cam_form_layout.addRow("Adresse IP:", self.ip_address_input)
        droid_cam_form_layout.addRow("Port:", self.port_input)
        droid_cam_form_layout.addRow("", self.test_droid_cam_btn)
        
        self.droid_cam_form.setLayout(droid_cam_form_layout)

        # Formulaire pour les paramètres ESP32-CAM
        self.esp32_cam_form = QWidget()
        esp32_cam_form_layout = QFormLayout()

        self.esp32_ip_input = QLineEdit()
        current_esp32_ip = config.get('camera.esp32_cam_ip', '192.168.1.100')
        self.esp32_ip_input.setText(current_esp32_ip)
        self.esp32_ip_input.setPlaceholderText("Ex: 192.168.1.100")

        self.esp32_port_input = QLineEdit()
        current_esp32_port = config.get('camera.esp32_cam_port', 80)
        self.esp32_port_input.setText(str(current_esp32_port))
        self.esp32_port_input.setPlaceholderText("Ex: 80")

        self.esp32_stream_path_input = QLineEdit()
        current_esp32_stream_path = config.get('camera.esp32_cam_stream_path', '/stream')
        self.esp32_stream_path_input.setText(current_esp32_stream_path)
        self.esp32_stream_path_input.setPlaceholderText("Ex: /stream")

        self.esp32_quality_input = QSpinBox()
        self.esp32_quality_input.setRange(1, 63)
        self.esp32_quality_input.setValue(config.get('camera.esp32_cam_quality', 10))
        self.esp32_quality_input.setToolTip("Qualité JPEG (1-63, plus bas = meilleure qualité)")

        self.test_esp32_btn = QPushButton("Tester la connexion ESP32-CAM")
        self.test_esp32_btn.clicked.connect(self.test_esp32_cam)

        esp32_cam_form_layout.addRow("Adresse IP:", self.esp32_ip_input)
        esp32_cam_form_layout.addRow("Port:", self.esp32_port_input)
        esp32_cam_form_layout.addRow("Chemin du flux:", self.esp32_stream_path_input)
        esp32_cam_form_layout.addRow("Qualité JPEG:", self.esp32_quality_input)
        esp32_cam_form_layout.addRow("", self.test_esp32_btn)

        self.esp32_cam_form.setLayout(esp32_cam_form_layout)

        # Formulaire pour les paramètres de webcam
        self.webcam_form = QWidget()
        webcam_form_layout = QFormLayout()
        
        self.webcam_combo = QComboBox()
        self.refresh_webcam_list()
        
        self.refresh_webcam_btn = QPushButton("Rafraîchir la liste")
        self.refresh_webcam_btn.clicked.connect(self.refresh_webcam_list)
        
        self.test_webcam_btn = QPushButton("Tester la caméra")
        self.test_webcam_btn.clicked.connect(self.test_webcam)
        
        webcam_form_layout.addRow("Caméra:", self.webcam_combo)
        webcam_form_layout.addRow("", self.refresh_webcam_btn)
        webcam_form_layout.addRow("", self.test_webcam_btn)
        
        self.webcam_form.setLayout(webcam_form_layout)
        
        # Gérer l'affichage des formulaires en fonction de la sélection
        self.droid_cam_radio.toggled.connect(self.toggle_camera_forms)
        self.esp32_cam_radio.toggled.connect(self.toggle_camera_forms)
        self.webcam_radio.toggled.connect(self.toggle_camera_forms)

        # Ajouter les formulaires
        camera_source_layout.addWidget(self.droid_cam_form)
        camera_source_layout.addWidget(self.esp32_cam_form)
        camera_source_layout.addWidget(self.webcam_form)
        
        # Initialiser l'affichage des formulaires
        self.toggle_camera_forms()
        
        camera_source_group.setLayout(camera_source_layout)
        camera_layout.addWidget(camera_source_group)
        
        # Boutons de sauvegarde
        buttons_layout = QHBoxLayout()
        
        self.save_camera_btn = QPushButton("Enregistrer les paramètres")
        self.save_camera_btn.clicked.connect(self.save_camera_settings)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_camera_btn)
        
        camera_layout.addLayout(buttons_layout)
        camera_layout.addStretch()
        
        camera_widget.setLayout(camera_layout)
        return camera_widget
    
    def create_app_tab(self):
        """Créer l'onglet des paramètres de l'application"""
        app_widget = QWidget()
        app_layout = QVBoxLayout()
        
        # Groupe pour les paramètres généraux
        general_group = QGroupBox("Paramètres généraux")
        general_layout = QFormLayout()
        
        # Nom de l'application
        self.app_name_input = QLineEdit()
        self.app_name_input.setText(config.get('app.name', "Système de reconnaissance faciale - CBT SARL"))
        
        # Taille de la fenêtre
        window_size_layout = QHBoxLayout()
        self.window_width = QSpinBox()
        self.window_width.setRange(800, 1920)
        self.window_width.setValue(config.get('ui.window_size.width', 1200))
        
        self.window_height = QSpinBox()
        self.window_height.setRange(600, 1080)
        self.window_height.setValue(config.get('ui.window_size.height', 800))
        
        window_size_layout.addWidget(self.window_width)
        window_size_layout.addWidget(QLabel("x"))
        window_size_layout.addWidget(self.window_height)
        
        general_layout.addRow("Nom de l'application:", self.app_name_input)
        general_layout.addRow("Taille de la fenêtre:", window_size_layout)
        
        general_group.setLayout(general_layout)
        app_layout.addWidget(general_group)
        
        # Boutons de sauvegarde
        buttons_layout = QHBoxLayout()
        
        self.save_app_btn = QPushButton("Enregistrer les paramètres")
        self.save_app_btn.clicked.connect(self.save_app_settings)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_app_btn)
        
        app_layout.addLayout(buttons_layout)
        app_layout.addStretch()
        
        app_widget.setLayout(app_layout)
        return app_widget
    
    def toggle_camera_forms(self):
        """Afficher ou masquer les formulaires en fonction de la sélection"""
        self.droid_cam_form.setVisible(self.droid_cam_radio.isChecked())
        self.esp32_cam_form.setVisible(self.esp32_cam_radio.isChecked())
        self.webcam_form.setVisible(self.webcam_radio.isChecked())
    
    def refresh_webcam_list(self):
        """Rafraîchir la liste des webcams disponibles"""
        self.webcam_combo.clear()

        try:
            available_cameras = list_available_cameras()
            current_camera = config.get('camera.index', 0)

            print(f"DEBUG: Caméras détectées: {available_cameras}")  # Debug

            if not available_cameras:
                # Fallback: ajouter les indices 0, 1, 2 par défaut
                print("DEBUG: Aucune caméra détectée, ajout des indices par défaut")
                for i in range(3):
                    self.webcam_combo.addItem(f"Caméra {i}", i)
                self.webcam_combo.addItem("Aucune caméra détectée", -1)
            else:
                for idx in available_cameras:
                    self.webcam_combo.addItem(f"Caméra {idx}", idx)

                    # Sélectionner la caméra configurée
                    if idx == current_camera:
                        self.webcam_combo.setCurrentIndex(self.webcam_combo.count() - 1)

            print(f"DEBUG: {self.webcam_combo.count()} éléments ajoutés à la liste")

        except Exception as e:
            print(f"DEBUG: Erreur dans refresh_webcam_list: {e}")
            # En cas d'erreur, ajouter au moins les indices de base
            for i in range(3):
                self.webcam_combo.addItem(f"Caméra {i}", i)
    
    def test_droid_cam(self):
        """Tester la connexion DroidCam"""
        ip_address = self.ip_address_input.text().strip()
        port = self.port_input.value()
        
        if not ip_address or ip_address == "192.168.1.X":
            QMessageBox.warning(self, "Avertissement", "Veuillez entrer une adresse IP valide.")
            return
        
        # Tester la connexion sans sauvegarder
        success, message = configure_droidcam(ip_address, port, True)
        
        if success:
            QMessageBox.information(self, "Succès", f"Connexion à DroidCam réussie: {message}")
        else:
            QMessageBox.critical(self, "Erreur", f"Échec de la connexion à DroidCam: {message}")
    
    def test_webcam(self):
        """Tester la webcam sélectionnée"""
        camera_idx = self.webcam_combo.currentData()
        
        if camera_idx == -1:
            QMessageBox.warning(self, "Avertissement", "Aucune caméra n'est disponible.")
            return
        
        # Tester la caméra sans sauvegarder
        import cv2
        
        cap = cv2.VideoCapture(camera_idx)
        if not cap.isOpened():
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir la caméra {camera_idx}.")
            return
        
        # Capturer une image pour tester
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            QMessageBox.information(self, "Succès", f"La caméra {camera_idx} fonctionne correctement.")
        else:
            QMessageBox.critical(self, "Erreur", f"Impossible de capturer une image depuis la caméra {camera_idx}.")

    def test_esp32_cam(self):
        """Tester la connexion ESP32-CAM"""
        ip_address = self.esp32_ip_input.text().strip()
        port = self.esp32_port_input.text().strip()
        stream_path = self.esp32_stream_path_input.text().strip()

        if not ip_address:
            QMessageBox.warning(self, "Avertissement", "Veuillez saisir l'adresse IP de l'ESP32-CAM.")
            return

        try:
            port = int(port) if port else 80
        except ValueError:
            QMessageBox.warning(self, "Avertissement", "Le port doit être un nombre entier.")
            return

        if not stream_path:
            stream_path = "/stream"

        # Tester la connexion
        success, message = test_esp32cam_connection(ip_address, port, stream_path)

        if success:
            QMessageBox.information(self, "Test réussi", message)
        else:
            QMessageBox.critical(self, "Test échoué", message)

    def save_camera_settings(self):
        """Sauvegarder les paramètres de caméra"""
        try:
            if self.droid_cam_radio.isChecked():
                # Configurer DroidCam
                ip_address = self.ip_address_input.text().strip()
                port = self.port_input.value()

                if not ip_address or ip_address == "192.168.1.X":
                    QMessageBox.warning(self, "Avertissement", "Veuillez entrer une adresse IP valide.")
                    return

                success, message = configure_droidcam(ip_address, port, True)

                if success:
                    QMessageBox.information(self, "Succès", "Les paramètres de DroidCam ont été enregistrés.")
                else:
                    QMessageBox.critical(self, "Erreur", f"Échec de la configuration de DroidCam: {message}")

            elif self.esp32_cam_radio.isChecked():
                # Configurer ESP32-CAM
                ip_address = self.esp32_ip_input.text().strip()
                port = self.esp32_port_input.text().strip()
                stream_path = self.esp32_stream_path_input.text().strip()
                quality = self.esp32_quality_input.value()

                if not ip_address:
                    QMessageBox.warning(self, "Avertissement", "Veuillez entrer une adresse IP valide.")
                    return

                try:
                    port = int(port) if port else 80
                except ValueError:
                    QMessageBox.warning(self, "Avertissement", "Le port doit être un nombre entier.")
                    return

                if not stream_path:
                    stream_path = "/stream"

                success, message = configure_esp32cam(ip_address, port, stream_path, quality, True)

                if success:
                    QMessageBox.information(self, "Succès", "Les paramètres de l'ESP32-CAM ont été enregistrés.")
                else:
                    QMessageBox.critical(self, "Erreur", f"Échec de la configuration de l'ESP32-CAM: {message}")

            else:
                # Configurer la webcam
                camera_idx = self.webcam_combo.currentData()

                if camera_idx == -1:
                    QMessageBox.warning(self, "Avertissement", "Aucune caméra n'est disponible.")
                    return

                success, message = set_default_camera(camera_idx)

                if success:
                    QMessageBox.information(self, "Succès", f"La caméra {camera_idx} a été configurée comme caméra par défaut.")
                else:
                    QMessageBox.critical(self, "Erreur", f"Échec de la configuration de la caméra: {message}")
            
            # Journal
            logging.info("Paramètres de caméra enregistrés")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {str(e)}")
            logging.error(f"Erreur lors de la sauvegarde des paramètres de caméra: {e}")
    
    def save_app_settings(self):
        """Sauvegarder les paramètres de l'application"""
        try:
            # Nom de l'application
            app_name = self.app_name_input.text().strip()
            if app_name:
                config.set('app.name', app_name)
            
            # Taille de la fenêtre
            config.set('ui.window_size.width', self.window_width.value())
            config.set('ui.window_size.height', self.window_height.value())
            
            # Afficher un message de confirmation
            QMessageBox.information(self, "Succès", "Les paramètres de l'application ont été enregistrés. Redémarrez l'application pour appliquer tous les changements.")
            
            # Journal
            logging.info("Paramètres de l'application enregistrés")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {str(e)}")
            logging.error(f"Erreur lors de la sauvegarde des paramètres de l'application: {e}") 