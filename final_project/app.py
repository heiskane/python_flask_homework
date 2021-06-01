from flask import Flask, render_template, url_for, redirect, flash, request, abort, jsonify, escape
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms import PasswordField, StringField, validators, IntegerField, HiddenField

# https://github.com/heiskane/python_flask_homework/blob/main/day5/auth/auth_app.py
from flask_login import login_manager, login_user, login_required, LoginManager, current_user, logout_user

# https://stackoverflow.com/questions/25324113/email-validation-from-wtform-using-flask
from wtforms.fields.html5 import EmailField

from os import urandom
from datetime import datetime, timedelta

from mailer import send_mail

# TODO: Fill the homepage
# TODO: Work on profile page
# TODO: Private rooms that allow certain users?
# TODO: user bans?

app = Flask(__name__)
app.secret_key = urandom(32)
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql:///heiskanewsgi'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, nullable=False, unique=True)
	description = db.Column(db.String(160), nullable=True)
	# Dont know if i want email to be required
	email = db.Column(db.String, unique=True, nullable=True) # set to unique after testing
	is_verified = db.Column(db.Boolean, default=False)
	verify_code = db.Column(db.String, nullable=False)
	messages = db.relationship('Message', backref=db.backref('sender', lazy=True))
	rooms = db.relationship('ChatRoom', backref=db.backref('owner', lazy=True))
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
	email = EmailField(label="Email", render_kw={
		'placeholder': 'Optional'
		}, validators=[validators.Email(), validators.Optional()])
	# Not sure whats the difference between InputRequired() and DataRequired()
	password = PasswordField(label="Password", validators=[validators.InputRequired()])

# https://stackoverflow.com/questions/41569206/flask-sqlalchemy-foreign-key-relationships
# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html
class ChatRoom(db.Model):
	# I think table name defauts to 'chat_room'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, unique=True, nullable=False)
	description = db.Column(db.String(160), nullable=False)
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	messages = db.relationship('Message', backref=db.backref('room', lazy=True))

class ChatRoomForm(FlaskForm):
	name = StringField(label="Room Name", validators=[validators.length(3, 32), validators.DataRequired()])
	description = StringField(label="Room Description", validators=[validators.length(3, 159), validators.DataRequired()])

