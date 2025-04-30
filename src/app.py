import sys
import os

# Assurez-vous que le répertoire src est dans le PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.main_window import FaceRecognizerApp, COLORS
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt


def set_application_style(app):
    """Configurer le style et la palette de couleurs de l'application"""
    # Appliquer le style Fusion (plus moderne)
    app.setStyle("Fusion")
    
    # Créer une palette de couleurs pour thème foncé
    palette = QPalette()
    
    # Couleurs de base
    palette.setColor(QPalette.Window, QColor(COLORS['background']))
    palette.setColor(QPalette.WindowText, QColor(COLORS['text']))
    palette.setColor(QPalette.Base, QColor(COLORS['card_bg']))
    palette.setColor(QPalette.AlternateBase, QColor(COLORS['content_bg']))
    palette.setColor(QPalette.ToolTipBase, QColor(COLORS['card_bg']))
    palette.setColor(QPalette.ToolTipText, QColor(COLORS['text']))
    palette.setColor(QPalette.Text, QColor(COLORS['text']))
    
    # Boutons
    palette.setColor(QPalette.Button, QColor(COLORS['primary']))
    palette.setColor(QPalette.ButtonText, QColor(COLORS['text']))
    palette.setColor(QPalette.BrightText, QColor(COLORS['text']))
    
    # Surlignage
    palette.setColor(QPalette.Highlight, QColor(COLORS['primary']))
    palette.setColor(QPalette.HighlightedText, QColor(COLORS['text']))
    
    # Liens
    palette.setColor(QPalette.Link, QColor(COLORS['accent']))
    palette.setColor(QPalette.LinkVisited, QColor(COLORS['secondary']))
    
    # Appliquer la palette
    app.setPalette(palette)
    
    # Définir une feuille de style globale pour tous les widgets
    app.setStyleSheet(f"""
        QToolTip {{
            border: 1px solid #5a6075;
            background-color: {COLORS['card_bg']};
            color: {COLORS['text']};
            padding: 8px;
            border-radius: 6px;
            font-size: 14px;
        }}
        QScrollBar:vertical {{
            border: none;
            background: {COLORS['background']};
            width: 12px;
            margin: 0px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: #5a6075;
            min-height: 30px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #778ca3;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            border: none;
            background: {COLORS['background']};
            height: 12px;
            margin: 0px;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background: #5a6075;
            min-width: 30px;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: #778ca3;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        QMessageBox {{
            background-color: {COLORS['card_bg']};
        }}
        QMessageBox QLabel {{
            color: {COLORS['text']};
            font-size: 14px;
        }}
        QMessageBox QPushButton {{
            background-color: {COLORS['primary']};
            color: {COLORS['text']};
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
            min-width: 100px;
        }}
        QMessageBox QPushButton:hover {{
            background-color: {COLORS['secondary']};
        }}
    """)


if __name__ == "__main__":
    # Initialiser l'application PyQt5
    app = QApplication(sys.argv)
    
    # Configurer le style et la palette de l'application
    set_application_style(app)
    
    # Créer et afficher la fenêtre principale
    main_window = FaceRecognizerApp()
    main_window.show()
    
    # Démarrer la boucle d'événements de l'application
    sys.exit(app.exec_()) 