from flask import Flask, render_template, request,jsonify, redirect, url_for, session,flash,render_template_string
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import os
from Services import GenerateResetLink       
from datetime import datetime
reset_tokens = {}

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'splitwise.db')

def QueryAsync(query):
    conn = sqlite3.connect(db_path) 
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data

def InsertAsync(query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    #data = cursor.fetchall()
    conn.close()
    return []

class RealDictCursor(sqlite3.Cursor):
    def fetchone(self):
        row = super().fetchone()  
        if row is None:
            return None
        return {col[0]: row[idx] for idx, col in enumerate(self.description)}

    def fetchall(self):
        rows = super().fetchall()
        return [{col[0]: row[idx] for idx, col in enumerate(self.description)} for row in rows]



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
    # Create Groups table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups_table (
            group_name TEXT PRIMARY KEY NOT NULL UNIQUE
        )
    ''')

    # Create Members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            FOREIGN KEY (group_name) REFERENCES groups_table(group_name)
        )
    ''')

     # Create group_expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL,
            category TEXT NOT NULL,
            total_amount REAL NOT NULL,
            payer TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (group_name) REFERENCES groups_table(group_name),
            FOREIGN KEY (payer) REFERENCES users(name)
        )
    ''')

    # Create expense_details table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expense_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_id INTEGER NOT NULL,
            member_name TEXT NOT NULL,
            amount_owed REAL NOT NULL,
            FOREIGN KEY (expense_id) REFERENCES group_expenses(id),
            FOREIGN KEY (member_name) REFERENCES members(name)
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
            return redirect(url_for('splitwise_home'))

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
        cursor.execute('SELECT name,id FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()  
        print(user)
        conn.close()

        # if user:
        #     session['username'] = user[0]
        #     return redirect(url_for('welcome'))
        # else:
        #     flash("Invalid email or password")
        #     redirect(url_for('login'))
        #     #return 'Invalid email or password'
        if user:
            session['username'] = user[0]   
            print(user[0]) # Save the user's name in the session
            return redirect(url_for('splitwise_home',username= user[0],id=user[1]))  # Redirect to splitwise home page 
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for('login'))  # Don't forget the return statement


    return render_template('login.html')


# @app.route('/home/<username>')     
# def splitwise_home(username):
#     current_id = request.args.get('id')  
#     print("Session data:", session) 
#     if 'username' in session:  # Check if the user is logged in
#         print("Redirecting to home for user:",username) 
#         return render_template('splitwise_home.html',username=username,ids=current_id)   # Render the main Splitwise page
#     else:
#         return redirect(url_for('login'))  # Redirect to login if not logged in
@app.route('/home/<username>')     
def splitwise_home(username):
    print(request.args)
    if 'username' in session:  # Check if the user is logged in
        print("the user name in home is :",username) 
        return render_template('splitwise_home.html',username=username,ids=request.args['id'])   # Render the main Splitwise page
    else:
        return redirect(url_for('login'))  # Redirect to login if not logged in


@app.route('/process')
def process():
    current_user_id = request.args.get('currentUserId')
    currentUserName = request.args.get('currentUserName')
    user_id = request.args.get('id')
    user_email = request.args.get('email')
    targetUsername = request.args.get('username')

    query = f"insert into FriendsList (sourceid,receiverid) values({current_user_id},{user_id})  "
    data = InsertAsync(query)
    return redirect(url_for('friendsOptions',username= currentUserName,current_user_id=current_user_id))  

    
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
            users[email]['password'] = new_password  # Update password (replace with hashed password)
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

@app.route("/friendsOptions/<username>")  
def friendsOptions(username):
    curId= request.args['curId']
    print(curId)
    return render_template("friends.html",username=username,curId=curId)     
 
@app.route("/addFriend/<username>")
def addFriend(username):

    currentUserIdQuery = f"select id from users where name like '%{username}%' "
    currentUser = QueryAsync(currentUserIdQuery)
    if len(currentUser)>0:
        currentUserId = currentUser[0][0]  

    query = f"select id,email,name,phone from users u where u.id not in (select sourceid from FriendsList) and u.id not in (select receiverid from FriendsList)"
    data = QueryAsync(query)  
    usersData =[]

    for i in data:
        temp =[]
        for j in i:
            temp.append(j)
        usersData.append(temp)
    return render_template("expense.html",username=username,currentUserId=currentUserId,usersData= usersData)    

    

#friends page routing

@app.route("/addExpense",methods=["POST"])   
def addExpense():  
    data = request.form
    total = data['total']
    creatorId = data['currentUserId']  
    partnerId = data['pid']
    partnerExpense= data['partnerExpense']
    creatorExpense = data['creatorExpense']
    expenseName = data['expenseName']
    date = data['date']

    query =  f''' insert into expense(expensename,creatorid,partnerid,total,creatoramount,partneramount,createdon)
                   values('{expenseName}',{creatorId},{partnerId},{total},{creatorExpense},{partnerExpense},'{date}') '''
    
    InsertAsync(query)

    print(data)

    return redirect(url_for("history",curId=creatorId))  

@app.route("/history")
def history():
    # # Get 'curId' from the request arguments or default to the user ID in session
    # curUser = request.args.get('curId') or session.get('id')

    # # Check if curUser is still missing, and redirect if necessary
    # if not curUser:
    #     flash("User ID is missing. Please log in again.")
    #     return redirect(url_for('login'))

    # # Query to fetch the history based on curUser
    # query = f'''
    #     SELECT expensename, creatoramount, partneramount, total,
    #     (SELECT name FROM users WHERE id = creatorid) AS creatorname,
    #     (SELECT name FROM users WHERE id = partnerid) AS friendname,
    #     creatorid, partnerid 
    #     FROM expense e 
    #     WHERE creatorid = {curUser} OR partnerid = {curUser}
    # '''

    # data = QueryAsync(query)
    # return render_template('history.html', userData=data, currentUser=int(curUser))  
    curUser =request.args['curId']
    
    query = f'''select expensename,creatoramount,partneramount ,total,
(select name from users where id=creatorid) as creatorname,
(select name from users where id= partnerid) as friendname,creatorid,partnerid,createdon from expense e where creatorid={curUser} or partnerid={curUser}'''

    data = QueryAsync(query)
    print(data)
    return render_template('history.html',userData=data,currentUser=int(curUser))

