import os
import json
import logging
from datetime import datetime

# Configuration du logger
logging.basicConfig(filename='config.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG_FILE = 'config.json'

# Configuration par défaut
DEFAULT_CONFIG = {
    'app': {
        'name': 'Système de reconnaissance faciale - CBT SARL',
        'version': '1.0.0'
    },
    'ui': {
        'window_size': {
            'width': 1200,
            'height': 800
        }
    },
    'camera': {
        'use_droid_cam': False,
        'droid_cam_url': 'http://192.168.1.X:4747/video',
        'use_esp32_cam': False,
        'esp32_cam_ip': '192.168.1.100',
        'esp32_cam_port': 80,
        'esp32_cam_stream_path': '/stream',
        'esp32_cam_quality': 10,
        'index': 0
    },
    'detection': {
        'min_confidence': 60,
        'required_frames': 5,
        'min_neighbors': 6,
        'scale_factor': 1.2,
        'min_size': [80, 80]
    }
}

class Config:
    def __init__(self):
        """Initialiser la configuration de l'application"""
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self):
        """Charger la configuration depuis le fichier JSON"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    loaded_config = json.load(f)
                    # Mise à jour récursive de la configuration
                    self._update_nested_dict(self.config, loaded_config)
                    logging.info("Configuration chargée avec succès")
            else:
                # Créer le fichier de configuration avec les valeurs par défaut
                self.save_config()
                logging.info("Nouveau fichier de configuration créé avec les valeurs par défaut")
        except Exception as e:
            logging.error(f"Erreur lors du chargement de la configuration: {e}")
    
    def save_config(self):
        """Enregistrer la configuration dans le fichier JSON"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            logging.info("Configuration enregistrée avec succès")
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'enregistrement de la configuration: {e}")
            return False
    
    def get(self, key_path, default=None):
        """
        Obtenir une valeur de configuration par son chemin d'accès
        
        Args:
            key_path (str): Chemin d'accès à la valeur (ex: 'camera.use_droid_cam')
            default: Valeur par défaut si la clé n'existe pas
        
        Returns:
            La valeur de configuration ou la valeur par défaut
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path, value):
        """
        Définir une valeur de configuration par son chemin d'accès
        
        Args:
            key_path (str): Chemin d'accès à la valeur (ex: 'camera.use_droid_cam')
            value: Nouvelle valeur à définir
        
        Returns:
            bool: True si la valeur a été définie avec succès, False sinon
        """
        keys = key_path.split('.')
        target = self.config
        
        # Naviguer jusqu'au dernier niveau de la hiérarchie
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        # Définir la valeur
        target[keys[-1]] = value
        
        # Enregistrer la configuration
        return self.save_config()
    
    def _update_nested_dict(self, d, u):
        """Mettre à jour récursivement un dictionnaire imbriqué"""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v

# Instance globale de la configuration
config = Config() 