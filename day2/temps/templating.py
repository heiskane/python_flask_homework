import sys
# Only run on python3
assert sys.version_info.major == 3

from flask import Flask, render_template
from flaskext.markdown import Markdown # pip3 install Flask-Markdown

app = Flask(__name__)
Markdown(app)

@app.route("/")
def home():
	names = ["bob", "joe", "alice", "traunt"]
	return render_template("home.html", title="Hello Variable", names=names)

@app.route("/other")
def other():
	return render_template('other.html')

if __name__ == "__main__":
	app.run(debug=True)