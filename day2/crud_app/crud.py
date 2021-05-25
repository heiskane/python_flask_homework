from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DB_URI'] = 'sqlite:///:memory:' # This is also default value
db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, nullable=False, unique=True)
	password = db.Column(db.String, nullable=False)

	def __repr__(self):
		return f'Username: {self.username}'

db.create_all()

@app.route('/')
def home():
	users = User.query.all()
	return render_template("home.html", users=users, title="Basic CRUD")

# Accept POST requests
# https://stackoverflow.com/questions/37362971/how-to-allow-post-method-with-flask
@app.route('/register', methods=['POST'])
def register():
	username = request.form['username']
	# https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
	password = generate_password_hash(request.form['password'], method='sha256')
	user = User()
	user.username = username
	user.password = password
	db.session.add(user)
	db.session.commit()
	return redirect(url_for('home'))

@app.route('/delete_user', methods=['POST'])
def delete_user():
	id = request.form['id']
	# https://stackoverflow.com/questions/27158573/how-to-delete-a-record-by-id-in-flask-sqlalchemy
	User.query.filter_by(id=id).delete()
	db.session.commit()
	return redirect(url_for('home'))

@app.route('/update_user', methods=['POST'])
def update_user():
	id = request.form['id']
	username = request.form['username']
	password = request.form['password']
	user = User.query.filter_by(id=id).first()
	user.username = username if username else user.username
	password_hash = generate_password_hash(request.form['password'], method='sha256')
	user.password = password_hash if password else user.password
	db.session.commit()
	return redirect(url_for('home'))


@app.route('/login')
def login():
	return "TODO: handle login"

if __name__ == '__main__':
	app.run(debug=True)