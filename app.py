from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///splitwise_account.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the User Profile model
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Define the Contact Us model
class ContactUs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Home route (User Profile)
@app.route('/')
def profile():
    user = UserProfile.query.first()
    return render_template('profile.html', user=user)

# Update User Profile (Edit Name)
@app.route('/updateProfile', methods=['POST'])
def update_profile():
    name = request.form['name']
    user = UserProfile.query.first()

    if user:
        user.name = name
    else:
        user = UserProfile(name=name)
        db.session.add(user)
    
    db.session.commit()
    return redirect(url_for('profile'))

# Contact Us route
@app.route('/contactUs', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        message = request.form['message']

        contact = ContactUs(fullname=fullname, email=email, message=message)
        db.session.add(contact)
        db.session.commit()

        return redirect(url_for('profile'))
    return render_template('contact_us.html')

# Run the app
if __name__ == '__main__':
    db.create_all()  # Create database tables
    app.run(debug=True)
