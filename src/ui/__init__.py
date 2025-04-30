"""
Module d'interface utilisateur pour l'application de reconnaissance faciale
"""

from .main_window import FaceRecognizerApp
from .registration_page import RegistrationPage
from .recognition_page import RecognitionPage
from .attendance_page import AttendancePage
from .dashboard_page import DashboardPage

__all__ = [
    'FaceRecognizerApp',
    'RegistrationPage',
    'RecognitionPage',
    'AttendancePage',
    'DashboardPage'
] 