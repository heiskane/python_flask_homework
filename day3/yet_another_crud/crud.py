from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy

# https://terokarvinen.com/2020/flask-automatic-forms/?fromSearch=
from wtforms.ext.sqlalchemy.orm import model_form
from flask_wtf import FlaskForm

from os import urandom

app = Flask(__name__)
app.secret_key = urandom(32)
db = SQLAlchemy(app)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, nullable=False)
	post_data = db.Column(db.String, nullable=False)
	likes = db.Column(db.Integer, nullable=True)
	# Maybe add replies?

@app.before_first_request
def runMeFirst():
	db.create_all()
	db.session.add(Post(
		username = "Heiskane",
		post_data = "Hello World",
		likes = 9001))
	db.session.commit()
	app.logger.info(Post.query.all())

PostForm = model_form(
	model = Post,
	db_session = db.session,
	base_class=FlaskForm)

@app.route('/')
def home():
	form = PostForm()
	posts = Post.query.all()
	return render_template('home.html', form=form, posts=posts)

@app.route('/post', methods=['POST'])
def post():
	form = PostForm()
	if not form.validate_on_submit():
		flash("Post validation failed")
		return redirect(url_for('home'))
	app.logger.info("Valitation Successful")
	username = request.form['username']
	post_data = request.form['post_data']
	db.session.add(Post(username=username, post_data=post_data, likes=0))
	db.session.commit()
	app.logger.info(Post.query.all())
	flash("Posted Successfully")
	return redirect(url_for('home'))

@app.route('/update', methods=['POST'])
def update():
	id = request.form['id']
	post = Post.query.filter_by(id=id).first()
	post_data = request.form['post_data']
	post.post_data = post_data
	db.session.commit()
	flash("Post Updated")
	return redirect(url_for('home'))

# https://flask.palletsprojects.com/en/2.0.x/quickstart/#routing
@app.route('/api/like/<int:post_id>')
def like(post_id):
	post = Post.query.filter_by(id=post_id).first()
	post.likes += 1
	db.session.commit()
	flash("You liked a post!")
	return redirect(url_for('home'))

@app.route('/api/dislike/<int:post_id>')
def dislike(post_id):
	post = Post.query.filter_by(id=post_id).first()
	post.likes -= 1
	db.session.commit()
	flash("You disliked a post!")
	return redirect(url_for('home'))

@app.route('/api/delete/<int:post_id>')
def delete(post_id):
	post = Post.query.filter_by(id=post_id).first()
	db.session.delete(post)
	db.session.commit()
	flash("You deleted a post!")
	return redirect(url_for('home'))

if __name__ == '__main__':
	app.run(debug=True)