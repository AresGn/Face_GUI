import os
import logging
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QComboBox, QGroupBox, QMessageBox, QFrame, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDateEdit, QSizePolicy,
                             QLineEdit, QFormLayout)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QDate

# Importer les modules database et utils
from database.db_manager import db_manager
from utils.export import data_exporter

# Configuration du logger
logging.basicConfig(filename='attendance.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Appliquer le style pour tous les QGroupBox dans cette page
GROUP_BOX_STYLE = """
    QGroupBox {
        font-size: 18px;
        font-weight: bold;
        margin-top: 40px;
        padding-top: 50px;
        border: 2px solid #3867d6;
        border-radius: 10px;
    }
    QGroupBox::title {
        color: white;
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 8px 30px;
        background-color: #3867d6;
        border-radius: 6px;
        min-width: 150px;
    }
    QLabel {
        font-size: 15px;
        font-weight: bold;
        color: white;
        margin: 5px;
    }
"""

class AttendancePage(QWidget):
    """Page d'affichage des présences"""
    
    def __init__(self):
        """Initialiser la page des présences"""
        super().__init__()
        
        # Initialiser l'interface utilisateur
        self.init_ui()
        
        # Charger les présences pour aujourd'hui par défaut
        self.load_attendance()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        # Créer le layout principal
        main_layout = QVBoxLayout()
        
        # Titre de la page
        title_label = QLabel("Registre des présences")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Créer la section des filtres
        filters_group = self.create_filters_section()
        main_layout.addWidget(filters_group)
        
        # Créer la section du tableau des présences
        table_layout = self.create_table_section()
        main_layout.addLayout(table_layout, 1)  # 1 est le facteur d'étirement
        
        # Créer la section des actions
        actions_group = self.create_actions_section()
        main_layout.addWidget(actions_group)
        
        # Définir le layout pour ce widget
        self.setLayout(main_layout)
    
    def create_filters_section(self):
        """Créer la section des filtres"""
        filters_group = QGroupBox("Filtres de recherche")
        filters_group.setStyleSheet(GROUP_BOX_STYLE)
        
        filters_layout = QVBoxLayout()
        filters_layout.setContentsMargins(20, 20, 20, 20)
        
        # Formulaire des filtres
        form_layout = QFormLayout()
        
        # Filtre par date
        self.date_filter = QDateEdit()
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.setCalendarPopup(True)
        form_layout.addRow("Date:", self.date_filter)
        
        # Filtre par employé
        self.employee_filter = QComboBox()
        self.employee_filter.addItem("Tous les employés", None)
        
        # Charger la liste des employés
        employees = db_manager.get_all_employees()
        for employee in employees:
            self.employee_filter.addItem(
                f"{employee['prenom']} {employee['nom']} ({employee['matricule']})",
                employee['id']
            )
        
        form_layout.addRow("Employé:", self.employee_filter)
        
        # Filtre par statut
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tous", "Present", "Absent"])
        form_layout.addRow("Statut:", self.status_filter)
        
        # Recherche par nom ou matricule
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        form_layout.addRow("Recherche:", self.search_input)
        
        # Ajouter le formulaire au layout des filtres
        filters_layout.addLayout(form_layout)
        
        # Boutons des filtres
        buttons_layout = QVBoxLayout()
        
        # Bouton d'application des filtres
        self.apply_btn = QPushButton("Appliquer")
        self.apply_btn.clicked.connect(self.load_attendance)
        buttons_layout.addWidget(self.apply_btn)
        
        # Bouton de réinitialisation des filtres
        self.reset_btn = QPushButton("Réinitialiser")
        self.reset_btn.clicked.connect(self.reset_filters)
        buttons_layout.addWidget(self.reset_btn)
        
        # Ajouter les boutons au layout des filtres
        filters_layout.addLayout(buttons_layout)
        
        # Définir le layout pour le groupe des filtres
        filters_group.setLayout(filters_layout)
        
        return filters_group
    
    def create_table_section(self):
        """Créer la section du tableau des présences"""
        table_layout = QVBoxLayout()
        
        # Créer le tableau des présences
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(7)
        self.attendance_table.setHorizontalHeaderLabels([
            "ID", "Nom", "Prénom", "Matricule", "Poste", "Heure d'arrivée", "Statut"
        ])
        
        # Ajuster la taille des colonnes
        self.attendance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Permettre la sélection par ligne
        self.attendance_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Ajouter le tableau au layout
        table_layout.addWidget(self.attendance_table)
        
        # Étiquette pour afficher le nombre d'enregistrements
        self.records_label = QLabel("0 enregistrement(s)")
        self.records_label.setAlignment(Qt.AlignCenter)
        table_layout.addWidget(self.records_label)
        
        return table_layout
    
    def create_actions_section(self):
        """Créer la section des actions"""
        actions_group = QGroupBox("Actions")
        actions_group.setStyleSheet(GROUP_BOX_STYLE)
        
        actions_layout = QHBoxLayout()
        
        # Bouton d'exportation
        self.export_btn = QPushButton("Exporter")
        self.export_btn.clicked.connect(self.export_data)
        actions_layout.addWidget(self.export_btn)
        
        # Bouton d'impression
        self.print_btn = QPushButton("Imprimer")
        self.print_btn.clicked.connect(self.print_data)
        actions_layout.addWidget(self.print_btn)
        
        # Bouton de rafraîchissement
        self.refresh_btn = QPushButton("Rafraîchir")
        self.refresh_btn.clicked.connect(self.load_attendance)
        actions_layout.addWidget(self.refresh_btn)
        
        # Définir le layout pour le groupe des actions
        actions_group.setLayout(actions_layout)
        
        return actions_group
    
    def load_attendance(self):
        """Charger les données de présence selon les filtres"""
        try:
            # Récupérer les valeurs des filtres
            selected_date = self.date_filter.date().toString("yyyy-MM-dd")
            employee_id = self.employee_filter.currentData()
            status = self.status_filter.currentText()
            search_text = self.search_input.text().strip().lower()
            
            # Afficher les données de debug
            logging.info(f"Chargement des présences avec filtres: Date={selected_date}, Employé={employee_id}, Statut={status}, Recherche={search_text}")
            
            # Récupérer les présences pour la date sélectionnée
            if status == "Tous":
                status = None
            
            # Récupérer les présences selon les filtres
            records = []
            
            # Récupérer toutes les présences pour la date sélectionnée d'abord
            all_records = db_manager.get_attendance(selected_date)
            logging.info(f"Nombre total de présences récupérées pour la date {selected_date}: {len(all_records)}")
            
            # Filtrer par employé si nécessaire
            if employee_id:
                records = [r for r in all_records if r.get('employee_id') == employee_id]
                logging.info(f"Après filtrage par employé: {len(records)} enregistrements")
            else:
                records = all_records
            
            # Filtrer par statut si nécessaire
            if status:
                records = [r for r in records if r.get('statut') == status]
                logging.info(f"Après filtrage par statut: {len(records)} enregistrements")
            
            # Filtrer par texte de recherche si nécessaire
            if search_text:
                filtered_records = []
                for record in records:
                    # Vérifier si le texte de recherche est dans le nom, prénom ou matricule
                    if (search_text in record.get('nom', '').lower() or
                        search_text in record.get('prenom', '').lower() or
                        search_text in record.get('matricule', '').lower()):
                        filtered_records.append(record)
                records = filtered_records
                logging.info(f"Après filtrage par recherche: {len(records)} enregistrements")
            
            # Effacer le tableau
            self.attendance_table.setRowCount(0)
            
            # Remplir le tableau avec les données
            for row, record in enumerate(records):
                self.attendance_table.insertRow(row)
                self.attendance_table.setItem(row, 0, QTableWidgetItem(str(record.get('employee_id', ''))))
                self.attendance_table.setItem(row, 1, QTableWidgetItem(record.get('nom', '')))
                self.attendance_table.setItem(row, 2, QTableWidgetItem(record.get('prenom', '')))
                self.attendance_table.setItem(row, 3, QTableWidgetItem(record.get('matricule', '')))
                self.attendance_table.setItem(row, 4, QTableWidgetItem(record.get('poste', '')))
                self.attendance_table.setItem(row, 5, QTableWidgetItem(record.get('heure_arrivee', '')))
                self.attendance_table.setItem(row, 6, QTableWidgetItem(record.get('statut', '')))
            
            # Mettre à jour le nombre d'enregistrements
            self.records_label.setText(f"{len(records)} enregistrement(s)")
            
            # Journal
            logging.info(f"Présences chargées: {len(records)} enregistrement(s)")
        
        except Exception as e:
            # Afficher un message d'erreur
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des présences: {e}")
            logging.error(f"Erreur lors du chargement des présences: {e}")
            # Ajouter plus de détails sur l'erreur
            import traceback
            logging.error(traceback.format_exc())
    
    def reset_filters(self):
        """Réinitialiser les filtres"""
        # Réinitialiser la date à aujourd'hui
        self.date_filter.setDate(QDate.currentDate())
        
        # Réinitialiser l'employé à "Tous les employés"
        self.employee_filter.setCurrentIndex(0)
        
        # Réinitialiser le statut à "Tous"
        self.status_filter.setCurrentIndex(0)
        
        # Effacer le texte de recherche
        self.search_input.clear()
        
        # Recharger les présences
        self.load_attendance()
        
        # Journal
        logging.info("Filtres réinitialisés")
    
    def export_data(self):
        """Exporter les données de présence"""
        # Récupérer les données du tableau
        rows = self.attendance_table.rowCount()
        if rows == 0:
            QMessageBox.warning(self, "Avertissement", "Aucune donnée à exporter.")
            return
        
        # Préparer les données pour l'exportation
        data = []
        for row in range(rows):
            record = {
                'employee_id': int(self.attendance_table.item(row, 0).text()),
                'nom': self.attendance_table.item(row, 1).text(),
                'prenom': self.attendance_table.item(row, 2).text(),
                'matricule': self.attendance_table.item(row, 3).text(),
                'poste': self.attendance_table.item(row, 4).text(),
                'date': self.date_filter.date().toString("yyyy-MM-dd"),
                'heure_arrivee': self.attendance_table.item(row, 5).text(),
                'statut': self.attendance_table.item(row, 6).text()
            }
            data.append(record)
        
        # Afficher la boîte de dialogue d'exportation
        result = data_exporter.show_export_dialog(data, self)
        
        if result:
            # Journal
            logging.info(f"Données exportées: {len(data)} enregistrement(s)")
    
    def print_data(self):
        """Imprimer les données de présence"""
        # À implémenter
        QMessageBox.information(self, "Information", "La fonctionnalité d'impression n'est pas encore implémentée.")
        
        # Journal
        logging.info("Tentative d'impression (non implémentée)")
    
    def closeEvent(self, event):
        """Gérer l'événement de fermeture de la page"""
        event.accept() 