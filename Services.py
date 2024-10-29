
import secrets
from datetime import datetime, timedelta
from flask_mail import Mail, Message
import socket

def GenerateResetLink(email,reset_tokens):
    hostname =  socket.gethostname()
    hostIp = socket.gethostbyname(hostname)
    print(hostIp)
    token = secrets.token_urlsafe()
    expiration = datetime.utcnow() + timedelta(minutes=5) 
    reset_tokens[token] = (email, expiration)
    return f"http://{hostIp}:8097/reset_password/{token}?email={email}"


