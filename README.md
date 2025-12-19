# Détection de Défauts de Câbles

#Aperçu
<img width="1919" height="1079" alt="Image" src="https://github.com/user-attachments/assets/4220da4a-0aaf-4be0-84ff-3e324843e880" />

<img width="1919" height="1079" alt="Image" src="https://github.com/user-attachments/assets/f2f78ef7-cf9c-4f92-8aae-be296bbaa4c6" />

<img width="1919" height="1079" alt="Image" src="https://github.com/user-attachments/assets/ffe69572-eea3-414b-99f9-c49c8eadce1a" />

<img width="1919" height="1079" alt="Image" src="https://github.com/user-attachments/assets/b816cbc4-7f2c-4b28-afd0-d00ddee6081c" />

<img width="1919" height="1079" alt="Image" src="https://github.com/user-attachments/assets/f435ea0a-b996-4e3d-a393-76223716e420" />

Application web de détection automatique de défauts de longueur des câbles électriques en utilisant YOLOv8 et Flask.

## Description

Ce projet permet d'analyser des images de câbles pour détecter les défauts de longueur. Le système utilise un modèle YOLOv8 pour segmenter le câble, calcule sa longueur et détermine s'il est conforme ou défectueux selon des critères définis.

## Fonctionnalités

- Upload d'images ou de dossiers d'images
- Détection et segmentation automatique avec YOLOv8
- Calcul de longueur du câble en centimètres
- Classification OK/DÉFECTUEUX selon les seuils configurés
- Dashboard avec statistiques et graphiques
- Historique des analyses
- Export des rapports en PDF
- Slideshow pour naviguer entre les résultats

## Configuration

Les paramètres de calibration et les seuils de qualité sont définis dans `config.py` :

- `LONGUEUR_MIN_OK` : Longueur minimale acceptable (cm)
- `LONGUEUR_MAX_OK` : Longueur maximale acceptable (cm)
- `LONGUEUR_OBJET_REEL_CM` : Calibration pour conversion pixels/cm

## Structure

```
projet ie/
├── app.py                      # Application Flask
├── config.py                   # Configuration
├── model/cable_analyzer.py     # Logique d'analyse
├── utils/image_processing.py   # Traitement d'image
├── templates/index.html        # Interface web
├── data/analyses.json          # Historique des analyses
└── models/best.pt             # Modèle YOLOv8
```

