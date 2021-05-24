from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
db = SQLAlchemy(app)

class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	todo = db.Column(db.String, nullable=False)

	def __repr__(self):
		return self.todo

db.create_all()

@app.route('/')
def home():
	data = Todo.query.all()
	return render_template('index.html', data=data)

@app.route('/add')
def add():
	content = request.args.get('todo')
	todo = Todo()
	todo.todo = content
	db.session.add(todo)
	db.session.commit()
	return redirect(url_for('home'))


if __name__ == '__main__':
	app.run(debug=True)