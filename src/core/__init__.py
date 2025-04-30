"""
Module core pour l'application de reconnaissance faciale
"""

from .face_detector import face_detector
from .dataset_creator import dataset_creator, DatasetCreatorThread
from .classifier import face_classifier, ClassifierTrainerThread

__all__ = [
    'face_detector',
    'dataset_creator',
    'DatasetCreatorThread',
    'face_classifier',
    'ClassifierTrainerThread'
] 