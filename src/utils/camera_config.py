import cv2
import logging
from .config import config

# Configuration du logger
logging.basicConfig(filename='camera_config.log', level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

def configure_droidcam(ip_address, port=4747, use_droidcam=True):
    """
    Configure l'utilisation de DroidCam comme source vidéo
    
    Args:
        ip_address (str): Adresse IP du smartphone
        port (int): Port utilisé par DroidCam (4747 par défaut)
        use_droidcam (bool): Activer ou désactiver l'utilisation de DroidCam
        
    Returns:
        bool: True si la configuration a réussi, False sinon
    """
    try:
        # Construire l'URL DroidCam
        droid_cam_url = f"http://{ip_address}:{port}/video"
        
        # Tester la connexion si DroidCam est activé
        if use_droidcam:
            # Tenter d'ouvrir la caméra pour vérifier la connexion
            cap = cv2.VideoCapture(droid_cam_url)
            if not cap.isOpened():
                logging.error(f"Impossible de se connecter à DroidCam à l'adresse {droid_cam_url}")
                return False, f"Échec de la connexion à DroidCam ({ip_address}:{port})"
            
            # Libérer la caméra après le test
            cap.release()
            logging.info(f"Connexion à DroidCam réussie: {droid_cam_url}")
        
        # Sauvegarder les paramètres dans la configuration
        config.set('camera.use_droid_cam', use_droidcam)
        config.set('camera.droid_cam_url', droid_cam_url)
        
        logging.info(f"Configuration DroidCam mise à jour: {droid_cam_url}, Activé: {use_droidcam}")
        return True, f"DroidCam configuré avec succès: {ip_address}:{port}"
    
    except Exception as e:
        logging.error(f"Erreur lors de la configuration de DroidCam: {e}")
        return False, f"Erreur: {str(e)}"

def list_available_cameras():
    """
    Liste les caméras disponibles sur le système
    
    Returns:
        list: Liste des indices de caméras disponibles
    """
    available_cameras = []
    
    # Tester les 5 premiers indices (généralement suffisant pour la plupart des systèmes)
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
    
    logging.info(f"Caméras disponibles: {available_cameras}")
    return available_cameras

def set_default_camera(camera_index):
    """
    Définit la caméra par défaut à utiliser
    
    Args:
        camera_index (int): Indice de la caméra
        
    Returns:
        bool: True si la configuration a réussi, False sinon
    """
    try:
        # Vérifier si la caméra est disponible
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            logging.error(f"La caméra avec l'indice {camera_index} n'est pas disponible")
            return False, f"Caméra {camera_index} non disponible"
        
        # Libérer la caméra après le test
        cap.release()
        
        # Désactiver DroidCam si une caméra locale est sélectionnée
        config.set('camera.use_droid_cam', False)
        config.set('camera.index', camera_index)
        
        logging.info(f"Caméra par défaut définie: {camera_index}")
        return True, f"Caméra {camera_index} configurée comme caméra par défaut"
    
    except Exception as e:
        logging.error(f"Erreur lors de la configuration de la caméra par défaut: {e}")
        return False, f"Erreur: {str(e)}" 