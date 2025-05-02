import sys
import logging
import os

# Add src's parent directory to path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from ui.main_ui import MainUI
from database.db_manager import db_manager

# Configuration du logger
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def delete_employee_id2():
    """Supprimer l'employé avec l'ID 2 s'il existe"""
    try:
        # Vérifier si l'employé existe
        employee = db_manager.get_employee_by_id(2)
        if employee:
            # Supprimer l'employé
            success = db_manager.delete_employee(2)
            if success:
                logging.info("Employé ID=2 supprimé avec succès")
                print("Employé ID=2 supprimé avec succès")
            else:
                logging.warning("Échec de la suppression de l'employé ID=2")
                print("Échec de la suppression de l'employé ID=2")
        else:
            logging.info("Aucun employé avec ID=2 trouvé")
            print("Aucun employé avec ID=2 trouvé")
    except Exception as e:
        logging.error(f"Erreur lors de la suppression de l'employé ID=2: {e}")
        print(f"Erreur lors de la suppression de l'employé ID=2: {e}")

class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        """Initialiser la fenêtre principale"""
        super().__init__()
        
        # Configurer la fenêtre
        self.setWindowTitle("Système de Reconnaissance Faciale")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("assets/icon.png"))
        
        # Créer l'interface utilisateur
        self.main_ui = MainUI(self)
        self.setCentralWidget(self.main_ui)
        
        # Journal
        logging.info("Application démarrée")
    
    def closeEvent(self, event):
        """Gérer l'événement de fermeture de la fenêtre"""
        # Afficher une boîte de dialogue de confirmation
        reply = QMessageBox.question(
            self, "Confirmation",
            "Êtes-vous sûr de vouloir quitter l'application?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Accepter l'événement
            event.accept()
            logging.info("Application fermée")
        else:
            # Ignorer l'événement
            event.ignore()

if __name__ == "__main__":
    # Supprimer l'employé ID=2 pour résoudre le problème
    delete_employee_id2()
    
    # Créer l'application
    app = QApplication(sys.argv)
    
    # Appliquer la feuille de style
    with open("assets/style.css", "r") as style_file:
        app.setStyleSheet(style_file.read())
    
    # Créer la fenêtre principale
    window = MainWindow()
    window.show()
    
    # Exécuter l'application
    sys.exit(app.exec_()) 