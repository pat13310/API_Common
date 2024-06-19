from flask import Flask, request, jsonify, make_response, Blueprint
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import timedelta

from common.doi import DOIManager
from common.mail import send_mail
from common.simplify import summarization, simplification

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret')  # Set this securely!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-jwt-secret')  # Set this securely too!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=90)  # pour 3 mois de validité
app.config['MAIL_SERVER'] = 'node109-eu.n0c.com'  # Replace with your mail server
app.config['MAIL_PORT'] = 465  # Replace with your mail server port
app.config['MAIL_USE_TLS'] = False  # Use TLS if supported by your server
app.config['MAIL_USE_SSL'] = True  # Use SSL if supported by your server
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'default-email@example.com')  # Replace with your email
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'Garcia66240!')  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'admin@xendev.fr'  # Replace with your email

mail = Mail(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


# Modèle de la base de données pour les DOI
class DOI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doi = db.Column(db.String(50), unique=True, nullable=False)
    titre = db.Column(db.String(200), nullable=False)
    auteur = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)


# Initialiser la classe DOIManager avec la base de données et le modèle DOI
doi_manager = DOIManager(db, DOI)

# Créer les tables dans la base de données
with app.app_context():
    db.create_all()

# Définir un Blueprint pour regrouper les routes sous /common/api/v1/
api_blueprint = Blueprint('api', __name__, url_prefix='/common/api/v1')


# Routes pour les utilisateurs
@api_blueprint.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    try:
        send_mail(new_user.username, 'Bienvenue!',
                  'Bienvenue et nous vous remercions de votre inscription à nos services.', app.config)
    except Exception as e:
        return str(e), 500

    return jsonify({'message': 'Utilisateur enregistré avec succès!'}), 201


@api_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    access_token = create_access_token(identity={'username': user.username})
    return jsonify({'token': access_token})


# Routes protégées pour l'envoi d'e-mails
@api_blueprint.route('/send-mail', methods=['POST'])
@jwt_required()
def send_email():
    data = request.get_json()
    to = data.get('recipient')
    subject = data.get('subject')
    body = data.get('body')

    if not to or not subject or not body:
        return jsonify({"message": "Recipient, sujet et corps du message sont obligatoires."}), 400

    return send_mail(to, subject, body, app.config)


@api_blueprint.route('/test-email', methods=['GET'])
@jwt_required()
def test_mail():
    return send_mail('patgarcia66240@gmail.com', 'Test API_Common',
                     'Ce mail est envoyé à partir du serveur API_Common.', app.config)


# Routes pour les DOI
@api_blueprint.route('/doi', methods=['POST'])
@jwt_required()
def create_doi():
    donnees = request.get_json()
    prefixe = donnees.get('prefixe', 'doi')
    titre = donnees['titre']
    auteur = donnees['auteur']
    date = donnees['date']
    type_objet = donnees['type']

    doi = doi_manager.enregistrer_doi(prefixe, titre, auteur, date, type_objet)
    return jsonify({'doi': doi}), 201


@api_blueprint.route('/doi/get/<doi>', methods=['GET'])
@jwt_required()
def get_doi(doi):
    informations = doi_manager.resoudre_doi(doi)
    if informations:
        return jsonify(informations)
    else:
        return jsonify({'message': 'DOI non trouvé'}), 404


@api_blueprint.route('/summarize', methods=['POST'])
@jwt_required()
def summarize():
    donnees = request.get_json()
    text = donnees['text']
    resume = summarization(text)
    if resume:
        return jsonify({"resume": resume.strip()}), 200
    else:
        return jsonify({'message': 'Résumé non trouvé'}), 404


@api_blueprint.route('/simplify', methods=['POST'])
@jwt_required()
def simplify():
    donnees = request.get_json()
    text = donnees['text']
    resume = simplification(text)
    resume=resume.replace(' .', '.')
    if resume:
        return jsonify({"simplify": resume.strip()}), 200
    else:
        return jsonify({'message': 'Texte simplifié non trouvé'}), 404


# Enregistrer le Blueprint dans l'application Flask
app.register_blueprint(api_blueprint)

# Démarrer l'application Flask
if __name__ == '__main__':
    app.run(debug=True)