# Groups functionalities
@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        group_name = request.form['group_name']
        member_names = request.form.getlist('member_name')
        phones = request.form.getlist('phone')
        emails = request.form.getlist('email')

        # Automatically add logged-in user to group
        logged_in_user = session['username']
        member_names.insert(0, logged_in_user)
        phones.insert(0, request.form.get('logged_in_user_phone', ''))  # Placeholder for logged-in user's phone
        emails.insert(0, request.form.get('logged_in_user_email', ''))  # Placeholder for logged-in user's email

        if len(member_names) < 3:
            flash('A group must have at least 3 members.', 'danger')
            return redirect(url_for('create_group'))

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO groups_table (group_name) VALUES (?)', (group_name,))
            for name, phone, email in zip(member_names, phones, emails):
                cursor.execute('INSERT INTO members (group_name, name, phone, email) VALUES (?, ?, ?, ?)', (group_name, name, phone, email))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Group name already exists. Please choose a different name."
        finally:
            conn.close()

        return redirect(url_for('view_groups'))

    return render_template('create_group.html')

@app.route('/view_groups')
def view_groups():
    if 'username' not in session:
        return redirect(url_for('login'))

    logged_in_user = session['username']
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT group_name FROM members WHERE name = ?', (logged_in_user,))
    groups = cursor.fetchall()
    group_data = []
    for group in groups:
        cursor.execute('SELECT name, phone, email FROM members WHERE group_name = ?', (group[0],))
        members = cursor.fetchall()
        group_data.append({'group_name': group[0], 'members': members})
    conn.close()
    return render_template('view_groups.html', groups=group_data)

