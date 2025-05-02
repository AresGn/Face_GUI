import sqlite3
import os
import datetime
import logging

# Configuration du logger
logging.basicConfig(filename='database.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:
    def __init__(self, db_path='data/employees.db'):
        """Initialiser le gestionnaire de base de données avec le chemin spécifié"""
        # Créer le répertoire de la base de données s'il n'existe pas
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Initialiser la base de données
        self._create_tables()
    
    def connect(self):
        """Établir une connexion à la base de données"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            logging.error(f"Erreur de connexion à la base de données: {e}")
            return False
    
    def disconnect(self):
        """Fermer la connexion à la base de données"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def _create_tables(self):
        """Créer les tables nécessaires si elles n'existent pas"""
        if not self.connect():
            return False
        
        try:
            # Table des employés
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    matricule TEXT UNIQUE NOT NULL,
                    poste TEXT NOT NULL,
                    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des données de visage
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS face_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    image_path TEXT NOT NULL,
                    FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE
                )
            ''')
            
            # Table des présences
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    heure_arrivee TIME NOT NULL,
                    statut TEXT NOT NULL DEFAULT 'Present',
                    FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE
                )
            ''')
            
            self.conn.commit()
            logging.info("Tables créées avec succès")
            return True
        except sqlite3.Error as e:
            logging.error(f"Erreur lors de la création des tables: {e}")
            self.conn.rollback()
            return False
        finally:
            self.disconnect()
    
    # Méthodes pour les employés
    def add_employee(self, nom, prenom, matricule, poste):
        """Ajouter un nouvel employé à la base de données"""
        if not self.connect():
            return None
        
        try:
            self.cursor.execute('''
                INSERT INTO employees (nom, prenom, matricule, poste)
                VALUES (?, ?, ?, ?)
            ''', (nom, prenom, matricule, poste))
            
            self.conn.commit()
            employee_id = self.cursor.lastrowid
            logging.info(f"Employé ajouté avec succès: ID={employee_id}")
            return employee_id
        except sqlite3.Error as e:
            logging.error(f"Erreur lors de l'ajout d'un employé: {e}")
            self.conn.rollback()
            return None
        finally:
            self.disconnect()
    
    def get_employee_by_id(self, employee_id):
        """Récupérer les informations d'un employé par son ID"""
        if not self.connect():
            return None
        
        try:
            self.cursor.execute('''
                SELECT id, nom, prenom, matricule, poste, date_creation
                FROM employees
                WHERE id = ?
            ''', (employee_id,))
            
            employee = self.cursor.fetchone()
            if employee:
                return {
                    'id': employee[0],
                    'nom': employee[1],
                    'prenom': employee[2],
                    'matricule': employee[3],
                    'poste': employee[4],
                    'date_creation': employee[5]
                }
            return None
        except sqlite3.Error as e:
            logging.error(f"Erreur lors de la récupération d'un employé: {e}")
            return None
        finally:
            self.disconnect()
    
    def get_all_employees(self):
        """Récupérer tous les employés"""
        if not self.connect():
            return []
        
        try:
            self.cursor.execute('''
                SELECT id, nom, prenom, matricule, poste, date_creation
                FROM employees
                ORDER BY nom, prenom
            ''')
            
            employees = self.cursor.fetchall()
            result = []
            for employee in employees:
                result.append({
                    'id': employee[0],
                    'nom': employee[1],
                    'prenom': employee[2],
                    'matricule': employee[3],
                    'poste': employee[4],
                    'date_creation': employee[5]
                })
            return result
        except sqlite3.Error as e:
            logging.error(f"Erreur lors de la récupération des employés: {e}")
            return []
        finally:
            self.disconnect()
    
    def get_employee_by_name(self, nom, prenom):
        """Récupérer les informations d'un employé par son nom complet"""
        if not self.connect():
            return None
        
        try:
            self.cursor.execute('''
                SELECT id, nom, prenom, matricule, poste, date_creation
                FROM employees
                WHERE nom = ? AND prenom = ?
            ''', (nom, prenom))
            
            employee = self.cursor.fetchone()
            if employee:
                return {
                    'id': employee[0],
                    'nom': employee[1],
                    'prenom': employee[2],
                    'matricule': employee[3],
                    'poste': employee[4],
                    'date_creation': employee[5]
                }
            return None
        except sqlite3.Error as e:
            logging.error(f"Erreur lors de la récupération d'un employé par nom: {e}")
            return None
        finally:
            self.disconnect()
    
    def delete_employee(self, employee_id):
        """Supprimer un employé et toutes ses données associées"""
        if not self.connect():
            return False
        
        try:
            # Vérifier si l'employé existe
            self.cursor.execute('SELECT id FROM employees WHERE id = ?', (employee_id,))
            employee = self.cursor.fetchone()
            if not employee:
                logging.warning(f"Tentative de suppression d'un employé inexistant: ID={employee_id}")
                return False
            
            # Supprimer l'employé
            self.cursor.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
            
            # Les données associées seront supprimées automatiquement grâce aux contraintes ON DELETE CASCADE
            
            self.conn.commit()
            logging.info(f"Employé supprimé avec succès: ID={employee_id}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Erreur lors de la suppression d'un employé: {e}")
            self.conn.rollback()
            return False
        finally:
            self.disconnect()
    
    # Méthodes pour les données de visage
    def add_face_data(self, employee_id, image_path):
        """Ajouter une image de visage pour un employé"""
        if not self.connect():
            return False
        
        try:
            self.cursor.execute('''
                INSERT INTO face_data (employee_id, image_path)
                VALUES (?, ?)
            ''', (employee_id, image_path))
            
            self.conn.commit()
            logging.info(f"Données de visage ajoutées pour l'employé ID={employee_id}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Erreur lors de l'ajout des données de visage: {e}")
            self.conn.rollback()
            return False
        finally:
            self.disconnect()
    
    def get_face_data(self, employee_id):
        """Récupérer toutes les images de visage pour un employé"""
        if not self.connect():
            return []
        
        try:
            self.cursor.execute('''
                SELECT id, image_path
                FROM face_data
                WHERE employee_id = ?
            ''', (employee_id,))
            
            face_data = self.cursor.fetchall()
            result = []
            for data in face_data:
                result.append({
                    'id': data[0],
                    'image_path': data[1]
                })
            return result
        except sqlite3.Error as e:
            logging.error(f"Erreur lors de la récupération des données de visage: {e}")
            return []
        finally:
            self.disconnect()
    
    # Méthodes pour les présences
    def mark_attendance(self, employee_id, date=None, heure=None, statut="Present"):
        """Marquer la présence d'un employé"""
        if not self.connect():
            return False
        
        try:
            if date is None:
                date = datetime.date.today().isoformat()
            if heure is None:
                heure = datetime.datetime.now().strftime("%H:%M:%S")
            
            # Vérifier si l'employé a déjà été marqué présent aujourd'hui
            self.cursor.execute('''
                SELECT id FROM attendance
                WHERE employee_id = ? AND date = ?
            ''', (employee_id, date))
            
            existing = self.cursor.fetchone()
            if existing:
                logging.info(f"L'employé ID={employee_id} a déjà été marqué présent aujourd'hui")
                return False
            
            self.cursor.execute('''
                INSERT INTO attendance (employee_id, date, heure_arrivee, statut)
                VALUES (?, ?, ?, ?)
            ''', (employee_id, date, heure, statut))
            
            self.conn.commit()
            logging.info(f"Présence marquée pour l'employé ID={employee_id}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Erreur lors du marquage de présence: {e}")
            self.conn.rollback()
            return False
        finally:
            self.disconnect()
    
    def get_attendance(self, date=None):
        """Récupérer les présences pour une date spécifique ou toutes les présences"""
        if not self.connect():
            return []
        
        try:
            query = '''
                SELECT a.id, a.employee_id, a.date, a.heure_arrivee, a.statut,
                       e.nom, e.prenom, e.matricule, e.poste
                FROM attendance a
                JOIN employees e ON a.employee_id = e.id
            '''
            params = ()
            
            if date:
                query += " WHERE a.date = ?"
                params = (date,)
            
            query += " ORDER BY a.date DESC, a.heure_arrivee"
            
            self.cursor.execute(query, params)
            
            attendances = self.cursor.fetchall()
            result = []
            for att in attendances:
                result.append({
                    'id': att[0],
                    'employee_id': att[1],
                    'date': att[2],
                    'heure_arrivee': att[3],
                    'statut': att[4],
                    'nom': att[5],
                    'prenom': att[6],
                    'matricule': att[7],
                    'poste': att[8]
                })
            return result
        except sqlite3.Error as e:
            logging.error(f"Erreur lors de la récupération des présences: {e}")
            return []
        finally:
            self.disconnect()
    
    def get_employee_attendance(self, employee_id, start_date=None, end_date=None):
        """Récupérer les présences d'un employé sur une période"""
        if not self.connect():
            return []
        
        try:
            query = '''
                SELECT a.id, a.date, a.heure_arrivee, a.statut
                FROM attendance a
                WHERE a.employee_id = ?
            '''
            params = [employee_id]
            
            if start_date:
                query += " AND a.date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND a.date <= ?"
                params.append(end_date)
            
            query += " ORDER BY a.date DESC, a.heure_arrivee"
            
            self.cursor.execute(query, tuple(params))
            
            attendances = self.cursor.fetchall()
            result = []
            for att in attendances:
                result.append({
                    'id': att[0],
                    'date': att[1],
                    'heure_arrivee': att[2],
                    'statut': att[3]
                })
            return result
        except sqlite3.Error as e:
            logging.error(f"Erreur lors de la récupération des présences d'un employé: {e}")
            return []
        finally:
            self.disconnect()

# Instance globale du gestionnaire de base de données
db_manager = DatabaseManager() 