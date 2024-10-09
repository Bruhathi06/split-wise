from flask import Flask, render_template, request, redirect, url_for, session,flash,render_template_string
import sqlite3
import os
from flask_mail import Mail, Message
import os
from Services import GenerateResetLink
from datetime import datetime
reset_tokens = {}

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Session management

mail = Mail(app)

def CheckUser(email):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM users WHERE email = '{email}' ")
    user = cursor.fetchone()
    conn.close()

    if user:
        
        return True
    else:
        return False 
    
def test(to,link):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # Gmail SMTP server configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    email_user='splitwiseteam@gmail.com'
    email_password='vgib xrhv cona zipq'
    # Email content
    to_email = to  # Replace with recipient's email
    subject = 'Test Email from Python'
    body = link

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(email_user, email_password)
            server.sendmail(email_user, to_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


def send_reset_email(to, link): 
    print("sent")
    msg = Message("Password Reset Request", recipients=[to])
    msg.body = f"To reset your password, click the following link: {link}"
    mail.send(msg)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'splitwise.db')

# Initialize database
def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table with email, password, name, and phone number
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']  
        name = request.form['name']
        phone = request.form['phone']

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (email, password, name, phone) VALUES (?, ?, ?, ?)', 
                           (email, password, name, phone))
            conn.commit()
            conn.close()

            session['username'] = name
            return redirect(url_for('welcome'))

        except sqlite3.IntegrityError:
            return 'Email already exists. Please use a different one.' 
        except Exception as e:
            return f'An error occurred: {e}'

    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = user[0]
            return redirect(url_for('welcome'))
        else:
            flash("Invalid email or password")
            redirect(url_for('login'))
            #return 'Invalid email or password'

    return render_template('login.html')

# Welcome page after successful registration or login  
@app.route('/welcome')
def welcome():
    if 'username' in session:
        return f'Welcome to Splitwise, {session["username"]}!'  
    return redirect(url_for('home'))


    
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password(): 
    if request.method == "GET":
        return  render_template_string('''
        <form method="post">
            Enter Email: <input type="email" name="email" required>
            <input type="submit" value="Submit">
        </form>
    ''')

    if request.method == 'POST':
        email = request.form['email']
        if CheckUser(email):
            reset_link = GenerateResetLink(email,reset_tokens)
            test(email,reset_link)
            return "A password reset link has been sent to your email."
            #send_reset_email(email, reset_link)
            #flash('A password reset link has been sent to your email.', 'success')
        else:
            flash('Email not found.', 'danger')
            return redirect(url_for('login'))
        return "User does not exists"
        

    return render_template('forgot_password.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email_info = reset_tokens.get(token)
    print(email_info)
    # Check if the token is valid and not expired
    if email_info:
        email, expiration = email_info
        print(email)
        if datetime.utcnow() > expiration:
            flash('The reset link has expired. Please request a new one.', 'danger')
            return redirect(url_for('forgot_password'))
        
        if request.method == 'POST':
            new_password = request.form['password']
            # Here, you should hash the new password before saving
            users_db[email]['password'] = new_password  # Update password (replace with hashed password)
            flash('Your password has been reset!', 'success')
            return redirect(url_for('forgot_password'))
        return  render_template("resetpassword.html",email=email) 
    return "Sorry the link has expired"


@app.route("/newPassword",methods=["GET","POST"])
def newPassword():

    if request.method == "GET":
        return render_template("resetpassword.html")  
     
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = f''' update users set password ='{password}' where email= '{email}' '''
        cursor.execute(query) 
        conn.commit()
        flash("Password updated succussfully")
        return redirect(url_for("login"))
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True,host='0.0.0.0',port=8097)  # Run in debug mode for better error visibility
