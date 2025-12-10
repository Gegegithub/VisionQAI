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

        # Debug: Afficher les informations sur la détection
        print(f"[DEBUG] Nombre de résultats: {len(results)}")
        print(f"[DEBUG] Masques disponibles: {results[0].masks}")
        if results[0].masks is not None:
            print(f"[DEBUG] Nombre de masques: {len(results[0].masks.data)}")

        # Vérifier s'il y a des masques détectés
        if results[0].masks is None or len(results[0].masks.data) == 0:
            raise ValueError("Aucun câble détecté dans l'image. Le modèle a détecté des objets mais sans masques de segmentation. Assurez-vous d'utiliser un modèle YOLOv8-seg (segmentation).")

        # Récupérer le premier masque (câble principal)
        print("[DEBUG] Récupération du masque...")
        mask = results[0].masks.data[0].cpu().numpy()
        print(f"[DEBUG] Forme du masque: {mask.shape}")
        mask = (mask > 0.5).astype(np.uint8) * 255

        # Convertir en format booléen pour le traitement
        mask_bool = mask > 0
        print(f"[DEBUG] Pixels positifs dans le masque: {np.sum(mask_bool)}")

        # Pipeline de traitement
        print("[DEBUG] Prétraitement du masque...")
        mask_clean = preprocess_mask(mask_bool)
        print(f"[DEBUG] Pixels après nettoyage: {np.sum(mask_clean)}")

        print("[DEBUG] Squelettisation...")
        skeleton = skeletonize_mask(mask_clean)
        print(f"[DEBUG] Pixels dans le squelette: {np.sum(skeleton)}")

        # Calculer la longueur
        print("[DEBUG] Construction du graphe...")
        G, coords = skeleton_graph(skeleton)
        print(f"[DEBUG] Nombre de nœuds dans le graphe: {G.number_of_nodes()}")

        print("[DEBUG] Calcul de la longueur...")
        longueur_pixels = longest_path_length(G)
        print(f"[DEBUG] Longueur en pixels: {longueur_pixels}")
        longueur_cm = pixels_to_cm(
            longueur_pixels,
            self.longueur_objet_reel_cm,
            self.longueur_objet_pixels
        )

        # Déterminer le statut
        print(f"[DEBUG] Détermination du statut... longueur_cm={longueur_cm}")
        if self.longueur_min_ok <= longueur_cm <= self.longueur_max_ok:
            statut = "OK"
        else:
            statut = "DÉFECTUEUX"
        print(f"[DEBUG] Statut: {statut}")

        # Créer la visualisation
        print("[DEBUG] Création de la visualisation...")
        print(f"[DEBUG] Forme image originale: {original_img.shape}")
        print(f"[DEBUG] Forme mask_clean: {mask_clean.shape}")
        print(f"[DEBUG] Forme skeleton: {skeleton.shape}")

        try:
            visualization = create_visualization(
                original_img,
                mask_clean,
                skeleton,
                longueur_cm,
                statut
            )
            print("[DEBUG] Visualisation créée avec succès")
        except Exception as e:
            print(f"[ERROR] Erreur lors de la création de la visualisation: {e}")
            raise

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
