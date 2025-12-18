"""
Configuration pour l'application de détection de défauts de câbles
"""
import os

# Chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'best.pt')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
RESULTS_FOLDER = os.path.join(BASE_DIR, 'static', 'results')

# Créer les dossiers s'ils n'existent pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Paramètres de calibration (à ajuster selon vos images)
LONGUEUR_OBJET_REEL_CM = 10  # Longueur réelle de l'objet de référence en cm
LONGUEUR_OBJET_PIXELS = 200  # Longueur de l'objet de référence en pixels

# Critères de qualité
LONGUEUR_MIN_OK = 20  # cm
LONGUEUR_MAX_OK = 40  # cm

# Extensions de fichiers autorisées
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Configuration Flask
SECRET_KEY = ''
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
