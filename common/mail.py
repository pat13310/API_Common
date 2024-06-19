import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import jsonify

import app


def send_mail(to, subject, body, config):
    sender_email = config['MAIL_DEFAULT_SENDER']
    password = config['MAIL_PASSWORD']
    host_server = config['MAIL_SERVER']
    port = config['MAIL_PORT']

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
