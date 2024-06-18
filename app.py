import smtplib
import ssl
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, make_response
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret')  # Set this securely!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-jwt-secret')  # Set this securely too!

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


# Create the database tables
with app.app_context():
    db.create_all()


def send_mail(to, subject, body):
    sender_email = app.config['MAIL_DEFAULT_SENDER']
    password = app.config['MAIL_PASSWORD']
    host_server = app.config['MAIL_SERVER']
    port = app.config['MAIL_PORT']

    # Créer le message MIME
    message = MIMEMultipart()
    # message.set_charset("utf-8")
    message["From"] = sender_email
    message["To"] = to
    message["Subject"] = subject

    # Ajouter le corps du message avec encodage UTF-8
    message.attach(MIMEText(body, "plain", "utf-8"))
    context = ssl.create_default_context()

    try:
        # Envoyer l'email
        with smtplib.SMTP_SSL(host_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, to, message.as_string().encode('UTF-8'))

        return jsonify({"message": "E-mail envoyé avec succès."}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Register endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    try:
        send_mail(new_user.username, 'Bienvenue!',
                  'Bienvenue et nous vous remercions de votre inscription à nos services.')
    except Exception as e:
        return str(e), 500

    return jsonify({'message': 'Utilisateur  enregsitré avec succès!'}), 201


# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    access_token = create_access_token(identity={'username': user.username})
    return jsonify({'token': access_token})


# Protected route example
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route('/test-email', methods=['GET'])
@jwt_required()
def test_mail():
    current_user = get_jwt_identity()  # Get the identity of the current user from the JWT token
    return send_mail('patgarcia66240@gmail.com', 'Test API_Common',
                     'Ce mail est envoyé à partir du serveur API_Common.')


@app.route('/send-mail', methods=['POST'])
@jwt_required()
def send_email():
    current_user = get_jwt_identity()  # Get the identity of the current user from the JWT token
    data = request.get_json()
    to = data.get('recipient')
    subject = data.get('subject')
    body = data.get('body')

    if not to or not subject or not body:
        return jsonify({"message": "Recipient, sujet et corps du message sont obligatoires."}), 400

    return send_mail(to, subject, body)


if __name__ == '__main__':
    app.run(debug=True)
