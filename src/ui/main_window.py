import sys
import os
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QTabWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QMessageBox,
                             QStackedWidget, QFrame, QSizePolicy, QAction, QToolBar,
                             QStatusBar, QSpacerItem)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QColor
from PyQt5.QtCore import Qt, QSize, QSettings

# Importer les composants de l'interface
from ui.registration_page import RegistrationPage
from ui.recognition_page import RecognitionPage
from ui.attendance_page import AttendancePage
from ui.dashboard_page import DashboardPage

# Importer les utilitaires
from utils.config import config

# Configuration du logger
logging.basicConfig(filename='ui.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Définition des couleurs de l'application
COLORS = {
    'primary': '#3867d6',       # Bleu plus vif
    'secondary': '#4b7bec',     # Bleu secondaire
    'accent': '#fa8231',        # Orange accent
    'background': '#2f3542',    # Fond principal (même que sidebar)
    'sidebar': '#2f3542',       # Gris foncé pour sidebar
    'content_bg': '#383f53',    # Fond un peu plus clair pour les contenus
    'card_bg': '#454e67',       # Fond encore plus clair pour les cartes 
    'text': '#ffffff',          # Texte blanc pour bon contraste sur fond foncé
    'text_secondary': '#dfe4ea', # Texte gris clair
    'success': '#20bf6b',       # Vert plus vif
    'warning': '#f7b731',       # Jaune vif
    'danger': '#eb3b5a'         # Rouge vif
}

class FaceRecognizerApp(QMainWindow):
    """Classe principale de l'application de reconnaissance faciale"""
    
    def __init__(self):
        """Initialiser la fenêtre principale de l'application"""
        super().__init__()
        
        # Configuration de base de la fenêtre
        self.setWindowTitle(config.get('app.name', "Système de reconnaissance faciale - CITEX SART"))
        self.setWindowIcon(QIcon(os.path.join('src', 'assets', 'icons', 'app_icon.png')))
        
        # Définir la taille de la fenêtre
        width = config.get('ui.window_size.width', 1200)
        height = config.get('ui.window_size.height', 800)
        self.resize(width, height)
        
        # Créer le widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Appliquer une feuille de style globale
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text']};
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 15px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
            QPushButton:pressed {{
                background-color: #2d5bbf;
            }}
            QTabWidget::pane {{
                border: 1px solid #5a6075;
                background-color: {COLORS['content_bg']};
                border-radius: 8px;
            }}
            QLineEdit, QComboBox, QTextEdit, QDateEdit {{
                padding: 12px;
                border: 1px solid #5a6075;
                border-radius: 6px;
                background-color: {COLORS['card_bg']};
                color: {COLORS['text']};
                font-size: 14px;
                selection-background-color: {COLORS['primary']};
            }}
            QStatusBar {{
                background-color: {COLORS['primary']};
                color: {COLORS['text']};
                font-weight: bold;
                font-size: 14px;
            }}
            QLabel {{
                color: {COLORS['text']};
                font-size: 15px;
            }}
            QLabel#header_title {{
                font-size: 22px;
                font-weight: bold;
                color: {COLORS['text']};
            }}
            QTableView {{
                border: 1px solid #5a6075;
                border-radius: 6px;
                background-color: {COLORS['card_bg']};
                alternate-background-color: #505771;
                gridline-color: #5a6075;
                selection-background-color: {COLORS['primary']};
                selection-color: {COLORS['text']};
                font-size: 14px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: {COLORS['text']};
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }}
            QGroupBox {{
                font-size: 15px;
                font-weight: bold;
                border: 1px solid #5a6075;
                border-radius: 8px;
                margin-top: 16px;
                background-color: {COLORS['content_bg']};
                color: {COLORS['text']};
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                top: -10px;
                padding: 0 5px;
                background-color: {COLORS['primary']};
                border-radius: 4px;
            }}
        """)
        
        # Créer le layout principal comme un layout horizontal
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Initialiser l'interface utilisateur
        self.init_ui()
        
        # Connexion des signaux
        self.connect_signals()
        
        # Journal de démarrage
        logging.info("Application démarrée")
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        # Créer la barre de menu
        self.create_menu()
        
        # Créer la sidebar
        self.create_sidebar()
        
        # Créer le conteneur principal pour le contenu
        self.content_container = QWidget()
        self.content_container.setStyleSheet(f"""
            background-color: {COLORS['content_bg']};
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
            border-top-right-radius: 0px;
            border-bottom-right-radius: 0px;
        """)
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        self.content_layout.setSpacing(15)
        
        # Créer l'en-tête
        self.create_header()
        
        # Créer le widget empilé pour les différentes pages
        self.create_stacked_widget()
        
        # Ajouter le conteneur de contenu au layout principal
        self.main_layout.addWidget(self.content_container, 4)  # Ratio 4:1 entre contenu et sidebar
        
        # Créer la barre d'état
        self.create_status_bar()
        
        # Améliorer la visibilité des liens et du texte souligné
        self.setStyleSheet(self.styleSheet() + """
            QLabel[isLink="true"], QLabel:underline {
                color: #4b7bec;
                font-weight: bold;
                font-size: 15px;
                text-decoration: underline;
                background-color: transparent;
                padding: 2px;
                margin: 2px;
            }
            
            QLabel[isLink="true"]:hover, QLabel:underline:hover {
                color: #3867d6;
            }
            
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 2px 5px;
                color: white;
                background-color: {COLORS['primary']};
                border-radius: 4px;
            }
        """)
    
    def create_sidebar(self):
        """Créer la barre latérale (sidebar)"""
        # Créer le widget sidebar
        self.sidebar = QFrame()
        self.sidebar.setFrameShape(QFrame.NoFrame)
        self.sidebar.setMinimumWidth(240)
        self.sidebar.setMaximumWidth(240)
        
        # Appliquer un style à la sidebar
        self.sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['sidebar']};
                border-right: 1px solid #5a6075;
            }}
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text']};
                border: none;
                border-radius: 0;
                text-align: left;
                padding: 18px 20px;
                font-size: 16px;
                font-weight: normal;
                min-width: 0px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                border-left: 4px solid {COLORS['accent']};
                padding-left: 16px;
            }}
            QPushButton#active {{
                background-color: rgba(255, 255, 255, 0.15);
                border-left: 4px solid {COLORS['accent']};
                padding-left: 16px;
                font-weight: bold;
            }}
            QLabel {{
                color: {COLORS['text']};
            }}
        """)
        
        # Layout vertical pour la sidebar
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(5)
        
        # Logo en haut de la sidebar
        logo_container = QFrame()
        logo_container.setMinimumHeight(120)
        logo_container.setMaximumHeight(120)
        logo_layout = QHBoxLayout(logo_container)
        
        logo_label = QLabel()
        logo_path = os.path.join('src', 'assets', 'icons', 'citex_logo.png')
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio))
        else:
            logo_label.setText("CITEX")
            logo_label.setFont(QFont("Arial", 26, QFont.Bold))
        
        logo_layout.addWidget(logo_label, 0, Qt.AlignCenter)
        sidebar_layout.addWidget(logo_container)
        
        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); margin: 0 15px;")
        sidebar_layout.addWidget(separator)
        
        # Boutons de navigation
        self.dashboard_btn = QPushButton("  Tableau de bord")
        dashboard_icon_path = os.path.join('src', 'icons-svg', 'Business', 'stats-up.svg')
        self.dashboard_btn.setIcon(QIcon(dashboard_icon_path))
        self.dashboard_btn.setIconSize(QSize(30, 30))
        
        self.register_btn = QPushButton("  Enregistrement")
        register_icon_path = os.path.join('src', 'icons-svg', 'Interface and Sign', 'circle-plus.svg')
        self.register_btn.setIcon(QIcon(register_icon_path))
        self.register_btn.setIconSize(QSize(30, 30))
        
        self.recognize_btn = QPushButton("  Reconnaissance")
        recognize_icon_path = os.path.join('src', 'icons-svg', 'Interface and Sign', 'eye.svg')
        self.recognize_btn.setIcon(QIcon(recognize_icon_path))
        self.recognize_btn.setIconSize(QSize(30, 30))
        
        self.attendance_btn = QPushButton("  Présences")
        attendance_icon_path = os.path.join('src', 'icons-svg', 'Business', 'notepad.svg')
        self.attendance_btn.setIcon(QIcon(attendance_icon_path))
        self.attendance_btn.setIconSize(QSize(30, 30))
        
        # Configurer le bouton actif par défaut
        self.dashboard_btn.setObjectName("active")
        
        # Ajouter les boutons à la sidebar
        sidebar_layout.addWidget(self.dashboard_btn)
        sidebar_layout.addWidget(self.register_btn)
        sidebar_layout.addWidget(self.recognize_btn)
        sidebar_layout.addWidget(self.attendance_btn)
        
        # Ajouter un espace extensible
        sidebar_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Bouton de paramètres en bas
        self.settings_btn = QPushButton("  Paramètres")
        settings_icon_path = os.path.join('src', 'icons-svg', 'filled', 'adjustments.svg')
        self.settings_btn.setIcon(QIcon(settings_icon_path))
        self.settings_btn.setIconSize(QSize(30, 30))
        sidebar_layout.addWidget(self.settings_btn)
        
        # Bouton pour quitter en bas
        self.exit_btn = QPushButton("  Quitter")
        exit_icon_path = os.path.join('src', 'icons-svg', 'Interface and Sign', 'power-switch.svg')
        self.exit_btn.setIcon(QIcon(exit_icon_path))
        self.exit_btn.setIconSize(QSize(30, 30))
        sidebar_layout.addWidget(self.exit_btn)
        
        # Ajouter la sidebar au layout principal
        self.main_layout.addWidget(self.sidebar, 0)  # Ratio fixe, non extensible
    
    def create_menu(self):
        """Créer la barre de menu"""
        self.menu_bar = self.menuBar()
        self.menu_bar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {COLORS['primary']};
                color: {COLORS['text']};
                font-weight: bold;
                padding: 8px;
                font-size: 15px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                color: {COLORS['text']};
                padding: 8px 12px;
                margin: 0 2px;
            }}
            QMenuBar::item:selected {{
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }}
            QMenu {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text']};
                border: 1px solid #5a6075;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }}
            QMenu::item {{
                padding: 10px 30px 10px 20px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['primary']};
                color: {COLORS['text']};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: #5a6075;
                margin: 5px 10px;
            }}
        """)
        
        # Menu Fichier
        file_menu = self.menu_bar.addMenu("Fichier")
        
        # Actions du menu Fichier
        export_action = QAction("Exporter les données", self)
        settings_action = QAction("Paramètres", self)
        exit_action = QAction("Quitter", self)
        exit_action.triggered.connect(self.close)
        
        # Ajouter les actions au menu Fichier
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        file_menu.addAction(settings_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Menu Aide
        help_menu = self.menu_bar.addMenu("Aide")
        
        # Actions du menu Aide
        about_action = QAction("À propos", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_action = QAction("Aide", self)
        
        # Ajouter les actions au menu Aide
        help_menu.addAction(help_action)
        help_menu.addAction(about_action)
    
    def create_header(self):
        """Créer l'en-tête de l'application"""
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_frame.setMaximumHeight(90)
        header_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border: 1px solid #5a6075;
                border-radius: 8px;
            }}
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Titre de l'application
        title_label = QLabel(config.get('app.name', "Système de reconnaissance faciale - CITEX SART"))
        title_label.setObjectName("header_title")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        # Ajouter le titre à l'en-tête
        header_layout.addWidget(title_label, 1)  # 1 est le facteur d'étirement
        
        # Ajouter l'en-tête au layout de contenu
        self.content_layout.addWidget(header_frame)
    
    def create_stacked_widget(self):
        """Créer le widget empilé pour les différentes pages"""
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['card_bg']};
                border: 1px solid #5a6075;
                border-radius: 8px;
            }}
        """)
        
        # Créer les pages
        self.dashboard_page = DashboardPage()
        self.registration_page = RegistrationPage()
        self.recognition_page = RecognitionPage()
        self.attendance_page = AttendancePage()
        
        # Appliquer un style pour les boutons d'action à toutes les pages
        action_button_style = f"""
            QPushButton[actionRole="true"] {{
                background-color: {COLORS['accent']};
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 15px 30px;
                border-radius: 6px;
                min-width: 150px;
            }}
            QPushButton[actionRole="true"]:hover {{
                background-color: #ff9f43;
            }}
            QPushButton[actionRole="true"]:pressed {{
                background-color: #e67e22;
            }}
            QPushButton[actionRole="secondary"] {{
                background-color: #546de5;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 15px 30px;
                border-radius: 6px;
                min-width: 150px;
            }}
            QPushButton[actionRole="secondary"]:hover {{
                background-color: #778beb;
            }}
            QPushButton[actionRole="danger"] {{
                background-color: {COLORS['danger']};
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 15px 30px;
                border-radius: 6px;
                min-width: 150px;
            }}
            QPushButton[actionRole="danger"]:hover {{
                background-color: #ff4757;
            }}
        """
        self.dashboard_page.setStyleSheet(action_button_style)
        self.registration_page.setStyleSheet(action_button_style)
        self.recognition_page.setStyleSheet(action_button_style)
        self.attendance_page.setStyleSheet(action_button_style)
        
        # Ajouter les pages au widget empilé
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.registration_page)
        self.stacked_widget.addWidget(self.recognition_page)
        self.stacked_widget.addWidget(self.attendance_page)
        
        # Définir la page par défaut
        self.stacked_widget.setCurrentIndex(0)
        
        # Ajouter le widget empilé au layout de contenu
        self.content_layout.addWidget(self.stacked_widget, 1)  # 1 est le facteur d'étirement
    
    def create_status_bar(self):
        """Créer la barre d'état"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Ajouter des informations permanentes à la barre d'état
        version_label = QLabel(f"Version: {config.get('app.version', '1.0.0')}")
        version_label.setStyleSheet("color: white; padding-right: 10px; font-size: 14px;")
        self.status_bar.addPermanentWidget(version_label)
        
        # Message par défaut
        self.status_bar.showMessage("Prêt")
    
    def connect_signals(self):
        """Connecter les signaux aux slots"""
        # Connecter les boutons de la sidebar aux pages
        self.dashboard_btn.clicked.connect(lambda: self.change_page(0, self.dashboard_btn))
        self.register_btn.clicked.connect(lambda: self.change_page(1, self.register_btn))
        self.recognize_btn.clicked.connect(lambda: self.change_page(2, self.recognize_btn))
        self.attendance_btn.clicked.connect(lambda: self.change_page(3, self.attendance_btn))
        
        # Connecter le bouton de sortie
        self.exit_btn.clicked.connect(self.close)
    
    def change_page(self, index, button):
        """Changer de page et mettre à jour le bouton actif"""
        # Réinitialiser tous les boutons
        for btn in [self.dashboard_btn, self.register_btn, self.recognize_btn, self.attendance_btn]:
            btn.setObjectName("")
            btn.setStyleSheet("")  # Réinitialiser le style pour appliquer celui du parent
        
        # Activer le bouton cliqué
        button.setObjectName("active")
        button.style().unpolish(button)
        button.style().polish(button)
        
        # Changer la page
        self.stacked_widget.setCurrentIndex(index)
    
    def show_about_dialog(self):
        """Afficher la boîte de dialogue À propos"""
        QMessageBox.about(self, "À propos", 
                          f"<h3>{config.get('app.name', 'Système de reconnaissance faciale')}</h3>"
                          f"<p>Version: {config.get('app.version', '1.0.0')}</p>"
                          "<p>Ce logiciel permet de gérer la présence des employés à l'aide de la reconnaissance faciale.</p>"
                          "<p>Développé pour CITEX SART.</p>")
    
    def closeEvent(self, event):
        """Gérer l'événement de fermeture de l'application"""
        # Demander confirmation avant de quitter
        reply = QMessageBox.question(self, "Confirmation", 
                                     "Êtes-vous sûr de vouloir quitter l'application ?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Nettoyer les ressources avant de quitter
            logging.info("Application fermée")
            event.accept()
        else:
            event.ignore() 