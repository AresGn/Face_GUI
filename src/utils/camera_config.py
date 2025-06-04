import cv2
import logging
import requests
import time
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

def configure_esp32cam(ip_address, port=80, stream_path="/stream", quality=10, use_esp32cam=True):
    """
    Configure l'utilisation de l'ESP32-CAM comme source vidéo

    Args:
        ip_address (str): Adresse IP de l'ESP32-CAM
        port (int): Port utilisé par l'ESP32-CAM (80 par défaut)
        stream_path (str): Chemin du flux vidéo (/stream par défaut)
        quality (int): Qualité JPEG (1-63, plus bas = meilleure qualité)
        use_esp32cam (bool): Activer ou désactiver l'utilisation de l'ESP32-CAM

    Returns:
        tuple: (bool, str) - (succès, message)
    """
    try:
        # Construire l'URL ESP32-CAM
        esp32_cam_url = f"http://{ip_address}:{port}{stream_path}"

        # Tester la connexion si ESP32-CAM est activé
        if use_esp32cam:
            # Vérifier d'abord si l'ESP32-CAM répond
            try:
                response = requests.get(f"http://{ip_address}:{port}", timeout=5)
                logging.info(f"ESP32-CAM accessible à l'adresse {ip_address}:{port}")
            except requests.exceptions.RequestException as e:
                logging.error(f"Impossible de joindre l'ESP32-CAM à {ip_address}:{port}")
                return False, f"ESP32-CAM non accessible ({ip_address}:{port}). Vérifiez l'adresse IP et la connexion réseau."

            # Tenter d'ouvrir le flux vidéo pour vérifier la connexion
            cap = cv2.VideoCapture(esp32_cam_url)
            if not cap.isOpened():
                logging.error(f"Impossible de se connecter au flux ESP32-CAM à l'adresse {esp32_cam_url}")
                return False, f"Échec de la connexion au flux vidéo ESP32-CAM ({ip_address}:{port}{stream_path})"

            # Tester la lecture d'une frame
            ret, frame = cap.read()
            if not ret or frame is None:
                cap.release()
                logging.error(f"Impossible de lire le flux vidéo ESP32-CAM")
                return False, f"Le flux vidéo ESP32-CAM ne fournit pas d'images valides"

            # Libérer la caméra après le test
            cap.release()
            logging.info(f"Connexion au flux ESP32-CAM réussie: {esp32_cam_url}")

        # Sauvegarder la configuration
        config.set('camera.use_esp32_cam', use_esp32cam)
        config.set('camera.esp32_cam_ip', ip_address)
        config.set('camera.esp32_cam_port', port)
        config.set('camera.esp32_cam_stream_path', stream_path)
        config.set('camera.esp32_cam_quality', quality)

        # Désactiver les autres sources de caméra si ESP32-CAM est activé
        if use_esp32cam:
            config.set('camera.use_droid_cam', False)

        message = f"ESP32-CAM configuré avec succès ({ip_address}:{port}{stream_path})" if use_esp32cam else "ESP32-CAM désactivé"
        logging.info(message)
        return True, message

    except Exception as e:
        logging.error(f"Erreur lors de la configuration ESP32-CAM: {e}")
        return False, f"Erreur de configuration ESP32-CAM: {str(e)}"

def test_esp32cam_connection(ip_address, port=80, stream_path="/stream"):
    """
    Teste la connexion à l'ESP32-CAM

    Args:
        ip_address (str): Adresse IP de l'ESP32-CAM
        port (int): Port utilisé par l'ESP32-CAM
        stream_path (str): Chemin du flux vidéo

    Returns:
        tuple: (bool, str) - (succès, message)
    """
    try:
        # Vérifier la connectivité de base
        response = requests.get(f"http://{ip_address}:{port}", timeout=5)

        # Tester le flux vidéo
        esp32_cam_url = f"http://{ip_address}:{port}{stream_path}"
        cap = cv2.VideoCapture(esp32_cam_url)

        if not cap.isOpened():
            return False, f"Impossible d'ouvrir le flux vidéo à {esp32_cam_url}"

        # Tester la lecture d'une frame
        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            return False, "Le flux vidéo ne fournit pas d'images valides"

        return True, f"ESP32-CAM connecté avec succès (Résolution: {frame.shape[1]}x{frame.shape[0]})"

    except requests.exceptions.RequestException:
        return False, f"ESP32-CAM non accessible à {ip_address}:{port}"
    except Exception as e:
        return False, f"Erreur de test: {str(e)}"

def get_esp32cam_info():
    """
    Récupère les informations de configuration ESP32-CAM

    Returns:
        dict: Informations de configuration ESP32-CAM
    """
    return {
        'enabled': config.get('camera.use_esp32_cam', False),
        'ip': config.get('camera.esp32_cam_ip', '192.168.1.100'),
        'port': config.get('camera.esp32_cam_port', 80),
        'stream_path': config.get('camera.esp32_cam_stream_path', '/stream'),
        'quality': config.get('camera.esp32_cam_quality', 10)
    }