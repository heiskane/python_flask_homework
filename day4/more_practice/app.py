from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from wtforms.ext.sqlalchemy.orm import model_form # m
from flask_wtf import FlaskForm # m
from os import urandom

app = Flask(__name__)
app.secret_key = urandom(32)
db = SQLAlchemy(app)

class Potato(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)

PotatoForm = model_form(
	model=Potato,
	db_session=db.session,
	base_class=FlaskForm)

@app.before_first_request
def initDB():
	db.create_all()
	app.logger.info("DB Created")
	db.session.add(Potato(name="Japanese Sweet Potato"))
	db.session.add(Potato(name="Austrian Crescent"))
	db.session.commit()
	app.logger.info("Dummy data added")

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/potato')
def potato():
	form = PotatoForm()
	potatoes = Potato.query.all()
	return render_template('potato.html', form=form, potatoes=potatoes)

@app.route('/add_potato', methods=['POST'])
def add_potato():
	form = PotatoForm()
	if not form.validate_on_submit():
		flash('Field validation failed', 'Error')
		return redirect(url_for('potato'))
	potato = Potato()
	form.populate_obj(potato)
	db.session.add(potato)
	db.session.commit()
	flash('Added potato', 'Message')
	return redirect(url_for('potato'))

if __name__ == '__main__':
	app.run(debug=True)