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

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Session management

mail = Mail(app)

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

# Welcome page after successful registration or login  
# @app.route('/welcome')
# def welcome():
#     if 'username' in session:
#         return f'Welcome to Splitwise, {session["username"]}!'  
#     return redirect(url_for('home'))
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

    

@app.route('/index')
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
    init_db()  # Initialize the database
    app.run(debug=True,host='0.0.0.0',port=8097)  # Run in debug mode for better error visibility
from flask import Flask, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with an actual secret key

@app.route('/logout')
def logout():
    # Logic for logging the user out
    session.clear()  # Clears session data, logging out the user
    return render_template('home.html')  # Redirect to homepage or login page

@app.route("/addExpense",methods=["POST"])   
def addExpense():  
    data = request.form
    total = data['total']
    creatorId = data['currentUserId']  
    partnerId = data['pid']
    partnerExpense= data['partnerExpense']
    creatorExpense = data['creatorExpense']
    expenseName = data['expenseName']


    query =  f''' insert into expense(expensename,creatorid,partnerid,total,creatoramount,partneramount)
                   values('{expenseName}',{creatorId},{partnerId},{total},{creatorExpense},{partnerExpense}) '''
    
    InsertAsync(query)

    print(data)

    return redirect(url_for("history",curId=creatorId))  

@app.route("/history")
def history():
    data =request.args['curId']
    
    query = f'''select expensename,creatoramount,partneramount ,total,
(select name from users where id=creatorid) as creatorname,
(select name from users where id= partnerid) as friendname from expense e where creatorid={data} or partnerid={data}'''

    data = QueryAsync(query)
    print(data)
    return render_template('history.html',userData=data)


if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True,host='0.0.0.0',port=8097)  # Run in debug mode for better error visibility
