# Face Recogniton GUI-APP


[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://www.youtube.com/channel/UCKvgGs-ALhvOq9u95PHXHNw)

# Live Demo
```html
https://www.youtube.com/embed/3EBdT-0gvu8

```


# A very Simple Gui app for Face Detection 

  - Collect Face Data
  - Build Face Classifier 
  - Detecte the face

#  New Features!

  - Add Emotion detection
  - Fixed image loading in Linux 
  
  
# Installation

1 : Install the requirements .

```sh
$ pip install -r  requirements.txt
```

2 : Run The App 

```sh
$ python app-gui.py
```

# APP GUI

### Home Page
![homepage](https://i.ibb.co/c62qvR2/home-page.png)

### Add a User <br>
Add the user you want to train a classifier for <br>
![page1](https://i.ibb.co/t8gdq6s/adduser.png)<br>


### Capture Data and Train Classifier<br>
Capture Data From the face then train the classifier<br>
![page2](https://i.ibb.co/D8JgYhN/capandtraindata.png)<br>

### Users List<br>
List of all the users<br>
![page3](https://i.ibb.co/1KwfVVV/dropdown.png)<br>

### Recognition <br>
A webcam window will popup and start recognition proccess<br>
![page4](https://i.ibb.co/sCtgDDC/4page.png)<br>
>![Face Recognition](https://i.ibb.co/bNpC5wR/jack.png)<br>
>![emotion](https://i.ibb.co/F7pdtjZ/emotion.png)<br>
>![Age and Gender](https://i.ibb.co/9q1L7sD/age.png)<br>



<br><br>

Made By ❤ : [JoeVenner](mailto:ylafrimi@gmail.com)<br>
**Free Software, Hell Yeah!**




Je comprends que vous souhaitez:

1. Réorganiser le projet avec une structure de dossiers plus propre (dossier src)
2. Créer une nouvelle interface avec PyQt5 pour une application de gestion de présence pour CITEX SART
3. Implémenter un système qui:
   - Enregistre les ouvriers (nom, prénom, matricule, poste)
   - Reconnaît les employés par reconnaissance faciale
   - Enregistre les présences dans un tableau (nom, heure, statut)
   - Permet d'exporter les données (PDF, Word)
   - Inclut un tableau de bord
4. Intégrer SQLite pour stocker les photos et informations

Voici mon plan d'implémentation:

## Plan d'organisation du projet

```
FaceRecognition-GUI/
├── src/
│   ├── core/
│   │   ├── face_detector.py (logique de reconnaissance faciale)
│   │   ├── dataset_creator.py (création des jeux de données)
│   │   └── classifier.py (entraînement du modèle)
│   ├── database/
│   │   ├── db_manager.py (gestion de la base de données SQLite)
│   │   └── schema.py (définition du schéma)
│   ├── ui/
│   │   ├── main_window.py (fenêtre principale)
│   │   ├── registration_page.py (page d'enregistrement employé)
│   │   ├── recognition_page.py (page de reconnaissance)
│   │   ├── attendance_page.py (tableau des présences)
│   │   └── dashboard_page.py (tableau de bord)
│   ├── utils/
│   │   ├── export.py (exportation PDF/Word)
│   │   └── config.py (configuration)
│   └── assets/
│       ├── icons/
│       └── styles/
├── data/
│   ├── attendance/ (fichiers d'exportation)
│   └── employees.db (base de données SQLite)
├── app.py (point d'entrée)
└── run_app.bat (script de lancement)
```

## Structure de la base de données

Tables proposées:
1. `employees` - Informations des employés (id, nom, prénom, matricule, poste)
2. `face_data` - Données des visages (employee_id, image_path)
3. `attendance` - Registre de présence (id, employee_id, date, heure_arrivée, statut)

## Flux de l'application

1. **Page d'accueil**
   - Bouton d'enregistrement d'employé
   - Bouton pour la prise de présence
   - Bouton pour consulter les présences
   - Accès au tableau de bord

2. **Enregistrement d'employé**
   - Formulaire (nom, prénom, matricule, poste)
   - Capture de photos pour l'entraînement du modèle
   - Sauvegarde dans la base de données

3. **Reconnaissance et prise de présence**
   - Caméra active pour reconnaître les employés
   - Affichage en temps réel des employés reconnus
   - Enregistrement automatique de l'heure d'arrivée

4. **Tableau des présences**
   - Liste des présences du jour
   - Filtrage par date/employé
   - Exportation (PDF, Word, Excel)

5. **Tableau de bord**
   - Statistiques de présence
   - Graphiques (taux de présence, retards, etc.)

Souhaitez-vous que je procède avec cette structure ou avez-vous des ajustements à proposer?


# Plan d'implémentation pour la fonctionnalité d'upload vidéo

Votre idée d'ajouter une option pour uploader une vidéo au lieu de la capture en direct est excellente et tout à fait réalisable. Cette fonctionnalité sera très utile pour les personnes qui ne peuvent pas se déplacer physiquement pour l'enregistrement.

## Composants nécessaires

1. **Interface utilisateur**:
   - Un bouton "Uploader une vidéo" comme alternative à "Capturer les images"
   - Un sélecteur de fichier (QFileDialog) pour choisir la vidéo
   - Un lecteur de prévisualisation vidéo (facultatif)
   - Une barre de progression pour le traitement

2. **Traitement vidéo**:
   - Nous utiliserons OpenCV (déjà implémenté) pour découper la vidéo en frames
   - Le même algorithme de détection faciale sera utilisé pour extraire les visages
   - Stockage des images extraites dans le même format que la capture directe

3. **Bibliothèques supplémentaires**:
   - Aucune bibliothèque supplémentaire n'est nécessaire car nous utilisons déjà OpenCV et PyQt5

## Plan d'implémentation

1. **Modification de l'interface utilisateur**:
   - Ajouter un GroupBox "Méthode d'enregistrement" avec deux options:
     - Option 1: Capture en direct (méthode actuelle)
     - Option 2: Upload vidéo (nouvelle méthode)
   - Ajouter un bouton "Sélectionner une vidéo" qui s'active lorsque l'option 2 est sélectionnée

2. **Création d'un nouveau thread**:
   - Créer une classe `VideoProcessorThread` similaire à `DatasetCreatorThread`
   - Cette classe prendra un chemin de vidéo en entrée au lieu de la caméra en direct
   - Elle utilisera `cv2.VideoCapture(video_path)` au lieu de `cv2.VideoCapture(0)`

3. **Extraction d'images de la vidéo**:
   - Lire la vidéo frame par frame
   - Échantillonner (par exemple, prendre une frame toutes les 5-10 frames) pour éviter la redondance
   - Utiliser la détection de visage sur chaque frame sélectionnée
   - Conserver uniquement les frames où un visage est clairement visible
   - Sauvegarder ces images dans le même format et dossier que la méthode actuelle

4. **Traitement et entraînement**:
   - Utiliser le même processus d'entraînement que celui déjà implémenté
   - La méthode `train_model()` peut rester inchangée

## Références existantes

Cette approche est similaire à plusieurs projets GitHub comme celui que vous avez mentionné avoir vu. Des projets comme [Face_recognition](https://github.com/JoaoIshida/Face_recognition) et d'autres utilisent déjà cette technique d'extraction d'images à partir de vidéos pour l'entraînement de modèles de reconnaissance faciale.

## Avantages

1. **Flexibilité**: Les utilisateurs peuvent s'enregistrer à distance
2. **Efficacité**: Peut-être même plus efficace que la capture en direct car la vidéo peut être de meilleure qualité
3. **Réutilisation du code**: Utilise majoritairement le code existant
4. **Interface intuitive**: Simple à comprendre pour les utilisateurs

Cette fonctionnalité devrait être relativement simple à implémenter en s'appuyant sur l'architecture existante de votre application.
