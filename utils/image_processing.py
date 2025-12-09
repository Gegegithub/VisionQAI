"""
Fonctions de traitement d'image pour l'analyse de câbles
"""
import numpy as np
import cv2
from skimage import morphology
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
import networkx as nx
import math


def preprocess_mask(mask):
    """
    Nettoyage du masque : fermeture, suppression petits objets, remplissage des trous

    Args:
        mask: Image binaire du masque

    Returns:
        Masque nettoyé (booléen)
    """
    mask = mask > 0
    mask = morphology.binary_closing(mask, morphology.disk(2))
    mask = morphology.remove_small_objects(mask, min_size=50)
    mask = ndi.binary_fill_holes(mask)
    return mask.astype(bool)


def skeletonize_mask(mask):
    """
    Squelettisation du masque

    Args:
        mask: Masque binaire

    Returns:
        Squelette du masque
    """
    return skeletonize(mask)


def skeleton_graph(skel):
    """
    Convertit le squelette en graphe NetworkX pour calculer la longueur

    Args:
        skel: Squelette binaire

    Returns:
        Tuple (graphe, coordonnées)
    """
    coords = np.argwhere(skel)
    idx_map = {(int(y), int(x)): i for i, (y, x) in enumerate(coords)}
    G = nx.Graph()

    for (y, x), i in idx_map.items():
        G.add_node(i, pos=(y, x))
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue
                ny, nx_ = y + dy, x + dx
                if (ny, nx_) in idx_map:
                    j = idx_map[(ny, nx_)]
                    dist = math.hypot(dy, dx)
                    G.add_edge(i, j, weight=dist)

    return G, coords


def find_endpoints(G):
    """
    Trouve les points terminaux (degré = 1) du graphe

    Args:
        G: Graphe NetworkX

    Returns:
        Liste des nœuds terminaux
    """
    return [n for n, d in G.degree() if d == 1]


def longest_path_length(G):
    """
    Calcule la longueur du chemin le plus long dans le graphe

    Args:
        G: Graphe NetworkX

    Returns:
        Longueur maximale en pixels
    """
    endpoints = find_endpoints(G)
    if not endpoints:
        return sum(d['weight'] for u, v, d in G.edges(data=True)) / 2

    maxlen = 0.0
    for i in range(len(endpoints)):
        lengths = nx.single_source_dijkstra_path_length(G, endpoints[i], weight='weight')
        for j in endpoints[i + 1:]:
            if j in lengths and lengths[j] > maxlen:
                maxlen = lengths[j]

    return maxlen


def pixels_to_cm(longueur_pixels, longueur_objet_reel_cm, longueur_objet_pixels):
    """
    Convertit des pixels en cm en utilisant un objet de référence

    Args:
        longueur_pixels: Longueur mesurée en pixels
        longueur_objet_reel_cm: Longueur réelle de l'objet de référence en cm
        longueur_objet_pixels: Longueur de l'objet de référence en pixels

    Returns:
        Longueur en centimètres
    """
    pixel_size_cm = longueur_objet_reel_cm / longueur_objet_pixels
    return longueur_pixels * pixel_size_cm


def create_visualization(original_img, mask, skeleton, longueur_cm, statut):
    """
    Crée une visualisation combinant l'image originale, le masque et le squelette

    Args:
        original_img: Image originale (BGR)
        mask: Masque binaire
        skeleton: Squelette binaire
        longueur_cm: Longueur calculée en cm
        statut: "OK" ou "DÉFECTUEUX"

    Returns:
        Image de visualisation
    """
    # Convertir l'image en RGB pour l'affichage
    img_rgb = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)

    # Créer une copie pour la superposition
    overlay = img_rgb.copy()

    # Redimensionner le masque et le squelette si nécessaire
    if mask.shape[:2] != img_rgb.shape[:2]:
        mask = cv2.resize(mask.astype(np.uint8),
                         (img_rgb.shape[1], img_rgb.shape[0]),
                         interpolation=cv2.INTER_NEAREST).astype(bool)
        skeleton = cv2.resize(skeleton.astype(np.uint8),
                             (img_rgb.shape[1], img_rgb.shape[0]),
                             interpolation=cv2.INTER_NEAREST).astype(bool)

    # Appliquer le masque en semi-transparent (bleu)
    overlay[mask] = overlay[mask] * 0.5 + np.array([0, 150, 255]) * 0.5

    # Appliquer le squelette en rouge vif
    overlay[skeleton] = [255, 0, 0]

    # Ajouter le texte avec les informations
    couleur = (0, 255, 0) if statut == "OK" else (255, 0, 0)
    cv2.putText(overlay, f"Longueur: {longueur_cm:.2f} cm",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, couleur, 2)
    cv2.putText(overlay, f"Statut: {statut}",
                (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, couleur, 2)

    # Convertir de RGB à BGR pour OpenCV
    result = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)

    return result
