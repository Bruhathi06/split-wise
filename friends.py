from flask import Flask, render_template, request, redirect, url_for
import sqlite3

# Create Flask app instance
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

        # Create the groups table if it does not exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')

        # Drop and recreate the group_members table
        cursor.execute('DROP TABLE IF EXISTS group_members')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_members (
                group_name TEXT,
                member_name TEXT,
                PRIMARY KEY (group_name, member_name)
            )
        ''')

# Initialize the database
init_db()

# Define the home route
@app.route('/')
def home():
    return render_template('home.html')

# Route to show friends
@app.route('/friends')
def friends():
    with sqlite3.connect('friends.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM friends')
        friends = cursor.fetchall()
    return render_template('friends.html', friends=friends)

# Route to show groups
@app.route('/groups')
def groups():
    with sqlite3.connect('friends.db') as conn:
        cursor = conn.cursor()
        
        # Fetch all groups
        cursor.execute('SELECT * FROM groups')
        group_list = cursor.fetchall()

        # Fetch all group members
        cursor.execute('SELECT group_name, member_name FROM group_members')
        group_members = cursor.fetchall()

        # Fetch SQLite sequence data (for auto-increment tracking)
        cursor.execute('SELECT * FROM sqlite_sequence')
        sequence_data = cursor.fetchall()

        # Organize group members by group name
        groups = {}
        for group_name, member_name in group_members:
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(member_name)

    # Pass groups and sequence data to the template
    return render_template('groups.html', groups=groups, sequence_data=sequence_data)

# Route to show account details
@app.route('/account')
def account():
    return render_template('account.html')

# Route to show activities
@app.route('/activity')
def activity():
    return render_template('activity.html')

# Route to add friends and groups
@app.route('/add')
def add():
    return render_template('add.html')

# Route to handle adding a friend
@app.route('/add_friend', methods=['POST'])
def add_friend():
    friend_name = request.form.get('friend_name')
    phone = request.form.get('phone') or None
    email = request.form.get('email') or None
    if friend_name:
        with sqlite3.connect('friends.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO friends (name, phone, email) VALUES (?, ?, ?)', 
                               (friend_name, phone, email))
                conn.commit()
            except sqlite3.IntegrityError:
                cursor.execute('UPDATE friends SET phone = ?, email = ? WHERE name = ?', 
                               (phone, email, friend_name))
                conn.commit()
    return redirect(url_for('friends'))

# Route to handle adding a member to a group
@app.route('/add_to_group', methods=['POST'])
def add_to_group():
    group_name = request.form.get('group_name')
    member_name = request.form.get('friend_to_add')

    if group_name and member_name:
        with sqlite3.connect('friends.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO group_members (group_name, member_name) VALUES (?, ?)', 
                               (group_name, member_name))
                conn.commit()
            except sqlite3.IntegrityError:
                pass  # Ignore if the member is already in the group
    return redirect(url_for('groups'))

# Ensure the application runs only when the script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
