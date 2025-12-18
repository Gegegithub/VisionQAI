"""
Application Flask pour la détection de défauts de câbles
"""
from flask import Flask, render_template, request, jsonify, url_for
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import config
from model.cable_analyzer import CableAnalyzer

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = config.RESULTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Initialiser l'analyseur de câbles
analyzer = None

# Base de données simple (fichier JSON) pour stocker les résultats
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'analyses.json')

def load_data():
    """Charge les données d'analyse depuis le fichier JSON"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:  # Fichier vide
                    return {'analyses': []}
                return json.loads(content)
        except json.JSONDecodeError:
            print(f"[WARN] Fichier JSON corrompu, réinitialisation...")
            return {'analyses': []}
    return {'analyses': []}

def save_data(data):
    """Sauvegarde les données d'analyse dans le fichier JSON"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS




@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Page du dashboard"""
    return render_template('dashboard.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Endpoint pour uploader et analyser une image"""
    global analyzer

    # Vérifier si un fichier a été envoyé
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400

    file = request.files['file']

    # Vérifier si un fichier a été sélectionné
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400

    # Vérifier l'extension du fichier
    if not allowed_file(file.filename):
        return jsonify({'error': 'Type de fichier non autorisé. Utilisez PNG, JPG ou JPEG'}), 400

    try:
        # Sauvegarder le fichier uploadé
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Initialiser l'analyseur si nécessaire
        if analyzer is None:
            analyzer = CableAnalyzer()

        # Analyser l'image
        results = analyzer.analyze_image(filepath)

        # Sauvegarder l'image de résultat
        result_filename = f"result_{filename}"
        result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
        analyzer.save_results(results, result_path)

        # Charger les données existantes
        data = load_data()

        # Générer un ID unique
        cable_id = f"CABLE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(data['analyses']) + 1}"

        # Ajouter cette analyse aux données
        analysis_record = {
            'id': cable_id,
            'filename': filename,
            'longueur_pixels': round(results['longueur_pixels'], 2),
            'longueur_cm': round(results['longueur_cm'], 2),
            'statut': results['statut'],
            'timestamp': datetime.now().isoformat(),
            'result_image': f'results/{result_filename}'
        }
        data['analyses'].append(analysis_record)

        # Sauvegarder les données
        save_data(data)

        # Préparer la réponse
        response = {
            'success': True,
            'id': cable_id,
            'longueur_pixels': round(results['longueur_pixels'], 2),
            'longueur_cm': round(results['longueur_cm'], 2),
            'statut': results['statut'],
            'original_image': url_for('static', filename=f'uploads/{filename}'),
            'result_image': url_for('static', filename=f'results/{result_filename}')
        }

        return jsonify(response)

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'analyse: {str(e)}'}), 500


@app.route('/dashboard/stats')
def dashboard_stats():
    """Endpoint pour obtenir les statistiques du dashboard avec analyse des machines responsables"""
    data = load_data()
    analyses = data['analyses']

    total = len(analyses)
    defectueux = [a for a in analyses if a['statut'] == 'DÉFECTUEUX']
    ok = [a for a in analyses if a['statut'] == 'OK']

    nb_defectueux = len(defectueux)
    nb_ok = len(ok)

    pct_defectueux = (nb_defectueux / total * 100) if total > 0 else 0
    pct_ok = (nb_ok / total * 100) if total > 0 else 0

    return jsonify({
        'total': total,
        'nb_defectueux': nb_defectueux,
        'nb_ok': nb_ok,
        'pct_defectueux': round(pct_defectueux, 1),
        'pct_ok': round(pct_ok, 1),
        'defectueux': [{'id': a['id'], 'longueur_cm': a['longueur_cm'], 'timestamp': a['timestamp'], 'statut': a['statut'], 'result_image': a.get('result_image', '')} for a in defectueux],
        'ok': [{'id': a['id'], 'longueur_cm': a['longueur_cm'], 'timestamp': a['timestamp'], 'statut': a['statut'], 'result_image': a.get('result_image', '')} for a in ok]
    })


@app.route('/health')
def health():
    """Endpoint de santé pour vérifier que l'application fonctionne"""
    return jsonify({'status': 'OK', 'model_loaded': analyzer is not None})


if __name__ == '__main__':
    # Vérifier que le modèle existe
    if not os.path.exists(config.MODEL_PATH):
        print(f"ATTENTION: Le modèle n'a pas été trouvé à {config.MODEL_PATH}")
        print("Veuillez placer votre fichier best.pt dans le dossier 'models/'")
    else:
        print(f"Modèle trouvé: {config.MODEL_PATH}")

    print(f"Dossier uploads: {config.UPLOAD_FOLDER}")
    print(f"Dossier résultats: {config.RESULTS_FOLDER}")

    app.run(debug=True, host='0.0.0.0', port=5000)
