# 🔌 Détection de Défauts de Câbles

Application Flask pour détecter et analyser les défauts dans les câbles en utilisant YOLOv8 pour la segmentation et des algorithmes de traitement d'image.

## 📋 Fonctionnalités

- Upload d'images de câbles via interface web
- Détection automatique avec YOLOv8
- Segmentation et génération de masques
- Squelettisation pour mesure précise
- Calcul de longueur en pixels et en centimètres
- Classification automatique (OK / DÉFECTUEUX)
- Visualisation avec masque et squelette superposés

## 🚀 Installation

### 1. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
```

Activer l'environnement :
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Placer le modèle YOLO

Créer un dossier `models/` et y placer votre fichier `best.pt` :

```bash
mkdir models
# Copier votre best.pt dans models/
```

## ⚙️ Configuration

Modifier les paramètres dans [config.py](config.py) :

```python
# Calibration (à ajuster selon vos images)
LONGUEUR_OBJET_REEL_CM = 10   # Longueur réelle de référence en cm
LONGUEUR_OBJET_PIXELS = 200   # Longueur de référence en pixels

# Critères de qualité
LONGUEUR_MIN_OK = 22  # Longueur minimale acceptable en cm
LONGUEUR_MAX_OK = 60  # Longueur maximale acceptable en cm
```

## 🏃 Lancement

```bash
python app.py
```

L'application sera accessible sur : http://localhost:5000

## 📁 Structure du Projet

```
projet_detection_cables/
├── app.py                    # Application Flask principale
├── config.py                 # Configuration
├── requirements.txt          # Dépendances Python
├── model/
│   ├── __init__.py
│   └── cable_analyzer.py    # Analyseur de câbles
├── utils/
│   ├── __init__.py
│   └── image_processing.py  # Traitement d'image
├── static/
│   ├── uploads/             # Images uploadées
│   └── results/             # Résultats générés
├── templates/
│   └── index.html           # Interface utilisateur
└── models/
    └── best.pt              # Modèle YOLO
```

## 🔧 Utilisation

1. Ouvrir l'application dans le navigateur
2. Cliquer ou glisser-déposer une image de câble
3. Cliquer sur "Lancer l'analyse"
4. Voir les résultats :
   - Longueur en pixels et en centimètres
   - Statut (OK / DÉFECTUEUX)
   - Visualisation avec masque et squelette

## 📊 Pipeline d'Analyse

1. **Détection** : YOLOv8 détecte et segmente le câble
2. **Nettoyage** : Morphologie mathématique pour nettoyer le masque
3. **Squelettisation** : Extraction du squelette central
4. **Graphe** : Conversion en graphe NetworkX
5. **Mesure** : Calcul du chemin le plus long
6. **Conversion** : Pixels → Centimètres via calibration
7. **Classification** : Comparaison aux seuils de qualité

## 🎨 Visualisation

L'image de sortie contient :
- **Masque bleu** : Zone détectée du câble
- **Squelette rouge** : Ligne centrale pour la mesure
- **Texte** : Longueur et statut en overlay

## ⚠️ Notes Importantes

- Assurez-vous que votre modèle `best.pt` est bien un modèle de segmentation YOLOv8
- Ajustez les paramètres de calibration selon votre setup
- Les seuils de qualité peuvent être modifiés dans [config.py](config.py)

## 🐛 Dépannage

**Erreur "Aucun câble détecté"** :
- Vérifier que l'image contient bien un câble
- Vérifier que le modèle est correctement entraîné

**Mesures incorrectes** :
- Ajuster les paramètres de calibration dans [config.py](config.py)

**Erreur de chargement du modèle** :
- Vérifier que `best.pt` est dans le dossier `models/`
- Vérifier que c'est bien un modèle YOLOv8 de segmentation
