import os
import logging
import datetime
import calendar
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QComboBox, QGroupBox, QMessageBox, QFrame, QSizePolicy,
                             QGridLayout, QDateEdit)
from PyQt5.QtGui import QFont, QIcon, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QDate, QRect, QSize

# Importer les modules database et utils
from database.db_manager import db_manager

# Configuration du logger
logging.basicConfig(filename='dashboard.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class PieChartWidget(QWidget):
    """Widget pour afficher un diagramme circulaire"""
    
    def __init__(self, data=None, labels=None, colors=None, title=""):
        """
        Initialiser le widget de diagramme circulaire
        
        Args:
            data (list): Liste des valeurs à afficher
            labels (list): Liste des étiquettes correspondant aux valeurs
            colors (list): Liste des couleurs pour chaque segment
            title (str): Titre du diagramme
        """
        super().__init__()
        
        self.data = data or []
        self.labels = labels or []
        self.colors = colors or []
        self.title = title
        
        # Si les couleurs ne sont pas fournies, en générer
        if not self.colors and self.data:
            self.colors = self._generate_colors(len(self.data))
        
        # Configuration du widget
        self.setMinimumSize(200, 200)
    
    def _generate_colors(self, count):
        """Générer des couleurs pour le diagramme"""
        colors = []
        hue_step = 360 / count
        
        for i in range(count):
            hue = i * hue_step
            colors.append(QColor.fromHsv(int(hue), 200, 230))
        
        return colors
    
    def set_data(self, data, labels=None, colors=None):
        """
        Définir les données du diagramme
        
        Args:
            data (list): Liste des valeurs à afficher
            labels (list): Liste des étiquettes correspondant aux valeurs
            colors (list): Liste des couleurs pour chaque segment
        """
        self.data = data
        
        if labels:
            self.labels = labels
        
        if colors:
            self.colors = colors
        elif data:
            self.colors = self._generate_colors(len(data))
        
        # Forcer un nouveau rendu
        self.update()
    
    def paintEvent(self, event):
        """Dessiner le diagramme circulaire"""
        if not self.data:
            return
        
        # Calculer la somme des données
        total = sum(self.data)
        if total == 0:
            return
        
        # Calculer les pourcentages et les angles
        percentages = [value / total * 100 for value in self.data]
        angles = [int(value / total * 360 * 16) for value in self.data]  # *16 car QPainter utilise des 1/16 de degré
        
        # Initialiser le peintre
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Définir la police
        font = QFont("Arial", 9)
        painter.setFont(font)
        
        # Calculer le rectangle pour le diagramme
        width = self.width()
        height = self.height()
        size = min(width, height) - 20
        rect = QRect((width - size) // 2, (height - size) // 2, size, size)
        
        # Dessiner le titre
        if self.title:
            title_font = QFont("Arial", 12, QFont.Bold)
            painter.setFont(title_font)
            painter.drawText(0, 10, width, 20, Qt.AlignCenter, self.title)
            painter.setFont(font)
        
        # Dessiner le diagramme
        start_angle = 0
        
        for i, angle in enumerate(angles):
            # Dessiner le segment
            painter.setPen(QPen(Qt.black, 1))
            painter.setBrush(QBrush(self.colors[i]))
            painter.drawPie(rect, int(start_angle), int(angle))
            
            # Calculer la position du texte
            mid_angle = start_angle + angle / 2
            mid_angle_rad = mid_angle * np.pi / (180 * 16)
            radius = size / 2 * 0.7
            
            x = int(rect.center().x() + radius * np.cos(mid_angle_rad))
            y = int(rect.center().y() - radius * np.sin(mid_angle_rad))
            
            # Dessiner l'étiquette
            if len(self.labels) > i:
                label_text = f"{self.labels[i]}: {percentages[i]:.1f}%"
                painter.setPen(Qt.black)
                painter.drawText(x - 40, y - 10, 80, 20, Qt.AlignCenter, label_text)
            
            start_angle += angle
        
        painter.end()

class BarChartWidget(QWidget):
    """Widget pour afficher un diagramme à barres"""
    
    def __init__(self, data=None, labels=None, colors=None, title=""):
        """
        Initialiser le widget de diagramme à barres
        
        Args:
            data (list): Liste des valeurs à afficher
            labels (list): Liste des étiquettes correspondant aux valeurs
            colors (list): Liste des couleurs pour chaque barre
            title (str): Titre du diagramme
        """
        super().__init__()
        
        self.data = data or []
        self.labels = labels or []
        self.colors = colors or []
        self.title = title
        
        # Si les couleurs ne sont pas fournies, en générer
        if not self.colors and self.data:
            self.colors = [QColor(0, 120, 215) for _ in range(len(self.data))]
        
        # Configuration du widget
        self.setMinimumSize(200, 200)
    
    def set_data(self, data, labels=None, colors=None):
        """
        Définir les données du diagramme
        
        Args:
            data (list): Liste des valeurs à afficher
            labels (list): Liste des étiquettes correspondant aux valeurs
            colors (list): Liste des couleurs pour chaque barre
        """
        self.data = data
        
        if labels:
            self.labels = labels
        
        if colors:
            self.colors = colors
        elif data:
            self.colors = [QColor(0, 120, 215) for _ in range(len(data))]
        
        # Forcer un nouveau rendu
        self.update()
    
    def paintEvent(self, event):
        """Dessiner le diagramme à barres"""
        if not self.data:
            return
        
        # Initialiser le peintre
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Définir la police
        font = QFont("Arial", 9)
        painter.setFont(font)
        
        # Calculer les dimensions du diagramme
        width = self.width()
        height = self.height()
        
        # Dessiner le titre
        if self.title:
            title_font = QFont("Arial", 12, QFont.Bold)
            painter.setFont(title_font)
            painter.drawText(0, 10, width, 20, Qt.AlignCenter, self.title)
            painter.setFont(font)
        
        # Calculer les dimensions de l'axe X et Y
        padding = 40
        chart_width = width - 2 * padding
        chart_height = height - 2 * padding - 20  # -20 pour le titre
        
        # Dessiner l'axe X et Y
        painter.setPen(QPen(Qt.black, 1))
        painter.drawLine(padding, height - padding, padding, padding + 20)  # Axe Y
        painter.drawLine(padding, height - padding, width - padding, height - padding)  # Axe X
        
        # Trouver la valeur maximale
        max_value = max(self.data) if self.data else 0
        if max_value == 0:
            max_value = 1  # Éviter la division par zéro
        
        # Dessiner les barres
        bar_count = len(self.data)
        if bar_count == 0:
            return
        
        bar_width = chart_width / bar_count
        
        for i, value in enumerate(self.data):
            bar_height = value / max_value * chart_height
            
            # Dessiner la barre
            painter.setPen(QPen(Qt.black, 1))
            
            # Utiliser la couleur définie ou une couleur par défaut
            if i < len(self.colors):
                painter.setBrush(QBrush(self.colors[i]))
            else:
                painter.setBrush(QBrush(QColor(0, 120, 215)))
            
            bar_x = padding + i * bar_width + bar_width * 0.1
            bar_y = height - padding - bar_height
            
            painter.drawRect(int(bar_x), int(bar_y), int(bar_width * 0.8), int(bar_height))
            
            # Dessiner la valeur au-dessus de la barre
            painter.setPen(Qt.black)
            painter.drawText(int(bar_x), int(bar_y - 15), int(bar_width * 0.8), 15, 
                             Qt.AlignCenter, str(value))
            
            # Dessiner l'étiquette sous la barre
            if i < len(self.labels):
                label_rect = QRect(int(bar_x), int(height - padding + 5), int(bar_width * 0.8), 20)
                painter.drawText(label_rect, Qt.AlignCenter, self.labels[i])
        
        painter.end()

class DashboardPage(QWidget):
    """Page du tableau de bord"""
    
    def __init__(self):
        """Initialiser la page du tableau de bord"""
        super().__init__()
        
        # Initialiser l'interface utilisateur
        self.init_ui()
        
        # Charger les données
        self.load_dashboard_data()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        # Créer le layout principal
        main_layout = QVBoxLayout()
        
        # Titre de la page
        title_label = QLabel("Tableau de bord")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Créer la section des filtres
        filters_group = self.create_filters_section()
        main_layout.addWidget(filters_group)
        
        # Créer la section des statistiques
        stats_layout = self.create_stats_section()
        main_layout.addLayout(stats_layout)
        
        # Définir le layout pour ce widget
        self.setLayout(main_layout)
    
    def create_filters_section(self):
        """Créer la section des filtres"""
        filters_group = QGroupBox("Filtres")
        filters_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                margin-top: 35px;
                padding-top: 45px;
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
                min-width: 120px;
            }
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: white;
                margin: 5px;
            }
        """)
        
        filters_layout = QHBoxLayout()
        
        # Sélection du mois
        month_label = QLabel("Mois:")
        self.month_combo = QComboBox()
        
        # Ajouter les mois
        for i in range(1, 13):
            month_name = calendar.month_name[i]
            self.month_combo.addItem(month_name, i)
        
        # Définir le mois actuel
        current_month = datetime.datetime.now().month
        self.month_combo.setCurrentIndex(current_month - 1)
        
        # Sélection de l'année
        year_label = QLabel("Année:")
        self.year_combo = QComboBox()
        
        # Ajouter les années (de l'année actuelle - 5 à l'année actuelle)
        current_year = datetime.datetime.now().year
        for year in range(current_year - 5, current_year + 1):
            self.year_combo.addItem(str(year), year)
        
        # Définir l'année actuelle
        self.year_combo.setCurrentIndex(5)  # Dernier élément (année actuelle)
        
        # Bouton d'application des filtres
        self.apply_filters_btn = QPushButton("Appliquer")
        self.apply_filters_btn.clicked.connect(self.load_dashboard_data)
        
        # Ajouter les widgets au layout
        filters_layout.addWidget(month_label)
        filters_layout.addWidget(self.month_combo)
        filters_layout.addWidget(year_label)
        filters_layout.addWidget(self.year_combo)
        filters_layout.addWidget(self.apply_filters_btn)
        
        # Définir le layout pour le groupe des filtres
        filters_group.setLayout(filters_layout)
        
        return filters_group
    
    def create_stats_section(self):
        """Créer la section des statistiques"""
        stats_layout = QGridLayout()
        
        # Créer les widgets de statistiques
        self.create_stat_widget(stats_layout, 0, 0, "Employés enregistrés", "0")
        self.create_stat_widget(stats_layout, 0, 1, "Présences ce mois", "0")
        self.create_stat_widget(stats_layout, 0, 2, "Taux de présence", "0%")
        
        return stats_layout
    
    def create_stat_widget(self, layout, row, col, title, value):
        """Créer un widget de statistique"""
        # Créer le cadre
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("""
            background-color: #454e67;
            border-radius: 8px;
            padding: 10px;
        """)
        frame.setMinimumSize(150, 100)
        
        # Créer le layout
        frame_layout = QVBoxLayout()
        
        # Titre
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 15px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(title_label)
        
        # Valeur
        attr_name = f"{title.lower().replace(' ', '_')}_label"
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        setattr(self, attr_name, value_label)  # Stocker la référence pour la mise à jour
        frame_layout.addWidget(value_label)
        
        # Définir le layout pour le cadre
        frame.setLayout(frame_layout)
        
        # Ajouter le cadre au layout
        layout.addWidget(frame, row, col)
    
    def load_dashboard_data(self):
        """Charger les données du tableau de bord"""
        try:
            # Récupérer le mois et l'année sélectionnés
            month = self.month_combo.currentData()
            year = self.year_combo.currentData()
            
            # Calculer le premier et le dernier jour du mois
            first_day = f"{year}-{month:02d}-01"
            _, last_day_num = calendar.monthrange(year, month)
            last_day = f"{year}-{month:02d}-{last_day_num}"
            
            # Récupérer les données de la base de données
            
            # 1. Nombre d'employés enregistrés
            employees = db_manager.get_all_employees()
            total_employees = len(employees)
            
            # 2. Présences ce mois
            attendances = db_manager.get_attendance(first_day)
            total_attendances = len(attendances)
            
            # 3. Taux de présence (présences / (employés * jours ouvrés))
            # Supposons 22 jours ouvrés par mois en moyenne
            working_days = 22
            if total_employees > 0:
                attendance_rate = (total_attendances / (total_employees * working_days)) * 100
            else:
                attendance_rate = 0
            
            # Mettre à jour les statistiques
            self.employés_enregistrés_label.setText(str(total_employees))
            self.présences_ce_mois_label.setText(str(total_attendances))
            self.taux_de_présence_label.setText(f"{attendance_rate:.2f}%")
            
            # Journal
            logging.info(f"Données du tableau de bord chargées pour {calendar.month_name[month]} {year}")
        
        except Exception as e:
            # Afficher un message d'erreur
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des données: {e}")
            logging.error(f"Erreur lors du chargement des données du tableau de bord: {e}")
    
    def closeEvent(self, event):
        """Gérer l'événement de fermeture de la page"""
        event.accept() 