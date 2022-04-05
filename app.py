from flask import Flask, flash, render_template,redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from functools import wraps
from datetime import datetime
from flask_bcrypt import Bcrypt

#Create a flask instance:
app = Flask(__name__)

#Configuring ORM with MySQL database:
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://nmjtbdwjipsjlr:bcfb563ccfb4d20d80157ce1dce3cdc5f7fe32bc74342620f8e918c46440f864@ec2-18-214-134-226.compute-1.amazonaws.com:5432/d6r6aqci8gss8c"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#If enabled True, will track modification of object & required more memory.

#Providing a secret key to protect from hacking:
app.config['SECRET_KEY'] = 'my_secret_key'

#Initialising our database:
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

#Creating our model (table name= Users) in our db:
class Users(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String(length = 15), nullable = False, unique = True)
    email = db.Column(db.String(length = 30), nullable = False, unique = True)
    password_hash = db.Column(db.String(length = 60), nullable = False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    complaints = db.relationship('Complaints', backref='owned', lazy = True)
    

    #Create a string representation object & return it:
    def __repr__(self):
        return '<Username %r>' % self.username


#Creating our model (table name= Complaints) in our db:
class Complaints(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(length = 30), nullable = False)
    email = db.Column(db.String(length = 25), nullable = False)
    category = db.Column(db.String(length = 15), nullable = False)
    title = db.Column(db.String(length = 30), nullable = False)
    description = db.Column(db.String(length = 200), nullable = False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    owner = db.Column(db.Integer(), db.ForeignKey('users.id'))

    def __init__(self, name, email, title, category, description):
        self.name = name
        self.email = email
        self.category = category
        self.title = title
        self.description = description
 
    

#Creating a home route:
@app.route('/home')
def home_page():
    return render_template('home.html')


#Creating a admin route:
@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    if request.method == "POST":
        if request.form["password"] == 'password' and request.form["email"] == 'admin@gofynd.com':
            session['loggedin']=True
            session['email'] = "email"
            
            flash('You have been successfully logged in as Admin ✅', 'success')
            return redirect(url_for('complain_page'))

        else:
            flash('Unauthorised admin login, Please check! ❌', 'danger')

    return render_template('admin.html')


#Create a register route:
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == "POST":
        username=request.form["username"]
        email=request.form["email"]
        password=request.form["password_hash"]

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())  #Hashing password.

        user_create = Users(username=username, email=email, password_hash=hashed)
        db.session.add(user_create)
        db.session.commit()
        all_user = Users.query.all()
        
        flash('You have been successfully registered, Please login here! ✅', 'success')
        return render_template('login.html', all_user=all_user)


    return render_template('register.html')
            
#Create a login route:
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == "POST":
        session.pop('username', None)

        email = request.form["email"]
        password = request.form["password_hash"]

        loggedin = Users.query.filter_by(email=email).first()
        
        if loggedin.email == email and bcrypt.check_password_hash(Users.password_hash, password):
            session['loggedin']=True
            session['email'] = "email"

            user_data = Complaints.query.filter_by(email=email).all()
            flash('You have been logged in! ✅', 'success')
            return redirect(url_for('view_page'))
        
        else:
            flash('Invalid credentials, Please check! ❌', 'warning')
            return redirect(url_for('login_page'))

    return render_template('login.html')
            

#Checks If user has logged in:
def is_logged_in(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'loggedin' in session:
			return f(*args,**kwargs)
		else:
			flash('Unauthorized, Please Login ❌','danger')
			return redirect(url_for('login_page'))
	return wrap


#Creating an API for user logout:
@app.route('/logout')
@is_logged_in
def logout_page():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login_page'))


#Creating an API to view User dashboard:
@app.route("/view", methods=['GET', 'POST'])
def view_page():
    user_data = Complaints.query.filter_by(email=Users.email).all()

    return render_template('view.html', user_data = user_data)


#Create a admin API, query on all our complain data:
@app.route('/complain')
def complain_page():
    all_data = Complaints.query.all()
 
    return render_template("complain.html", complains = all_data)
 
  

#Creating an API to add a complain from user side:
@app.route('/add', methods = ['POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        category = request.form['category']
        title = request.form['title']
        description = request.form['description']
  
        my_complain = Complaints(name, email, category, title, description)
        db.session.add(my_complain)
        db.session.commit()
  
        flash("Your complaint has been added successfully")
        return redirect(url_for('view_page'))

  
#Creating an API to edit/update a complain from user side:
@app.route('/update', methods = ['GET', 'POST'])
def update():
    if request.method == 'POST':
        my_complain = Complaints.query.get(request.form.get('id'))
  
        my_complain.name = request.form['name']
        my_complain.email = request.form['email']
        my_complain.category = request.form['category']
        my_complain.title = request.form['title']
        my_complain.description = request.form['description']
  
        db.session.commit()
        flash("Your complaint has been updated successfully")
        return redirect(url_for('view_page'))
  

#Creating an API to delete a complain from user side:
@app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    my_complain = Complaints.query.get(id)
    db.session.delete(my_complain)
    db.session.commit()
    flash("Your complaint has been deleted successfully")
    return redirect(url_for('view_page'))