@app.route('/split_expense', methods=['GET', 'POST'])
def split_expense():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        group_name = request.form.get('group_name')
        category = request.form.get('category')
        total_amount = request.form.get('total_amount')
        date = request.form.get('date')
        payer = session['username']  # Automatically set the payer to the logged-in user

        if not group_name or not category or not total_amount or not date:
            flash("Please fill in all fields", "danger")
            return redirect(url_for('split_expense'))

        try:
            total_amount = float(total_amount)
        except ValueError:
            flash("Total amount must be a valid number", "danger")
            return redirect(url_for('split_expense'))

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all the members of the selected group
        cursor.execute('SELECT name FROM members WHERE group_name = ?', (group_name,))
        members = [member[0] for member in cursor.fetchall()]

        if not members:
            conn.close()
            flash("No members found in the selected group. Please add members before splitting expenses.", "danger")
            return redirect(url_for('split_expense'))
        
        # Calculate how much each member owes the payer
        members_owe = [member for member in members if member != payer]
        if len(members_owe) == 0:
            conn.close()
            flash("No members to split the expense with.", "danger")
            return redirect(url_for('split_expense'))

        # Calculate split amounts
        split_amount = total_amount / len(members)
        split_amounts = {member: split_amount for member in members}
        split_amounts[payer] = 0 

        # Insert the expense into the group_expenses table
        cursor.execute('INSERT INTO group_expenses (group_name, category, total_amount, payer, date) VALUES (?, ?, ?, ?, ?)',
                       (group_name, category, total_amount, payer, date))
        expense_id = cursor.lastrowid

        # Insert each member's owed amount into the expense_details table
        for member, amount in split_amounts.items():
            cursor.execute('INSERT INTO expense_details (expense_id, member_name, amount_owed) VALUES (?, ?, ?)',
                           (expense_id, member, amount))
            
        conn.commit()
        conn.close()

        # Pass the calculated split_amounts and other details to the result template
        return redirect(url_for('group_history', group_name=group_name))

    # Handling GET request to show available groups
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT group_name FROM groups_table')
    groups = cursor.fetchall()
    conn.close()

    # Render template with groups available
    return render_template('split_expense.html', groups=groups)

@app.route('/group_history')
def group_history():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ge.group_name, ge.category, ge.total_amount, ge.payer, ge.date, ed.member_name, ed.amount_owed
        FROM group_expenses ge
        JOIN expense_details ed ON ge.id = ed.expense_id
    ''')
    history = cursor.fetchall()
    conn.close()

    return render_template('group_history.html', history=history)

#account page 
@app.route('/index')
def index():
    return render_template('index.html')


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
# Add this route to your existing Flask code above
@app.route('/activity', methods=['GET'])
def get_activity():
    user_id = request.args.get('user_id')
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return "Invalid user ID", 400

    # Debug output to verify the user_id
    print("User ID for activity:", user_id)

    query = f'''
        SELECT expensename AS transaction_name, total AS amount_spent, creatoramount AS bills_paid, 
               partneramount AS bills_owed, date('now') AS transaction_date,
               CASE WHEN expensename LIKE '%food%' THEN 'Food Bill'
                    WHEN expensename LIKE '%electricity%' THEN 'Electricity Bill'
                    WHEN expensename LIKE '%groceries%' THEN 'Groceries Bill'
                    WHEN expensename LIKE '%bus%' OR expensename LIKE '%train%' THEN 'Transportation'
                    ELSE 'Other' END AS category
        FROM expense
        WHERE creatorid = {user_id} OR partnerid = {user_id}
    '''

    # Retrieve and process the data
    transactions = QueryAsync(query)
    print("Transactions fetched:", transactions)  # Debug output

    response = [
        {
            "transaction_name": row[0],
            "transaction_date": row[4],
            "amount_spent": row[1],
            "bills_paid": row[2],
            "bills_owed": row[3],
            "category": row[5]
        }
        for row in transactions
    ]
    print("Processed response:", response)  # Debug output for processed data
    return render_template('activity.html', transactions=response)

def create_expense_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expense (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expensename TEXT NOT NULL,
            total REAL NOT NULL,
            creatoramount REAL NOT NULL,
            partneramount REAL NOT NULL,
            creatorid INTEGER NOT NULL,
            partnerid INTEGER NOT NULL,
            FOREIGN KEY (creatorid) REFERENCES users(id),
            FOREIGN KEY (partnerid) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/view_history/<int:transaction_id>')
def view_history(transaction_id):
    # Query details of the specific transaction by ID
    query = f'''
        SELECT e.expensename AS transaction_name, e.total AS amount_spent, e.creatoramount AS bills_paid,
               e.partneramount AS bills_owed, e.creatorid, e.partnerid
        FROM expense e
        WHERE e.id = {transaction_id}
    '''
    transaction = QueryAsync(query)

    if not transaction:
        flash("Transaction not found.")
        return redirect(url_for('activity'))

    return render_template('view_history.html', transaction=transaction[0])

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True,host='0.0.0.0',port=8097)  # Run in debug mode for better error visibility
