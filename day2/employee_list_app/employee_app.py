from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4asdasdasdQ8z\n\xec]/'
db = SQLAlchemy(app)

class Employee(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String, nullable=False)
	last_name = db.Column(db.String, nullable=False)
	email = db.Column(db.String)

db.create_all()

@app.route('/')
def home():
	employees = Employee.query.all()
	return render_template('home.html', employees=employees)

@app.route('/add_employee', methods=['POST'])
def add_employee():
	employee = Employee()
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	email = request.form['email']
	if first_name and last_name and email:
		employee.first_name = first_name
		employee.last_name = last_name
		employee.email = email
		db.session.add(employee)
		db.session.commit()
	else:
		flash("Missing required fields")
	return redirect(url_for('home'))

@app.route('/delete_employee', methods=['POST'])
def delete_employee():
	id = request.form['id']
	employee = Employee.query.get(id)
	db.session.delete(employee)
	db.session.commit()
	return redirect(url_for('home'))

@app.route('/update_employee', methods=['POST'])
def update_employee():
	# https://stackoverflow.com/questions/6699360/flask-sqlalchemy-update-a-rows-information
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	email = request.form['email']
	id = request.form['id']
	if first_name and last_name and email and id:
		employee = Employee.query.get(id)
		employee.first_name = first_name
		employee.last_name = last_name
		employee.email = email
		db.session.commit()
	else:
		flash("Missing required fields")
	return redirect(url_for('home'))

if __name__ == '__main__':
	app.run(debug=True)