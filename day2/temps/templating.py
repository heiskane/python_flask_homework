import sys
# Only run on python3
assert sys.version_info.major == 3

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
	names = ["bob", "joe", "alice", "traunt"]
	return render_template("home.html", title="Hello Variable", names=names)

if __name__ == "__main__":
	app.run(debug=True)