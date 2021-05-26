from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

class Product(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	price = db.Column(db.Float, nullable=False)
	category = db.Column(db.String, nullable=True)

@app.before_first_request
def runMeBoi():
	db.create_all()
	db.session.add(Product(
		name = "table",
		price = 14.125,
		category = "chairs"))
	db.session.commit()

@app.route('/')
def home():
	products = Product.query.all()
	return render_template('home.html', products=products)

app.run(debug=True)