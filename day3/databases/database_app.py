from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user = db.Column(db.String, nullable=False)
	comment = db.Column(db.String, nullable=False)

@app.before_first_request
def runMeBoi():
	db.create_all()

	comment = Comment(comment="Hello World", user="potato")
	db.session.add(comment)

	comment = Comment(comment="Hello Other World", user="tomato")
	db.session.add(comment)

	db.session.commit()

@app.route('/')
def home():
	comments = Comment.query.all()
	return render_template('home.html', comments=comments)

if __name__ == "__main__":
	app.run(debug=True)