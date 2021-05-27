from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form # m
from os import urandom

app = Flask(__name__)
app.secret_key = urandom(32)
db = SQLAlchemy(app)

class Client(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String, nullable=False)
	last_name = db.Column(db.String, nullable=False)
	email = db.Column(db.String, nullable=True)
	# Not sure if phonenumber should be a string instead
	phone_number = db.Column(db.Integer, nullable=False)

ClientForm = model_form(
	model=Client,
	base_class=FlaskForm,
	db_session=db.session)

@app.before_first_request
def intialize():
	db.create_all()
	app.logger.info("Database Created")
	db.session.add(Client(
		first_name='John',
		last_name='Connor',
		email='john.connor@example.com',
		phone_number='123123123'))
	db.session.commit()
	app.logger.info("First db entry created")

@app.route('/')
def home():
	clients = Client.query.all()
	return render_template('home.html', clients=clients)

@app.route('/register_client/<int:id>', methods=['GET', 'POST'])
@app.route('/register_client', methods=['GET', 'POST'])
def register_client(id=None):
	client = Client()

	if id:
		client = Client.query.get_or_404(id)
	# https://github.com/heiskane/python_flask_homework/blob/main/day4/more_practice/app.py
	form = ClientForm(obj=client)

	if request.method == 'GET':
		return render_template('register.html', form=form)

	if not form.validate_on_submit():
		flash("Form validation failed", "Error")
		return render_template('register.html', form=form)

	form.populate_obj(client)
	db.session.add(client)
	db.session.commit()
	flash("Client added to the database", "Message")
	return redirect(url_for('home'))

@app.route('/delete_client/<int:id>')
def delete_client(id):
	client = Client.query.get_or_404(id)
	db.session.delete(client)
	db.session.commit()
	return redirect(url_for('home'))

if __name__ == '__main__':
	app.run(debug=True)