from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Function to create or update the database and tables if they don't exist
def init_db():
    with sqlite3.connect('friends.db') as conn:
        cursor = conn.cursor()
        
        # Create the friends table if it does not exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS friends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                phone TEXT,
                email TEXT
            )
        ''')
        
        # Add columns phone and email to the friends table if they do not exist
        try:
            cursor.execute('ALTER TABLE friends ADD COLUMN phone TEXT;')
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute('ALTER TABLE friends ADD COLUMN email TEXT;')
        except sqlite3.OperationalError:
            pass

        # Create the groups table if it does not exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')

        # Drop the group_members table if it exists and recreate it
        cursor.execute('DROP TABLE IF EXISTS group_members')
        cursor.execute('''
            CREATE TABLE group_members (
                group_name TEXT,
                member_name TEXT,
                PRIMARY KEY (group_name, member_name)
            )
        ''')

# Initialize the database
init_db()

@app.route('/')
def home():
    with sqlite3.connect('friends.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM friends')
        friends = cursor.fetchall()

        cursor.execute('''
            SELECT group_name, member_name 
            FROM group_members
        ''')
        groups = {}
        for group_name, member_name in cursor.fetchall():
            if group_name not in groups:
                groups[group_name] = []
            if member_name:
                groups[group_name].append(member_name)
    
    return render_template('index.html', friends=friends, groups=groups)

@app.route('/add_friend', methods=['POST'])
def add_friend():
    friend_name = request.form.get('friend_name')
    phone = request.form.get('phone') or None
    email = request.form.get('email') or None
    if friend_name:
        with sqlite3.connect('friends.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO friends (name, phone, email) VALUES (?, ?, ?)',
                    (friend_name, phone, email)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                cursor.execute(
                    'UPDATE friends SET phone = ?, email = ? WHERE name = ?',
                    (phone, email, friend_name)
                )
                conn.commit()
    return redirect(url_for('home'))

@app.route('/add_to_group', methods=['POST'])
def add_to_group():
    group_name = request.form.get('group_name')
    member_name = request.form.get('friend_to_add')

    if group_name and member_name:
        with sqlite3.connect('friends.db') as conn:
            cursor = conn.cursor()
            
            # Insert the group and member relationship
            try:
                cursor.execute(
                    'INSERT INTO group_members (group_name, member_name) VALUES (?, ?)',
                    (group_name, member_name)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                pass  # The member is already in the group, ignore the error
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
