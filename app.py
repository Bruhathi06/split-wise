from flask import Flask, render_template, request, jsonify, url_for
import qrcode
import smtplib
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Set upload folder for profile pictures
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_qr')
def generate_qr():
    # Simulate user account URL
    account_url = "http://www.google.com"
    img = qrcode.make(account_url)
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'qr_code.png')
    img.save(img_path)
    
    return jsonify({'qr_code': url_for('static', filename='uploads/qr_code.png')})

@app.route('/contact_us', methods=['POST'])
def contact_us():
    name = request.form.get('contactName')
    email = request.form.get('email')
    message = request.form.get('message')
    
    # Sending email logic
    send_email(name, email, message)
    
    return jsonify({"status": "success"})

def send_email(name, email, message):
    msg = MIMEText(f"Message from {name} ({email}):\n\n{message}")
    msg['Subject'] = 'Contact Us Message'
    msg['From'] = 'yourapp@example.com'
    msg['To'] = 'developer@example.com'

    # Send the email via your SMTP server
    s = smtplib.SMTP('smtp.example.com')
    s.login('yourapp@example.com', 'yourpassword')
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()

@app.route('/update_profile', methods=['POST'])
def update_profile():
    name = request.form.get('name')
    profile_picture = request.files['profilePicture']
    
    if profile_picture:
        filename = secure_filename(profile_picture.filename)
        profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Save user name and profile picture to the database (placeholder)
    
    return jsonify({"status": "profile updated"})

if __name__ == '__main__':
    app.run(debug=True)