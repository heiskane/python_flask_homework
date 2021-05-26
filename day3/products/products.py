from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os

# python3-flaskext.wtf
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form

app = Flask(__name__)
app.secret_key = os.urandom(32)
db = SQLAlchemy(app)

class Product(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	price = db.Column(db.Float, nullable=False)
	category = db.Column(db.String, nullable=True)

ProductForm = model_form(
	Product,
	base_class=FlaskForm,
	# db_session must be specified or something somewhere breaks for some reason
	db_session=db.session)

@app.before_first_request
def runMeBoi():
	db.create_all()
	db.session.add(Product(
		name = "table",
		price = 14.125,
		category = "chairs"))
	db.session.commit()
	app.logger.info("Database Created")

@app.route('/')
def home():
	products = Product.query.all()
	return render_template('home.html',
		products = products,
		description = """
		Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas vitae dui eget est tincidunt feugiat quis ut mi.
		Nam id neque quis justo laoreet venenatis at in nisi. Donec a risus cursus, hendrerit urna vitae, scelerisque magna.
		Phasellus odio purus, tincidunt quis malesuada sit amet, mattis vitae neque. Aliquam consectetur ipsum vel neque vehicula interdum.
		Proin in nibh augue. Vivamus commodo justo est, pellentesque egestas turpis facilisis sit amet.
		""")

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
	product_form = ProductForm()
	app.logger.info(request.form)
	return render_template('add_product.html', product_form=product_form)

if __name__ == "__main__":
	app.run(debug=True)