from flask import Flask, render_template, url_for, redirect, flash, session
from flask_login import login_manager, login_user, login_required, LoginManager # sudo apt install python3-flask-login
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import PasswordField, StringField, validators
from os import urandom

app = Flask(__name__)
app.secret_key = urandom(32)
db = SQLAlchemy(app)

# https://flask-login.readthedocs.io/en/latest/#installation
login_manager = LoginManager()
login_manager.init_app(app)

class Book(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	description = db.Column(db.String(161), nullable=False)

BookForm = model_form(
	model=Book,
	db_session=db.session,
	base_class=FlaskForm)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, nullable=False, unique=True)
	email = db.Column(db.String, nullable=True, unique=True)
	passwordHash = db.Column(db.String, nullable=False)

	# https://realpython.com/using-flask-login-for-user-management-with-flask/#the-user-model
	# this has to be in the db for flask-login for some reason
	# i guess it beeds to be able to get the value somewhere
	# where the actual object is inaccessible
	authenticated = db.Column(db.Boolean, default=False)

	# Should probably default to False and turn to True after email verification
	# Also this will probably have to be in the db i assume
	is_active = True

	# For some reason this has to be a method that get the data from the db??
	def is_authenticated():
		return self.authenticated

	is_anonymous = False

	def get_id(self):
		return self.username

	def set_password(self, password):
		self.passwordHash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.passwordHash, password)

class UserForm(FlaskForm):
	username = StringField(label="Username", render_kw={
		'placeholder': 'Username'
		}, validators=[validators.Length(4, 18), validators.DataRequired()])
	email = StringField(label="Email", render_kw={
		'placeholder': 'Email (Optional)',
		'type': 'email'
		}, validators=[validators.Email(), validators.Optional()])
	password = PasswordField(label="Password",render_kw={
		'placeholder': 'Password'
		}, validators=[validators.InputRequired()])

@app.before_first_request
def initialize():
	db.create_all()
	app.logger.info("Database initialized")
	db.session.add_all([
		Book(
			name = "Countdown to Zeroday",
			description= "asdasda"),
		Book(
			name = "Red Dragon",
			description = "qweqwe"),
		User(
			username = "heiskane",
			email = "asd@asd.asd",
			passwordHash = generate_password_hash("asd"))
	])
	db.session.commit()
	app.logger.info("Database populated with dummy data")

@login_manager.user_loader
def load_user(username):
	return User.query.filter_by(username=username).first()

# https://flask-login.readthedocs.io/en/latest/#configuring-your-application
@login_manager.unauthorized_handler
def unauthorized():
	flash("Please login first")
	return redirect(url_for('login'))

@app.route('/')
def home():
	books = Book.query.all()
	return render_template('home.html', books=books)

@app.route('/login', methods=['GET', 'POST'])
def login():
	title = 'Login'
	user_form = UserForm()

	if not user_form.validate_on_submit():
		app.logger.info("Form did not validate")
		return render_template('login.html', user_form=user_form, title=title)

	user = load_user(user_form.username.data)

	if not user or not user.check_password(user_form.password.data):
		app.logger.info("User not found or passsword is wrong")
		flash("Login failed")
		return render_template('login.html', user_form=user_form, title=title)

	login_user(user)
	app.logger.info("User logged in")
	# Find a way to redirect user back where he came from if it was on the site
	return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	title = 'Register'
	user_form = UserForm()
	if not user_form.validate_on_submit():
		return render_template('login.html', user_form=user_form, title=title)
	if User.query.filter_by(username=user_form.username.data).first():
		app.logger.info("Username taken")
		flash("Username taken") # Implement flashes
		return render_template('login.html', user_form=user_form, title=title)
	user = User(
		username = user_form.username.data,
		email = user_form.email.data)
	app.logger.info(user_form.password.data)
	user.set_password(user_form.password.data)
	db.session.add(user)
	db.session.commit()
	login_user(user)
	return redirect(url_for('home'))

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
	book_form = BookForm()
	if not book_form.validate_on_submit():
		app.logger.info("Form did not validate")
		return render_template('add_book.html', book_form=book_form)
	book = Book()
	book_form.populate_obj(book)
	db.session.add(book)
	db.session.commit()
	return redirect(url_for('home'))

if __name__ == '__main__':
	app.run(debug=True)