import os
import csv
import logging
import datetime
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

# Configuration du logger
logging.basicConfig(filename='export.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class DataExporter:
    def __init__(self, parent=None):
        """
        Initialiser l'exportateur de données
        
        Args:
            parent (QWidget): Widget parent pour les boîtes de dialogue
        """
        self.parent = parent
        
        # Créer le répertoire d'exportation s'il n'existe pas
        os.makedirs(os.path.join('data', 'attendance'), exist_ok=True)
    
    def export_to_csv(self, data, filename=None):
        """
        Exporter les données de présence au format CSV
        
        Args:
            data (list): Liste des enregistrements de présence
            filename (str, optional): Nom du fichier CSV
            
        Returns:
            bool: True si l'exportation a réussi, False sinon
        """
        try:
            if not filename:
                # Générer un nom de fichier par défaut
                date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join('data', 'attendance', f'attendance_{date_str}.csv')
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Définir les en-têtes
                fieldnames = ['ID', 'Nom', 'Prénom', 'Matricule', 'Poste', 'Date', 'Heure d\'arrivée', 'Statut']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Écrire les en-têtes
                writer.writeheader()
                
                # Écrire les données
                for record in data:
                    writer.writerow({
                        'ID': record['employee_id'],
                        'Nom': record['nom'],
                        'Prénom': record['prenom'],
                        'Matricule': record['matricule'],
                        'Poste': record['poste'],
                        'Date': record['date'],
                        'Heure d\'arrivée': record['heure_arrivee'],
                        'Statut': record['statut']
                    })
            
            logging.info(f"Données exportées avec succès au format CSV: {filename}")
            return True
        
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation au format CSV: {e}")
            if self.parent:
                QMessageBox.critical(self.parent, "Erreur", f"Erreur lors de l'exportation au format CSV: {e}")
            return False
    
    def export_to_excel(self, data, filename=None):
        """
        Exporter les données de présence au format Excel
        
        Args:
            data (list): Liste des enregistrements de présence
            filename (str, optional): Nom du fichier Excel
            
        Returns:
            bool: True si l'exportation a réussi, False sinon
        """
        try:
            if not filename:
                # Générer un nom de fichier par défaut
                date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join('data', 'attendance', f'attendance_{date_str}.xlsx')
            
            # Créer un nouveau classeur
            wb = Workbook()
            ws = wb.active
            ws.title = "Présences"
            
            # Définir les en-têtes
            headers = ['ID', 'Nom', 'Prénom', 'Matricule', 'Poste', 'Date', 'Heure d\'arrivée', 'Statut']
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num)
                cell.value = header
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center')
                cell.fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
            
            # Écrire les données
            for row_num, record in enumerate(data, 2):
                ws.cell(row=row_num, column=1).value = record['employee_id']
                ws.cell(row=row_num, column=2).value = record['nom']
                ws.cell(row=row_num, column=3).value = record['prenom']
                ws.cell(row=row_num, column=4).value = record['matricule']
                ws.cell(row=row_num, column=5).value = record['poste']
                ws.cell(row=row_num, column=6).value = record['date']
                ws.cell(row=row_num, column=7).value = record['heure_arrivee']
                ws.cell(row=row_num, column=8).value = record['statut']
            
            # Ajuster la largeur des colonnes
            for col_num in range(1, 9):
                column_letter = get_column_letter(col_num)
                ws.column_dimensions[column_letter].width = 15
            
            # Enregistrer le classeur
            wb.save(filename)
            
            logging.info(f"Données exportées avec succès au format Excel: {filename}")
            return True
        
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation au format Excel: {e}")
            if self.parent:
                QMessageBox.critical(self.parent, "Erreur", f"Erreur lors de l'exportation au format Excel: {e}")
            return False
    
    def export_to_word(self, data, filename=None, title="Rapport de présence"):
        """
        Exporter les données de présence au format Word
        
        Args:
            data (list): Liste des enregistrements de présence
            filename (str, optional): Nom du fichier Word
            title (str, optional): Titre du rapport
            
        Returns:
            bool: True si l'exportation a réussi, False sinon
        """
        try:
            if not filename:
                # Générer un nom de fichier par défaut
                date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join('data', 'attendance', f'attendance_{date_str}.docx')
            
            # Créer un nouveau document
            doc = Document()
            
            # Ajouter un titre
            doc_title = doc.add_heading(title, level=1)
            doc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Ajouter la date du rapport
            date_paragraph = doc.add_paragraph(f"Date du rapport: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
            date_paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
            # Ajouter un tableau
            table = doc.add_table(rows=1, cols=8)
            table.style = 'Table Grid'
            
            # Définir les en-têtes
            header_cells = table.rows[0].cells
            header_cells[0].text = 'ID'
            header_cells[1].text = 'Nom'
            header_cells[2].text = 'Prénom'
            header_cells[3].text = 'Matricule'
            header_cells[4].text = 'Poste'
            header_cells[5].text = 'Date'
            header_cells[6].text = 'Heure d\'arrivée'
            header_cells[7].text = 'Statut'
            
            # Mettre en forme les en-têtes
            for cell in header_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
            
            # Ajouter les données
            for record in data:
                row_cells = table.add_row().cells
                row_cells[0].text = str(record['employee_id'])
                row_cells[1].text = record['nom']
                row_cells[2].text = record['prenom']
                row_cells[3].text = record['matricule']
                row_cells[4].text = record['poste']
                row_cells[5].text = record['date']
                row_cells[6].text = record['heure_arrivee']
                row_cells[7].text = record['statut']
            
            # Enregistrer le document
            doc.save(filename)
            
            logging.info(f"Données exportées avec succès au format Word: {filename}")
            return True
        
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation au format Word: {e}")
            if self.parent:
                QMessageBox.critical(self.parent, "Erreur", f"Erreur lors de l'exportation au format Word: {e}")
            return False
    
    def export_to_pdf(self, data, filename=None):
        """
        Exporter les données de présence au format PDF
        
        Args:
            data (list): Liste des enregistrements de présence
            filename (str, optional): Nom du fichier PDF
            
        Returns:
            bool: True si l'exportation a réussi, False sinon
        """
        try:
            if not filename:
                # Générer un nom de fichier par défaut
                date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join('data', 'attendance', f'attendance_{date_str}.pdf')
            
            # Créer un DataFrame pandas
            df = pd.DataFrame([{
                'ID': record['employee_id'],
                'Nom': record['nom'],
                'Prénom': record['prenom'],
                'Matricule': record['matricule'],
                'Poste': record['poste'],
                'Date': record['date'],
                'Heure d\'arrivée': record['heure_arrivee'],
                'Statut': record['statut']
            } for record in data])
            
            # Convertir le DataFrame en HTML et ajouter des styles CSS
            html = df.to_html(index=False)
            css = '''
            <style>
                table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin-bottom: 20px; 
                }
                th { 
                    background-color: #4CAF50; 
                    color: white; 
                    text-align: left;
                    padding: 8px;
                }
                td { 
                    padding: 8px; 
                    border-bottom: 1px solid #ddd; 
                }
                tr:nth-child(even) { 
                    background-color: #f2f2f2; 
                }
                h1 { 
                    text-align: center; 
                    color: #333; 
                }
                .report-date { 
                    text-align: right; 
                    margin-bottom: 20px; 
                }
            </style>
            '''
            
            # Ajouter un titre et la date du rapport
            title = f"<h1>Rapport de présence</h1>"
            date_str = f"<p class='report-date'>Date du rapport: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</p>"
            
            # Combiner le HTML
            full_html = f"<html><head>{css}</head><body>{title}{date_str}{html}</body></html>"
            
            # Générer le PDF à partir du HTML
            # On utilise la méthode to_pdf de pandas avec pdfkit
            # Vous devez installer wkhtmltopdf séparément
            import pdfkit
            pdfkit.from_string(full_html, filename)
            
            logging.info(f"Données exportées avec succès au format PDF: {filename}")
            return True
        
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation au format PDF: {e}")
            if self.parent:
                QMessageBox.critical(self.parent, "Erreur", f"Erreur lors de l'exportation au format PDF: {e}")
            return False
    
    def show_export_dialog(self, data, parent=None):
        """
        Afficher une boîte de dialogue pour exporter les données
        
        Args:
            data (list): Liste des enregistrements de présence
            parent (QWidget): Widget parent pour les boîtes de dialogue
            
        Returns:
            bool: True si l'exportation a réussi, False sinon
        """
        if not data:
            if parent:
                QMessageBox.warning(parent, "Avertissement", "Aucune donnée à exporter.")
            return False
        
        if not parent:
            parent = self.parent
        
        # Demander à l'utilisateur le format d'exportation
        options = ["CSV", "Excel", "Word", "PDF"]
        selected, ok = QMessageBox.question(parent, "Exportation", "Choisir le format d'exportation:",
                                            *options, QMessageBox.Cancel)
        
        if not ok or selected == QMessageBox.Cancel:
            return False
        
        # Demander à l'utilisateur l'emplacement du fichier
        default_dir = os.path.join(os.getcwd(), 'data', 'attendance')
        date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if selected == 0:  # CSV
            filename, _ = QFileDialog.getSaveFileName(parent, "Exporter au format CSV",
                                                     f"{default_dir}/attendance_{date_str}.csv",
                                                     "Fichiers CSV (*.csv)")
            if filename:
                return self.export_to_csv(data, filename)
        
        elif selected == 1:  # Excel
            filename, _ = QFileDialog.getSaveFileName(parent, "Exporter au format Excel",
                                                     f"{default_dir}/attendance_{date_str}.xlsx",
                                                     "Fichiers Excel (*.xlsx)")
            if filename:
                return self.export_to_excel(data, filename)
        
        elif selected == 2:  # Word
            filename, _ = QFileDialog.getSaveFileName(parent, "Exporter au format Word",
                                                     f"{default_dir}/attendance_{date_str}.docx",
                                                     "Fichiers Word (*.docx)")
            if filename:
                return self.export_to_word(data, filename)
        
        elif selected == 3:  # PDF
            filename, _ = QFileDialog.getSaveFileName(parent, "Exporter au format PDF",
                                                     f"{default_dir}/attendance_{date_str}.pdf",
                                                     "Fichiers PDF (*.pdf)")
            if filename:
                return self.export_to_pdf(data, filename)
        
        return False

# Instance globale de l'exportateur de données
data_exporter = DataExporter() 