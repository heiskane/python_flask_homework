from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form
from datetime import date
from os import urandom

app = Flask(__name__)
app.secret_key = urandom(32)
db = SQLAlchemy(app)

class Item(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	item_name = db.Column(db.String, nullable=False)
	item_type = db.Column(db.String, nullable=False)
	# https://docs.sqlalchemy.org/en/14/core/type_basics.html
	# datetime.date.today()
	borrow_date = db.Column(db.Date, default=date.today(), nullable=False)
	returned = db.Column(db.Boolean, default=False, nullable=True)

ItemForm = model_form(
	model=Item,
	db_session=db.session,
	base_class=FlaskForm)

@app.before_first_request
def initialize():
	db.create_all()
	app.logger.info("Database initialized")
	db.session.add_all([
		Item(
			item_name="Hat",
			item_type="Apparel",
			borrow_date=date.today(),
			returned=True),
		Item(
			item_name="Guitar",
			item_type="Instrument",
			borrow_date=date.today(),
			returned=False),
		Item(
			item_name="Laptop",
			item_type="Computer",
			borrow_date=date.today(),
			returned=False)
	])
	db.session.commit()
	app.logger.info("Initial items added to database")
	app.logger.info(Item.query.all())

@app.route('/')
def home():
	items = Item.query.all()
	return render_template('home.html', items=items)

@app.route('/add_item/<int:id>', methods=['GET', 'POST'])
@app.route('/add_item', methods=['GET', 'POST'])
def add_item(id=None):
	form = ItemForm()
	item = Item()
	if id:
		item = Item.query.get_or_404(id)
	if request.method == 'GET':
		# https://github.com/heiskane/python_flask_homework/blob/main/day4/more_practice/app.py
		form = ItemForm(obj=item)
		return render_template('add_item.html', form=form)
	if not form.validate_on_submit():
		app.logger.info(form)
		flash("Form validation failed", "Error")
		return render_template('add_item.html', form=form)
	form.populate_obj(item)
	db.session.add(item)
	db.session.commit()
	flash("Item added", "Message")
	return redirect(url_for('home'))

@app.route('/delete_item/<int:id>')
def delete_item(id):
	item = Item.query.get_or_404(id)
	db.session.delete(item)
	db.session.commit()
	flash(item.item_name + " deleted", "Message")
	return redirect(url_for('home'))

@app.route('/returned/<int:id>')
def returned(id):
	item = Item.query.get_or_404(id)
	item.returned = False if item.returned else True
	db.session.add(item)
	db.session.commit()
	flash(item.item_name + " returned set to " + str(item.returned), "Message" )
	return redirect(url_for('home'))

if __name__ == '__main__':
	app.run(debug=True)