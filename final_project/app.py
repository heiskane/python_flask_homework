from flask import Flask, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms import PasswordField, StringField, validators

# https://stackoverflow.com/questions/25324113/email-validation-from-wtform-using-flask
from wtforms.fields.html5 import EmailField
from os import urandom

app = Flask(__name__)
app.secret_key = urandom(32)
db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, nullable=False, unique=True)
	# Dont know if i want email to be required
	email = db.Column(db.String, nullable=True)
	password_hash = db.Column(db.String, nullable=False)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

class UserForm(FlaskForm):
	username = StringField(label="Username", render_kw={
		'placeholder': 'Username'
		}, validators=[validators.length(4, 18)])
	email = EmailField(label="Email", validators=[validators.Email()])
	# Not sure whats the difference between InputRequired() and DataRequired()
	password = PasswordField(label="Password", validators=[validators.InputRequired()])

@app.before_first_request
def initialize_database():
	db.create_all()
	app.logger.info("Database initialized")
	db.session.add(User(
		username="heiskane",
		email="asd@asd.asd",
		password_hash=generate_password_hash("asd")))
	db.session.commit()
	app.logger.info("First user added")

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	user_form = UserForm()
	if not user_form.validate_on_submit():
		return render_template('login.html', user_form=user_form)
	user = User.query.filter_by(username=user_form.username.data).first()
	if not user or not user.check_password(user_form.password.data):
		flash("Login failed")
		return redirect(url_for('login'))
	return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register_user():
	user_form = UserForm()
	if not user_form.validate_on_submit():
		return render_template('register.html', user_form=user_form)
	username = user_form.username.data
	if User.query.filter_by(username=username).first():
		flash("Username taken")
		return redirect(url_for('register_user'))
	email = user_form.email.data
	user = User(
		username=username,
		email=email)
	user.set_password(user_form.password.data)
	app.logger.info("New user registered with the name: " + username)
	db.session.add(user)
	db.session.commit()
	return redirect(url_for('home'))

if __name__ == '__main__':
	app.run(debug=True)