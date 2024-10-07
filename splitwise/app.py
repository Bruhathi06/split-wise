from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Session management

# Database path
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
            return 'Invalid email or password'

    return render_template('login.html')

# Welcome page after successful registration or login
@app.route('/welcome')
def welcome():
    if 'username' in session:
        return f'Welcome to Splitwise, {session["username"]}!'
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)  # Run in debug mode for better error visibility
