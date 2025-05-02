import os
import shutil
import logging
import sqlite3

# Configuration du logger
logging.basicConfig(filename='reset_db.log', level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

def reset_database():
    """
    Réinitialise complètement la base de données et supprime toutes les données d'entraînement
    """
    try:
        # 1. Supprimer la base de données
        db_path = 'data/employees.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            logging.info(f"Base de données supprimée: {db_path}")
        
        # 2. Supprimer les données de visage
        faces_dir = 'data/faces'
        if os.path.exists(faces_dir):
            shutil.rmtree(faces_dir)
            os.makedirs(faces_dir)
            logging.info(f"Répertoire des visages réinitialisé: {faces_dir}")
        
        # 3. Supprimer les classificateurs
        classifiers_dir = 'data/classifiers'
        if os.path.exists(classifiers_dir):
            shutil.rmtree(classifiers_dir)
            os.makedirs(classifiers_dir)
            logging.info(f"Répertoire des classificateurs réinitialisé: {classifiers_dir}")
        
        # 4. Recréer une base de données vide avec la structure correcte
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Recréer les tables nécessaires
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                matricule TEXT UNIQUE NOT NULL,
                poste TEXT NOT NULL,
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS face_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                date DATE NOT NULL,
                heure_arrivee TIME NOT NULL,
                statut TEXT NOT NULL DEFAULT 'Present',
                FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logging.info("Réinitialisation de la base de données terminée avec succès")
        return True, "Base de données réinitialisée avec succès"
    
    except Exception as e:
        logging.error(f"Erreur lors de la réinitialisation de la base de données: {e}")
        return False, f"Erreur lors de la réinitialisation: {str(e)}"

if __name__ == "__main__":
    # Permet d'exécuter la réinitialisation directement
    success, message = reset_database()
    print(message) 