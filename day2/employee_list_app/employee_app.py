from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

class Employee(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String, nullable=False)
	last_name = db.Column(db.String, nullable=False)
	email = db.Column(db.String)

db.create_all()

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/')
def add_employee():
	return "asd"

if __name__ == '__main__':
	app.run(debug=True)