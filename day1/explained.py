# Import libraries
from flask import Flask, render_template

# Create an instance of the Flask class (object)
app = Flask(__name__)

# Use decorator to set the route for the function
@app.route('/')
def hello(): # Define the function
	return "Hello World" # Return a string

# Make sure script was not imported
if __name__ == '__main__':
	app.run(debug=True) # Run the flask app with the debug option