from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
# https://terokarvinen.com/2020/flask-automatic-forms/?fromSearch=
from wtforms.ext.sqlalchemy.orm import model_form
from flask_wtf import FlaskForm
from os import urandom

app = Flask(__name__)
app.secret_key = urandom(32)
db = SQLAlchemy(app)

class Note(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user = db.Column(db.String, nullable=True)
	note = db.Column(db.String, nullable=False)

# https://terokarvinen.com/2020/flask-automatic-forms/?fromSearch=
NoteForm = model_form(
	model=Note,
	base_class=FlaskForm,
	db_session=db.session
)

@app.before_first_request
def runMeBoi():
	db.create_all()
	db.session.add(Note(note="Hello World"))
	db.session.add(Note(note="Hello Other World"))
	db.session.commit()
	# List all notes for debuggin
	app.logger.info([ note.note for note in Note.query.all() ])

@app.route('/')
def home():
	note_form = NoteForm()
	return render_template('home.html', form=note_form)

@app.route('/post', methods=['POST'])
def post():
	flash(request.form['note'], 'Message')
	return redirect(url_for('home'))

@app.route('/gobuster-is-my-only-weakness')
def not_so_secret_secret():
	flash("How i could possibly seen this coming?", 'NotSoSecret')
	return redirect(url_for('home'))

if __name__ == '__main__':
	app.run(debug=True)