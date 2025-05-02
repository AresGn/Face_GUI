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
from utils.config import config

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
        
        # Utiliser un classificateur plus robuste pour la détection de visage
        cascade_path = os.path.join('data', 'haarcascade_frontalface_default.xml')
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Précharger tous les classificateurs au démarrage
        self.recognizers = {}
        self.preload_recognizers()
        
        # Paramètres pour améliorer la détection
        self.min_neighbors = 6  # Augmenté pour réduire les faux positifs
        self.scale_factor = 1.2  # Valeur équilibrée pour vitesse/précision
        self.min_size = (80, 80)  # Taille minimale du visage à détecter (augmentée)
        
        # Couleurs pour les rectangles
        self.green_color = (0, 255, 0)  # Visage reconnu (BGR)
        self.red_color = (0, 0, 255)    # Visage inconnu (BGR)
        
        # Configuration de la caméra
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
    
    def preload_recognizers(self):
        """Précharger tous les classificateurs des employés"""
        try:
            # Récupérer tous les employés
            employees = db_manager.get_all_employees()
            logging.info(f"Tentative de préchargement des classificateurs pour {len(employees)} employés")
            
            # Vérifier le répertoire des classificateurs
            classifiers_dir = os.path.join('data', 'classifiers')
            if not os.path.exists(classifiers_dir):
                os.makedirs(classifiers_dir, exist_ok=True)
                logging.warning(f"Le répertoire {classifiers_dir} n'existait pas et a été créé")
            
            loaded_count = 0
            for employee in employees:
                employee_id = employee['id']
                
                # Vérifier si le fichier du classificateur existe
                classifier_path = os.path.join('data', 'classifiers', f'{employee_id}_classifier.xml')
                if os.path.exists(classifier_path):
                    try:
                        # Charger le classificateur
                        recognizer = cv2.face.LBPHFaceRecognizer_create()
                        recognizer.read(classifier_path)
                        
                        # Stocker le classificateur et les infos de l'employé
                        self.recognizers[employee_id] = {
                            'recognizer': recognizer,
                            'employee': employee
                        }
                        loaded_count += 1
                        logging.info(f"Classificateur chargé avec succès pour {employee['prenom']} {employee['nom']} (ID: {employee_id})")
                    except Exception as e:
                        logging.error(f"Erreur lors du chargement du classificateur pour l'employé {employee_id}: {e}")
                else:
                    logging.warning(f"Aucun classificateur trouvé pour {employee['prenom']} {employee['nom']} (ID: {employee_id})")
            
            if loaded_count == 0 and len(employees) > 0:
                logging.warning("Aucun classificateur n'a pu être chargé alors qu'il y a des employés dans la base de données")
            
            logging.info(f"Préchargement terminé: {loaded_count}/{len(employees)} classificateurs chargés")
        except Exception as e:
            logging.error(f"Erreur générale lors du préchargement des classificateurs: {e}")
    
    def run(self):
        """Exécuter la reconnaissance faciale"""
        self.running = True
        cap = None
        
        try:
            # Ouvrir la caméra avec la source appropriée
            camera_source = self.get_camera_source()
            logging.info(f"Ouverture de la caméra: {camera_source}")
            cap = cv2.VideoCapture(camera_source)
            
            if not cap.isOpened():
                self.error_signal.emit(f"Impossible d'ouvrir la caméra: {camera_source}")
                return
            
            # Réduire la résolution pour accélérer le traitement
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Compteur pour ne pas traiter toutes les frames
            frame_count = 0
            
            # Dictionnaire pour suivre les détections consécutives
            consecutive_detections = {}
            
            while self.running and not self.isInterruptionRequested():
                try:
                    ret, frame = cap.read()
                    if not ret:
                        logging.warning("Échec de la capture d'image")
                        # Ne pas quitter immédiatement, tenter encore quelques fois
                        if frame_count % 10 == 0:  # Tous les 10 frames, émettre une erreur
                            self.error_signal.emit("Problème avec la caméra - essai de récupération")
                        continue
                    
                    # Obtenir les dimensions de l'image
                    frame_height, frame_width = frame.shape[:2]
                    
                    # Création d'une copie pour l'affichage
                    display_frame = frame.copy()
                    
                    # Convertir l'image en niveaux de gris pour la détection
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Améliorer le contraste pour une meilleure détection
                    gray = cv2.equalizeHist(gray)
                    
                    # Traiter uniquement une frame sur 2 pour réduire la charge CPU
                    process_frame = True
                    frame_count += 1
                    if frame_count % 2 != 0:
                        process_frame = False
                    
                    if process_frame:
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
                        
                        # Si un visage est détecté, essayer de le reconnaître
                        for (x, y, w, h) in valid_faces:
                            roi_gray = gray[y:y+h, x:x+w]
                            
                            best_match = None
                            best_confidence = 0
                            best_employee_id = None
                            
                            # Utiliser les classificateurs préchargés
                            for employee_id, data in self.recognizers.items():
                                recognizer = data['recognizer']
                                employee = data['employee']
                                
                                try:
                                    # Prédire l'identité
                                    id_pred, confidence = recognizer.predict(roi_gray)
                                    confidence = 100 - int(confidence)
                                    
                                    # Si la confiance est suffisante et meilleure que précédemment
                                    if confidence > 60 and confidence > best_confidence:  # Seuil à 60
                                        best_confidence = confidence
                                        best_employee_id = employee_id
                                        # Créer une copie de l'employé pour éviter de modifier l'original
                                        best_match = employee.copy()
                                        best_match['confidence'] = confidence
                                        best_match['time'] = datetime.datetime.now().strftime("%H:%M:%S")
                                except Exception as e:
                                    logging.error(f"Erreur lors de la reconnaissance pour l'employé {employee_id}: {e}")
                            
                            # Incrémenter le compteur de détections consécutives pour cet employé
                            if best_employee_id is not None:
                                if best_employee_id not in consecutive_detections:
                                    consecutive_detections[best_employee_id] = 1
                                else:
                                    consecutive_detections[best_employee_id] += 1
                                
                                # Réinitialiser les compteurs des autres employés
                                for emp_id in consecutive_detections:
                                    if emp_id != best_employee_id:
                                        consecutive_detections[emp_id] = 0
                                
                                # Si détecté consécutivement plusieurs fois, émettre le signal
                                required_detections = 5  # Au moins 5 détections consécutives
                                if consecutive_detections[best_employee_id] >= required_detections:
                                    logging.info(f"Détection confirmée après {required_detections} frames pour ID={best_employee_id}")
                                    # On réinitialise pour éviter des détections multiples
                                    consecutive_detections[best_employee_id] = 0
                                    # On émet le signal
                                    self.recognition_signal.emit(best_match)
                            
                            # Dessiner un rectangle sur le visage
                            if best_match:
                                # Rectangle vert pour un visage reconnu
                                cv2.rectangle(display_frame, (x, y), (x + w, y + h), self.green_color, 2)
                                text = f"{best_match['prenom']} {best_match['nom']} ({best_match['confidence']}%)"
                                cv2.putText(display_frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.green_color, 2)
                            else:
                                # Rectangle rouge pour un visage inconnu
                                cv2.rectangle(display_frame, (x, y), (x + w, y + h), self.red_color, 2)
                                cv2.putText(display_frame, "Inconnu", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.red_color, 2)
                    
                    # Convertir l'image pour l'affichage dans Qt
                    rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_frame.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    
                    # Émettre le signal de mise à jour de l'image
                    self.update_frame_signal.emit(qt_image)
                    
                    # Vérifier si le thread doit être arrêté
                    if not self.running or self.isInterruptionRequested():
                        logging.info("Interruption détectée dans la boucle de traitement")
                        break
                    
                    # Attente minimale
                    cv2.waitKey(30)
                
                except Exception as e:
                    logging.error(f"Erreur lors du traitement d'une frame: {e}")
                    self.error_signal.emit(f"Erreur de traitement: {str(e)}")
            
            logging.info("Boucle de reconnaissance terminée")
        
        except Exception as e:
            logging.error(f"Erreur générale dans le thread de reconnaissance: {e}")
            self.error_signal.emit(f"Erreur générale: {str(e)}")
        
        finally:
            # S'assurer que les ressources sont libérées
            if cap is not None and cap.isOpened():
                cap.release()
            logging.info("Ressources de caméra libérées")
    
    def stop(self):
        """Arrêter le thread de reconnaissance"""
        logging.info("Demande d'arrêt du thread de reconnaissance")
        self.running = False
        self.requestInterruption()
        self.wait(1000)

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
        controls_group.setStyleSheet("""
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
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(20, 20, 20, 20)
        
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
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(20, 20, 20, 20)
        
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
        # Recharger la liste des employés au démarrage de la reconnaissance
        self.results_list.clear()
        self.load_employees_list()
        
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
            try:
                # Désactiver les boutons pendant l'arrêt
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(False)
                
                # Mettre à jour le statut
                self.status_label.setText("Arrêt en cours...")
                
                # Signaler l'arrêt du thread
                self.recognition_thread.stop()
                
                # Créer un timer pour vérifier l'état du thread après un court délai
                # et le terminer si nécessaire, sans bloquer l'interface
                QTimer.singleShot(1000, self.finalize_thread_stop)
                
                # Journal
                logging.info("Arrêt de la reconnaissance faciale initié")
            except Exception as e:
                logging.error(f"Erreur lors de l'arrêt de la reconnaissance: {e}")
                # En cas d'erreur, réactiver le bouton de démarrage
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.status_label.setText("Erreur lors de l'arrêt")
        else:
            # Si aucun thread n'est en cours, réactiver simplement le bouton de démarrage
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("Reconnaissance arrêtée")
    
    def finalize_thread_stop(self):
        """Finaliser l'arrêt du thread après un délai"""
        try:
            if self.recognition_thread:
                if self.recognition_thread.isRunning():
                    logging.warning("Le thread ne s'est pas arrêté normalement, forçage de l'arrêt")
                    # Terminer le thread si toujours en cours d'exécution
                    self.recognition_thread.terminate()
                    self.recognition_thread.wait(500)  # Court délai après terminate()
                
                # Nettoyer les ressources
                self.recognition_thread = None
            
            # Réactiver le bouton de démarrage
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            
            # Mettre à jour le statut
            self.status_label.setText("Reconnaissance arrêtée")
            
            # Journal
            logging.info("Reconnaissance faciale arrêtée avec succès")
        except Exception as e:
            logging.error(f"Erreur lors de la finalisation de l'arrêt du thread: {e}")
            self.status_label.setText("Erreur lors de l'arrêt")
    
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
        
        # Ajouter un log de débogage pour voir ce que nous recevons
        logging.info(f"Reconnaissance reçue: ID={employee_id}, Nom={employee.get('prenom', 'N/A')} {employee.get('nom', 'N/A')}, Confiance={confidence}%, Heure={time}")
        
        # Vérifier si la reconnaissance n'est pas un doublon récent (moins de 10 secondes)
        current_time = datetime.datetime.now()
        if employee_id in self.recognized_employees:
            last_time = self.recognized_employees[employee_id]
            time_diff = (current_time - last_time).total_seconds()
            if time_diff < 10:
                return  # Ignorer la reconnaissance
        
        # Mettre à jour le timestamp de reconnaissance
        self.recognized_employees[employee_id] = current_time
        
        # Si la liste est vide, nous devons recharger la liste des employés
        if self.results_list.count() == 0:
            self.load_employees_list()
        
        # Récupérer les détails de l'employé reconnu pour l'affichage
        prenom = employee.get('prenom', '')
        nom = employee.get('nom', '')
        
        # Flag pour savoir si l'employé a été trouvé dans la liste
        found = False
        
        # Trouver l'élément dans la liste correspondant à l'employé
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            if item and item.data(Qt.UserRole) == employee_id:
                # Mettre à jour le texte de l'élément avec "Présent" et l'heure
                prenom_nom = f"{prenom} {nom}"
                if not prenom_nom.strip():  # Si le nom/prénom est vide, utiliser le texte existant
                    prenom_nom = item.text().split('(')[0].strip()
                item.setText(f"{prenom_nom} - Présent à {time}")
                item.setForeground(QColor(32, 191, 107))  # Vert - couleur #20bf6b
                found = True
                break
        
        # Si l'employé n'est pas trouvé dans la liste, ajouter un nouvel élément
        if not found and prenom and nom:
            item_text = f"{prenom} {nom} - Présent à {time}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, employee_id)
            item.setForeground(QColor(32, 191, 107))  # Vert
            self.results_list.addItem(item)
            logging.info(f"Nouvel employé ajouté à la liste: {item_text}")
        
        # Journal
        logging.info(f"Employé reconnu et affiché: ID={employee_id}, Confiance={confidence}%, Heure={time}")
        
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
        
        try:
            # Enregistrer les présences dans la base de données
            count = 0
            for employee_id, timestamp in self.recognized_employees.items():
                # Récupérer les informations d'heure
                time_str = timestamp.strftime("%H:%M:%S")
                date_str = timestamp.strftime("%Y-%m-%d")
                
                # Enregistrer dans la base de données
                result = db_manager.mark_attendance(employee_id, date_str, time_str, "Present")
                if result:
                    count += 1
            
            # Afficher un message de succès
            QMessageBox.information(self, "Enregistrement réussi", 
                                   f"{count} présences ont été enregistrées avec succès dans la base de données.")
            
            # Journal
            logging.info(f"{count} présences enregistrées dans la base de données")
        except Exception as e:
            # En cas d'erreur, afficher un message d'erreur
            QMessageBox.critical(self, "Erreur", 
                                f"Une erreur est survenue lors de l'enregistrement des présences: {str(e)}")
            logging.error(f"Erreur lors de l'enregistrement des présences: {e}")
    
    def closeEvent(self, event):
        """Gérer l'événement de fermeture de la page"""
        try:
            logging.info("Fermeture de la page de reconnaissance")
            
            # Arrêter proprement le thread de reconnaissance
            if self.recognition_thread and self.recognition_thread.isRunning():
                # D'abord, signaler l'arrêt sans bloquer
                self.recognition_thread.stop()
                
                # Créer un timer pour compléter la fermeture après un court délai
                # Cela permet d'éviter un blocage de l'interface
                cleanup_timer = QTimer(self)
                cleanup_timer.setSingleShot(True)
                cleanup_timer.timeout.connect(self.complete_cleanup)
                cleanup_timer.start(500)  # 500ms
                
                # Ne pas bloquer l'événement de fermeture
                event.accept()
            else:
                # Si pas de thread en cours, accepter immédiatement
                event.accept()
        except Exception as e:
            logging.error(f"Erreur lors de la fermeture de la page: {e}")
            event.accept()  # Accepter quand même pour éviter de bloquer
    
    def complete_cleanup(self):
        """Finaliser le nettoyage des ressources après un délai"""
        try:
            logging.info("Finalisation du nettoyage des ressources")
            
            # Forcer l'arrêt du thread s'il est toujours en cours
            if self.recognition_thread and self.recognition_thread.isRunning():
                logging.warning("Forcer l'arrêt du thread qui n'a pas répondu")
                self.recognition_thread.terminate()
                self.recognition_thread.wait(500)
                
                # Libérer explicitement les ressources OpenCV
                cv2.destroyAllWindows()
                
                # Supprimer le thread
                self.recognition_thread = None
                
            logging.info("Nettoyage des ressources terminé")
        except Exception as e:
            logging.error(f"Erreur lors du nettoyage final: {e}")
    
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