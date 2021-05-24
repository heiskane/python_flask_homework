from flask import Flask, render_template
from flaskext.markdown import Markdown # pip3 install Flask-Markdown

app = Flask(__name__)
Markdown(app)

@app.route('/')
def index():
	return render_template("home.html")

@app.route('/hello')
def hello():
	return "Hello World"


if __name__=='__main__':
	app.run(debug=True)