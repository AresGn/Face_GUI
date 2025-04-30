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
