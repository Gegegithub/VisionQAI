"""
Analyseur de câbles utilisant YOLO pour la détection et la segmentation
"""
import cv2
import numpy as np
from ultralytics import YOLO
from utils.image_processing import (
    preprocess_mask,
    skeletonize_mask,
    skeleton_graph,
    longest_path_length,
    pixels_to_cm,
    create_visualization
)
import config


class CableAnalyzer:
    """Classe pour analyser les câbles et détecter les défauts"""

    def __init__(self, model_path=None):
        """
        Initialise l'analyseur avec le modèle YOLO

        Args:
            model_path: Chemin vers le modèle YOLO (si None, utilise config.MODEL_PATH)
        """
        if model_path is None:
            model_path = config.MODEL_PATH

        self.model = YOLO(model_path)
        self.longueur_objet_reel_cm = config.LONGUEUR_OBJET_REEL_CM
        self.longueur_objet_pixels = config.LONGUEUR_OBJET_PIXELS
        self.longueur_min_ok = config.LONGUEUR_MIN_OK
        self.longueur_max_ok = config.LONGUEUR_MAX_OK

    def analyze_image(self, image_path):
        """
        Analyse une image de câble et retourne les résultats

        Args:
            image_path: Chemin vers l'image à analyser

        Returns:
            Dictionnaire contenant les résultats de l'analyse:
            {
                'longueur_pixels': float,
                'longueur_cm': float,
                'statut': str ('OK' ou 'DÉFECTUEUX'),
                'mask': np.array,
                'skeleton': np.array,
                'visualization': np.array
            }
        """
        # Charger l'image originale
        original_img = cv2.imread(image_path)

        # Effectuer la prédiction avec YOLO
        results = self.model(image_path)

        # Vérifier s'il y a des masques détectés
        if results[0].masks is None or len(results[0].masks.data) == 0:
            raise ValueError("Aucun câble détecté dans l'image")

        # Récupérer le premier masque (câble principal)
        mask = results[0].masks.data[0].cpu().numpy()
        mask = (mask > 0.5).astype(np.uint8) * 255

        # Convertir en format booléen pour le traitement
        mask_bool = mask > 0

        # Pipeline de traitement
        mask_clean = preprocess_mask(mask_bool)
        skeleton = skeletonize_mask(mask_clean)

        # Calculer la longueur
        G, coords = skeleton_graph(skeleton)
        longueur_pixels = longest_path_length(G)
        longueur_cm = pixels_to_cm(
            longueur_pixels,
            self.longueur_objet_reel_cm,
            self.longueur_objet_pixels
        )

        # Déterminer le statut
        if self.longueur_min_ok <= longueur_cm <= self.longueur_max_ok:
            statut = "OK"
        else:
            statut = "DÉFECTUEUX"

        # Créer la visualisation
        visualization = create_visualization(
            original_img,
            mask_clean,
            skeleton,
            longueur_cm,
            statut
        )

        return {
            'longueur_pixels': longueur_pixels,
            'longueur_cm': longueur_cm,
            'statut': statut,
            'mask': mask_clean,
            'skeleton': skeleton,
            'visualization': visualization
        }

    def save_results(self, results, output_path):
        """
        Sauvegarde l'image de visualisation

        Args:
            results: Dictionnaire de résultats depuis analyze_image()
            output_path: Chemin de sortie pour l'image de visualisation
        """
        cv2.imwrite(output_path, results['visualization'])
