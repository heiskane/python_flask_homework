from flask import Flask, render_template, url_for, redirect, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms import PasswordField, StringField, validators, IntegerField, HiddenField

# https://github.com/heiskane/python_flask_homework/blob/main/day5/auth/auth_app.py
from flask_login import login_manager, login_user, login_required, LoginManager, current_user

# https://stackoverflow.com/questions/25324113/email-validation-from-wtform-using-flask
from wtforms.fields.html5 import EmailField

from os import urandom

app = Flask(__name__)
app.secret_key = urandom(32)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, nullable=False, unique=True)
	description = db.Column(db.String(160), nullable=True)
	# Dont know if i want email to be required
	email = db.Column(db.String, nullable=True)
	messages = db.relationship('Message')
	password_hash = db.Column(db.String, nullable=False)
	# Not sure if i need to set nullable if i have a default value 
	authenticated = db.Column(db.Boolean, default=False)
	# Implement admin stuff later
	is_admin = db.Column(db.Boolean, default=False)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	# Not sure why flask login needs a method to get the authenticated attribute
	# Maybe it uses a method so i can do more fancy stuff with it
	def is_authenticated(self):
		return self.authenticated

	def get_id(self):
		return self.username

	# Check if this needs to be in the db to actually work.
	# Probably yes. Implement like the is_authenticated method
	is_active = True

	# Flask-Login wants this for something im not using
	is_anonymous = False

class UserForm(FlaskForm):
	username = StringField(label="Username", render_kw={
		'placeholder': 'Username'
		}, validators=[validators.length(4, 18)])
	email = EmailField(label="Email", validators=[validators.Email(), validators.Optional()])
	# Not sure whats the difference between InputRequired() and DataRequired()
	password = PasswordField(label="Password", validators=[validators.InputRequired()])

# https://stackoverflow.com/questions/41569206/flask-sqlalchemy-foreign-key-relationships
# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html
# Add chat room feature??
# Do i need many-to-one or one-to-many ??

class ChatRoom(db.Model):
	# I think table name defauts to 'chat_room.id'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, unique=True, nullable=False)
	messages = db.relationship('Message')

class Message(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	room_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'), nullable=False)
	sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	content = db.Column(db.String, nullable=False)

class MessageForm(FlaskForm):
	room_id = HiddenField(label="room_id", validators=[validators.DataRequired()])
	content = StringField(label="Message", validators=[validators.DataRequired()])

@app.before_first_request
def initialize_database():
	db.create_all()
	app.logger.info("Database initialized")

	user = User(
		username="heiskane",
		is_admin=True,
		description="The admin man guy",
		email="asd@asd.asd",
		password_hash=generate_password_hash("asd"))
	db.session.add(user)
	db.session.commit()
	app.logger.info("First user added")

	chat_room = ChatRoom(name="Welcome")
	db.session.add(chat_room)
	db.session.commit()

	message = Message(content="Welcome to a chat room", room_id=chat_room.id, sender_id=user.id)
	db.session.add(message)
	db.session.commit()

	# Usage:
	#db.session.add(Message(content="potato", parent_id=room.id))
	#chat = ChatRoom.query.filter_by(name="test").first()
	#messages = Message.query.filter_by(parent_id=chat.id).first()


@login_manager.user_loader
def user_loader(username):
	return User.query.filter_by(username=username).first()

# https://github.com/heiskane/python_flask_homework/blob/main/day5/auth/auth_app.py
@login_manager.unauthorized_handler
def unauthorized():
	flash("Please login first")
	# https://stackoverflow.com/questions/36269485/how-do-i-pass-through-the-next-url-with-flask-and-flask-login
	destination = url_for(request.endpoint,**request.view_args)
	return redirect(url_for('login', next=destination))

@app.route('/')
@login_required
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
	login_user(user)
	destination = request.args.get('next')
	if destination:
		return redirect(destination)
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
	user = User(
		username=username,
		email=user_form.email.data)
	user.set_password(user_form.password.data)
	db.session.add(user)
	db.session.commit()
	app.logger.info("New user registered with the name: " + username)
	login_user(user)
	return redirect(url_for('home'))

# string here does not accept slashes so maybe use 'path' instead
# I guess use string for now but i will have to add illegal chars to usernames
@app.route('/user/<string:username>')
@login_required
def profile_page(username):
	user = user_loader(username)
	if not user:
		abort(404)
	return render_template('user_profile.html', user=user)

@app.route('/chat_room/<string:room_name>')
def chat_room(room_name):
	# Make api endpoint that gives messages as json for some javascript or something
	room = ChatRoom.query.filter_by(name=room_name).first()
	messages = Message.query.filter_by(room_id=room.id)
	message_form = MessageForm()
	message_form.room_id.data = room.id
	#if not current_user.is_anonymous:
	#	message_form.sender_id.data = current_user.id
	#message_form.sender_id.data = 1 # maybe setup an anonymous user
	return render_template('chat_room.html', messages=messages, room=room, message_form=message_form)

@app.route('/chat_rooms')
def chat_rooms():
	rooms = ChatRoom.query.all()
	return render_template('chat_rooms.html', rooms=rooms)

@app.route('/<int:room_id>/send_message', methods=['POST'])
@login_required
def send_message(room_id):
	user = current_user
	message_form = MessageForm()
	if not message_form.validate_on_submit():
		flash("Something went wrong sending the message")
		return redirect(request.referrer)
	# Check if room exists here later
	db.session.add(Message(
		room_id = message_form.room_id.data,
		sender_id = user.id,
		content = message_form.content.data))
	db.session.commit()
	return redirect(request.referrer)

@app.route('/forgot_password')
def forgot_password():
	flash("Get a password manager :)")
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.run(debug=True)