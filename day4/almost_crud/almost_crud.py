from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from os import urandom

# https://terokarvinen.com/2020/flask-automatic-forms/?fromSearch=
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form

app = Flask(__name__)
app.secret_key = urandom(32)
db = SQLAlchemy(app)

class Thing(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)

# https://terokarvinen.com/2020/flask-automatic-forms/?fromSearch=
ThingForm = model_form(
	model=Thing,
	db_session=db.session,
	base_class=FlaskForm)

@app.before_first_request
def initDb():
	db.create_all()
	app.logger.info("Created DB")
	db.session.add(Thing(name="Potato"))
	db.session.add(Thing(name="tomato"))
	db.session.commit()
	app.logger.info("Added dummy entries to DB")

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/notes')
def notes():
	form = ThingForm()
	things = Thing.query.all()
	return render_template('notes.html', form=form, things=things)

@app.route('/add', methods=['POST'])
def add():
	form = ThingForm()

	if not form.validate_on_submit():
		flash("Form validation failed", "Error")
		return redirect(url_for('notes'))

	app.logger.info("Form validated")
	thing = Thing()
	form.populate_obj(thing) # Memorize this
	db.session.add(thing)
	db.session.commit()
	app.logger.info(Thing.query.all())
	flash("Thing added", "Message")
	return redirect(url_for('notes'))


if __name__ == '__main__':
	app.run(debug=True)