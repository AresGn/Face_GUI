import os
import json
import logging
from datetime import datetime

# Configuration du logger
logging.basicConfig(filename='config.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Configuration:
    """Classe pour gérer la configuration de l'application"""
    
    def __init__(self, config_file='config.json'):
        """
        Initialiser la configuration
        
        Args:
            config_file (str): Chemin vers le fichier de configuration
        """
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """
        Charger la configuration depuis le fichier
        
        Returns:
            dict: La configuration chargée ou la configuration par défaut
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logging.info(f"Configuration chargée depuis {self.config_file}")
                return config
            else:
                # Créer une configuration par défaut
                config = self.get_default_config()
                self.save_config(config)
                return config
        except Exception as e:
            logging.error(f"Erreur lors du chargement de la configuration: {e}")
            return self.get_default_config()
    
    def save_config(self, config=None):
        """
        Sauvegarder la configuration dans le fichier
        
        Args:
            config (dict, optional): La configuration à sauvegarder
        
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            if config is None:
                config = self.config
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            logging.info(f"Configuration sauvegardée dans {self.config_file}")
            return True
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde de la configuration: {e}")
            return False
    
    def get_default_config(self):
        """
        Retourner la configuration par défaut
        
        Returns:
            dict: La configuration par défaut
        """
        return {
            "app": {
                "name": "Système de reconnaissance faciale - CITEX SART",
                "version": "1.0.0",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "database": {
                "path": "data/employees.db"
            },
            "face_recognition": {
                "min_confidence": 50,
                "max_images": 300,
                "cascade_file": "data/haarcascade_frontalface_default.xml"
            },
            "paths": {
                "faces_dir": "data/faces",
                "classifiers_dir": "data/classifiers",
                "attendance_dir": "data/attendance"
            },
            "export": {
                "default_format": "excel",
                "company_name": "CITEX SART",
                "report_title": "Rapport de présence des employés"
            },
            "ui": {
                "theme": "fusion",
                "language": "fr",
                "window_size": {
                    "width": 1024,
                    "height": 768
                }
            }
        }
    
    def get(self, key, default=None):
        """
        Obtenir une valeur de configuration
        
        Args:
            key (str): Clé de la configuration (peut être une clé imbriquée avec '.')
            default: Valeur par défaut si la clé n'existe pas
        
        Returns:
            La valeur de la configuration ou la valeur par défaut
        """
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value):
        """
        Définir une valeur de configuration
        
        Args:
            key (str): Clé de la configuration (peut être une clé imbriquée avec '.')
            value: Valeur à définir
        
        Returns:
            bool: True si la définition a réussi, False sinon
        """
        try:
            keys = key.split('.')
            config = self.config
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value
            return self.save_config()
        except Exception as e:
            logging.error(f"Erreur lors de la définition de la configuration: {e}")
            return False
    
    def ensure_directories(self):
        """
        S'assurer que tous les répertoires nécessaires existent
        
        Returns:
            bool: True si tous les répertoires existent ou ont été créés, False sinon
        """
        try:
            # Créer les répertoires définis dans la configuration
            for path_key, path_value in self.get('paths', {}).items():
                os.makedirs(path_value, exist_ok=True)
                logging.info(f"Répertoire créé/vérifié: {path_value}")
            
            # Créer le répertoire de la base de données
            db_path = self.get('database.path', 'data/employees.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            return True
        except Exception as e:
            logging.error(f"Erreur lors de la création des répertoires: {e}")
            return False

# Instance globale de la configuration
config = Configuration() 