class Message(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	room_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'), nullable=False)
	sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	content = db.Column(db.String, nullable=False)
	sent_time = db.Column(db.DateTime, nullable=False)

class MessageForm(FlaskForm):
	room_id = HiddenField(label="room_id", validators=[validators.DataRequired()])
	content = StringField(label="Message", validators=[validators.DataRequired()])

@app.before_first_request
def initialize_database():
	db.create_all()
	app.logger.info("Database initialized")

	if not User.query.filter_by(username="heiskane").first():
		user = User(
			username="heiskane",
			is_admin=True,
			description="The admin man guy",
			email="asd@asd.asd",
			verify_code = urandom(16).hex(),
			password_hash=generate_password_hash("asd"))
		db.session.add(user)
		db.session.commit()
		app.logger.info("First user added")

	if not ChatRoom.query.filter_by(name="Welcome").first():
		chat_room = ChatRoom(name="Welcome", description="A room for newcomers!", owner=user)
		db.session.add(chat_room)
		db.session.commit()

		message = Message(
			content="Welcome to a chat room",
			room=chat_room, sender=user,
			sent_time = datetime(2021, 5, 25))
		db.session.add(message)
		db.session.commit()

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

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

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
	login_user(user)
	destination = request.args.get('next')
	if destination:
		return redirect(destination)
	return redirect(url_for('home'))

# https://flask-login.readthedocs.io/en/latest/
@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

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

	if email and User.query.filter_by(email=email).first():
		# I really dont like telling the user that the email i registered
		# but not sure what i should do diffrently
		flash('Account already exists')
		return redirect(url_for('register_user'))
	
	user = User(
		username=username,
		email=user_form.email.data,
		# Temporary code. New one is set in get_verify_code
		verify_code=urandom(16).hex())
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

@app.route('/user/set_email', methods=['POST'])
@login_required
def set_email():
	email = request.form.get('email')
	if User.query.filter_by(email=email).first():
		flash("No")
		return redirect(url_for('profile_page', username=current_user.username))
	current_user.email = email
	app.logger.info(email)
	db.session.commit()
	return redirect(url_for('profile_page', username=current_user.username))

@app.route('/verify')
@login_required
def verify():
	code = request.args.get('code')
	if not current_user.verify_code == code:
		flash("Something went wrong!")
		return redirect(url_for('profile_page', username=current_user.username))
	current_user.is_verified = True
	db.session.commit()
	flash("Email successfully verified!")
	return redirect(url_for('profile_page', username=current_user.username))

@app.route('/get_verify_code')
@login_required
def get_verify_code():
	if current_user.is_verified:
		flash("User already verified!")
		return redirect(url_for('profile_page', username=current_user.username))
	if not current_user.email:
		flash("Please add an email address to your profile first")
		return redirect(url_for('profile_page', username=current_user.username))
	current_user.verify_code = urandom(16).hex()
	db.session.commit()
	content = f"""
	Thank you for verifying your email!
	Here is your code: {current_user.verify_code}
	You can also just use this link here: http://mypythonproject.rocks/verify?code={current_user.verify_code}
	"""
	send_mail(
		recipient=current_user.email,
		subject="Verify Code",
		content=content)
	app.logger.info("Verify code sent")
	flash("Verify code sent to your email!")
	return redirect(url_for('profile_page', username=current_user.username))

@app.route('/chat_room/<string:room_name>')
def chat_room(room_name):
	room = ChatRoom.query.filter_by(name=room_name).first()
	if not room:
		abort(404)
	# https://www.youtube.com/watch?v=juPQ04_twtA
	messages = room.messages
	message_form = MessageForm()
	message_form.room_id.data = room.id
	# maybe setup an anonymous user to use current_user.is_anonymous
	return render_template(
		'chat_room.html',
		messages=messages,
		message_form=message_form,
		room=room)

@app.route('/add_room', methods=['GET', 'POST'])
@login_required
def add_room():
	room_form = ChatRoomForm()
	if not room_form.validate_on_submit():
		return render_template('add_room.html', room_form=room_form)
	app.logger.info(room_form.name.data)
	app.logger.info(room_form.description.data)
	app.logger.info(current_user.id)
	db.session.add(ChatRoom(
		name = room_form.name.data,
		description = room_form.description.data,
		owner = current_user))
	db.session.commit()
	return redirect(url_for('chat_rooms'))

@app.route('/chat_rooms')
def chat_rooms():
	rooms = ChatRoom.query.all()
	return render_template('chat_rooms.html', rooms=rooms)

@app.route('/get_messages/<int:room_id>')
def get_messages(room_id):
	room = ChatRoom.query.get(room_id)
	message_list = []
	if not room.messages:
		return ''
	messages = room.messages[-500:]
	for message in messages:
		if datetime.now() - message.sent_time < timedelta(days = 1):
			# https://www.w3schools.com/python/python_datetime.asp
			sent_time = message.sent_time.strftime("%H:%M")
		else:
			sent_time = message.sent_time.strftime("%d/%m")
		message_list.append({
			'sender': f'{escape(message.sender.username)}',
			'content': f'{escape(message.content)}',
			'sent_time': f'{sent_time}'})
	return jsonify(message_list)

@app.route('/<int:room_id>/send_message', methods=['GET', 'POST'])
@login_required
def send_message(room_id):
	user = current_user
	message_form = MessageForm()
	if not message_form.validate_on_submit():
		#flash("Something went wrong sending the message")
		return redirect(request.referrer)
	room = ChatRoom.query.get(message_form.room_id.data)
	if not room:
		abort(404)
	db.session.add(Message(
		room_id = room.id,
		sender_id = user.id,
		content = message_form.content.data,
		sent_time = datetime.now()))
	db.session.commit()
	return redirect(request.referrer)
	#return redirect(url_for('chat_room', room_id=room_id))

@app.route('/forgot_password')
def forgot_password():
	flash("Get a password manager :)")
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.run(debug=True)