from requests import post
from dotenv import load_dotenv # sudo apt install python3-dotenv
from os import getenv

# Requires .env file with the content:
# API_KEY = asdasdasdasdasd

load_dotenv()
API_KEY = getenv('API_KEY')
headers = {'Authorization': f'Bearer {API_KEY}'}

def send_mail(recipient, subject, content, sender="verify@mypythonproject.rocks"):
	"""
	from mailer import send_mail   
	send_mail(
		recipient="recipient@gmail.com",
		subject="subject",
		content="Hello Potato") 
	"""
	URL = 'https://api.sendgrid.com/v3/mail/send'
	#URL = 'http://127.0.0.1'
	json = {
		"personalizations": [
			{ "to": [
					{
						"email": f"{recipient}"
					}]}],
		"from": {
			"email": f"{sender}"
		},
		"subject": f"{subject}",
		"content": [
			{
				"type": "text/plain",
				"value": f"{content}"}]}
	post(URL, json=json, headers=headers)

if __name__ == '__main__':
	send_mail(
		recipient="example@gmail.com",
		subject="Potato",
		content="Hello World!")