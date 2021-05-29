Tero
==> 
teejo.py
 <==
# User example - 
http://TeroKarvinen.com

from flask import Flask, render_template, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy

from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form

from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, validators

app = Flask(__name__)
app.secret_key = "Ieph1che9Ea3Phighul5FohM0iivee"
db = SQLAlchemy(app)

class Task(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)

TaskForm = model_form(Task, base_class=FlaskForm, db_session=db.session)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String, nullable=False, unique=True)
	passwordHash = db.Column(db.String, nullable=False)

	def setPassword(self, password):
		self.passwordHash = generate_password_hash(password)

	def checkPassword(self, password):
		return check_password_hash(self.passwordHash, password)

class UserForm(FlaskForm):
	email = StringField("email", validators=[validators.Email()])
	password = PasswordField("password", validators=[validators.InputRequired()])

## User utility functions

def currentUser():
	try:
		uid = int(session["uid"])
	except:
		return None
	return User.query.get(uid)

app.jinja_env.globals["currentUser"] = currentUser

## User view

@app.route("/user/login", methods=["GET", "POST"])
def loginView():
	form = UserForm()

	if form.validate_on_submit():
		email = form.email.data

		password = form.password.data


		user = User.query.filter_by(email=email).first()
		if not user:
			flash("Login failed.")
			print("No such user")
			return redirect("/user/login")
		if not user.checkPassword(password):
			flash("Login failed.")
			print("Wrong password")
			return redirect("/user/login")

		session["uid"]= user.id

		flash("Login successful.")
		return redirect("/")
		
	return render_template("login.html", form=form)

@app.route("/user/register", methods=["GET", "POST"])
def registerView():
	form = UserForm()

	if form.validate_on_submit():
		email = form.email.data

		password = form.password.data


		if User.query.filter_by(email=email).first():
			flash("User already exits! Please log in.")
			return redirect("/user/login")

		user = User(email=email)
		user.setPassword(password)

		db.session.add(user)
		db.session.commit()

		flash("Registration successfull. Welcome! Now, log in.")
		return redirect("/user/login")

	return render_template("register.html", form=form)

@app.route("/user/logout")
def logoutView():
	session["uid"] = None
	flash("Logged out. See you again!")
	return redirect("/")

## Main views

@app.before_first_request
def initDb():
	db.create_all()

	task = Task(name="Jog 10 km")
	db.session.add(task)
	db.session.commit()

@app.errorhandler(404)
def custom404(e):
	return render_template("404.html")

@app.route("/task/<int:id>/edit", methods=["GET", "POST"])
@app.route("/task/add", methods=["GET", "POST"])
def addView(id=None):
	task = Task()
	if id:
		task = Task.query.get_or_404(id)

	fields = TaskForm(obj=task)

	if fields.validate_on_submit():
		fields.populate_obj(task)
		db.session.add(task)
		db.session.commit()

		flash("Added!")
		return redirect("/")
	
	return render_template("add.html", fields=fields)

@app.route("/task/<int:id>/delete")
def deleteView(id):
	task = Task.query.get_or_404(id)
	db.session.delete(task)
	db.session.commit()

	flash("Deleted.")
	return redirect("/")

@app.route("/")
def indexView():
	tasks = Task.query.all()
	return render_template("index.html", tasks=tasks)

if __name__ == "__main__":
	
app.run
()

==> templates/404.html <==
{% set title="404 page not found" %}
{% extends "base.html" %}

{% block content %}

<p>Sorry, we lost your page. 
	<a href="/">See you at home.</a>
</p>
	
{% endblock content %}

==> templates/add.html <==
{% set title="Add Teejo Task" %}
{% extends "base.html" %}

{% block content %}

	<form method=post>
		{% for field in fields %}
			{% if not field.flags.hidden %}
				{{ field.label }}
			{% endif %}

			{{ field }}

			{% for err in field.errors %}
				<b>{{ err }}</b>
			{% endfor %}

			<br>
		{% endfor %}
		<input type=submit>
	</form>

{% endblock content %}

==> templates/base.html <==
{% if not title %}
	{% set title="Welcome to Teejo" %}
{% endif %}

<!doctype html>
<html lang=en>
	<head>
		<title>{{ title }}</title>
		<meta charset="utf-8">
	</head>
	<body>
		{% for msg in get_flashed_messages() %}
			<p><b>{{ msg }}</b></p>
		{% endfor %}
		<nav>
			<a href="/">Home</a> - 
			<a href="/task/add">Add task</a> - 
			{% if currentUser() %}
				<a href="/user/logout">Logout</a> - 
				{{ currentUser().email }} - 
			{% else %}
				<a href="/user/login">Login</a> - 
				<a href="/user/register">Register</a>
			{% endif %}
		</nav>

		<h1>{{ title }}</h1>
		
		{% block content %}
		<p>Welcome</p>
		{% endblock content %}

	</body>
</html>

==> templates/index.html <==
{% set title="Your Teejo Tasks" %}
{% extends "base.html" %}

{% block content %}

	{% for task in tasks %}
		<p>
			<a href="/task/{{ task.id }}/edit">
				{{ 
task.name
 }}
			</a>
			-
			<a href="/task/{{ task.id }}/delete">Delete</a>
		</p>
	{% endfor %}
	
{% endblock content %}

==> templates/login.html <==
{% set title="Login" %}
{% extends "base.html" %}

{% block content %}

	<form method=post>
		{% for field in form %}
			{% if not field.flags.hidden %}
				{{ field.label }}
			{% endif %}

			{{ field }}

			{% for err in field.errors %}
				<b>{{ err }}</b>
			{% endfor %}

			<br>
		{% endfor %}
		<input type=submit>
	</form>

{% endblock content %}

==> templates/register.html <==
{% set title="Register new user" %}
{% extends "base.html" %}

{% block content %}

	<form method=post>
		{% for field in form %}
			{% if not field.flags.hidden %}
				{{ field.label }}
			{% endif %}

			{{ field }}

			{% for err in field.errors %}
				<b>{{ err }}</b>
			{% endfor %}

			<br>
		{% endfor %}
		<input type=submit>
	</form>

{% endblock content %}