# Guide d'intégration ESP32-CAM avec le système de reconnaissance faciale

## Vue d'ensemble

L'ESP32-CAM a été intégré avec succès dans votre système de reconnaissance faciale existant. Cette intégration utilise l'approche hybride Arduino/Python recommandée, où l'ESP32-CAM fournit le flux vidéo via Wi-Fi et le traitement de reconnaissance faciale est effectué sur votre PC.

## Prérequis matériels

### Composants nécessaires
- **ESP32-CAM AI Thinker** avec caméra OV2640
- **Programmeur FTDI** (pour l'upload du firmware)
- **Câbles de connexion** femelle-femelle
- **Alimentation 5V** (optionnelle, peut être alimenté via FTDI)

### Connexions pour la programmation
```
ESP32-CAM    <->    FTDI
VCC          <->    5V (ou 3.3V)
GND          <->    GND
U0R          <->    TX
U0T          <->    RX
IO0          <->    GND (seulement pour la programmation)
```

**Important :** Connecter IO0 à GND uniquement pendant l'upload, puis déconnecter et redémarrer l'ESP32-CAM.

## Installation du firmware

### 1. Configuration Arduino IDE
1. Ouvrir Arduino IDE
2. Aller dans **Fichier > Préférences**
3. Ajouter cette URL dans "URLs de gestionnaire de cartes supplémentaires" :
   ```
   https://dl.espressif.com/dl/package_esp32_index.json
   ```
4. Aller dans **Outils > Type de carte > Gestionnaire de cartes**
5. Rechercher "ESP32" et installer "ESP32 by Espressif Systems"
6. Sélectionner **Outils > Type de carte > ESP32 Arduino > AI Thinker ESP32-CAM**

### 2. Configuration de la carte
- **Carte :** AI Thinker ESP32-CAM
- **Partition Scheme :** Huge APP (3MB No OTA/1MB SPIFFS)
- **Port :** Sélectionner le port COM de votre FTDI

### 3. Upload du firmware
1. Ouvrir le fichier `ESP32-CAM_FaceRecognition.ino`
2. Modifier les paramètres Wi-Fi :
   ```cpp
   const char* ssid = "VOTRE_SSID";
   const char* password = "VOTRE_MOT_DE_PASSE";
   ```
3. Connecter IO0 à GND
4. Appuyer sur le bouton Reset de l'ESP32-CAM
5. Cliquer sur "Téléverser" dans Arduino IDE
6. Une fois l'upload terminé, déconnecter IO0 de GND
7. Redémarrer l'ESP32-CAM

## Configuration du système

### 1. Via l'interface graphique
1. Lancer l'application de reconnaissance faciale
2. Aller dans **Paramètres > Caméra**
3. Sélectionner **"Utiliser ESP32-CAM (module caméra Wi-Fi)"**
4. Remplir les paramètres :
   - **Adresse IP :** L'IP affichée dans le moniteur série Arduino
   - **Port :** 80 (par défaut)
   - **Chemin du flux :** /stream (par défaut)
   - **Qualité JPEG :** 10 (recommandé pour reconnaissance faciale)
5. Cliquer sur **"Tester la connexion ESP32-CAM"**
6. Si le test réussit, cliquer sur **"Sauvegarder"**

### 2. Via le script de configuration
```bash
python configure_droidcam.py
```
Choisir l'option **"2. Utiliser ESP32-CAM"** et suivre les instructions.

## Fonctionnalités

### Interface web ESP32-CAM
L'ESP32-CAM fournit une interface web accessible à `http://[IP_ESP32]/` avec :
- **Flux vidéo en direct**
- **Contrôle du flash LED**
- **Informations de statut** (FPS, mémoire libre)
- **Redémarrage à distance**

### Optimisations pour reconnaissance faciale
Le firmware inclut des optimisations spécifiques :
- **Résolution VGA (640x480)** optimale pour la détection de visages
- **Qualité JPEG ajustable** (1-63, plus bas = meilleure qualité)
- **Configuration automatique du capteur** pour de meilleures performances
- **Gestion de la reconnexion Wi-Fi** automatique
- **Double buffering** si PSRAM disponible

## Dépannage

### Problèmes courants

#### 1. ESP32-CAM non accessible
**Symptômes :** Impossible de se connecter à l'ESP32-CAM
**Solutions :**
- Vérifier que l'ESP32-CAM et le PC sont sur le même réseau Wi-Fi
- Vérifier l'adresse IP dans le moniteur série Arduino
- Redémarrer l'ESP32-CAM
- Vérifier les paramètres Wi-Fi dans le code

#### 2. Flux vidéo de mauvaise qualité
**Symptômes :** Images floues ou pixelisées
**Solutions :**
- Ajuster la qualité JPEG (valeur plus basse = meilleure qualité)
- Vérifier l'éclairage de la zone de capture
- Nettoyer l'objectif de la caméra
- Vérifier la stabilité de la connexion Wi-Fi

#### 3. Reconnaissance faciale lente
**Symptômes :** Détection lente ou saccadée
**Solutions :**
- Réduire la résolution si nécessaire
- Améliorer la qualité du signal Wi-Fi
- Vérifier les performances du PC
- Ajuster les paramètres de détection dans l'application

#### 4. Déconnexions fréquentes
**Symptômes :** Perte de connexion régulière
**Solutions :**
- Vérifier la stabilité de l'alimentation de l'ESP32-CAM
- Améliorer la qualité du signal Wi-Fi
- Vérifier la température de l'ESP32-CAM
- Redémarrer le routeur Wi-Fi

### Codes d'erreur

| Code | Description | Solution |
|------|-------------|----------|
| 0x20001 | Erreur initialisation caméra | Vérifier les connexions de la caméra |
| 0x20002 | Erreur allocation mémoire | Redémarrer l'ESP32-CAM |
| 0x105 | Erreur Wi-Fi | Vérifier SSID/mot de passe |

## Maintenance

### Mise à jour du firmware
1. Télécharger la dernière version du firmware
2. Suivre la procédure d'installation
3. Reconfigurer les paramètres Wi-Fi si nécessaire

### Surveillance des performances
- Surveiller le FPS via l'interface web
- Vérifier la mémoire libre régulièrement
- Contrôler la température de fonctionnement

## Spécifications techniques

### ESP32-CAM
- **Processeur :** ESP32 dual-core 32-bit LX6
- **Fréquence :** Jusqu'à 240 MHz
- **Mémoire :** 520 KB SRAM + 4 MB PSRAM (optionnel)
- **Wi-Fi :** 802.11 b/g/n
- **Caméra :** OV2640 2MP
- **Résolutions supportées :** UXGA (1600x1200), SXGA (1280x1024), VGA (640x480), etc.

### Performances
- **FPS :** Jusqu'à 30 FPS en VGA
- **Latence :** < 100ms sur réseau local
- **Portée Wi-Fi :** Jusqu'à 50m en intérieur
- **Consommation :** ~200mA en fonctionnement

## Support

Pour toute question ou problème :
1. Consulter ce guide de dépannage
2. Vérifier les logs dans le moniteur série Arduino
3. Tester la connectivité réseau
4. Vérifier la configuration dans l'application

---

**Note :** Ce guide couvre l'intégration de base. Pour des configurations avancées ou des problèmes spécifiques, consultez la documentation technique de l'ESP32-CAM.
