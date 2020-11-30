import os
import pusher

from flask import Flask, jsonify
from flask import url_for
from flask import render_template

from dotenv import load_dotenv
load_dotenv()

import requests

from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['LICHESS_CLIENT_ID'] =  os.getenv("LICHESS_CLIENT_ID")
app.config['LICHESS_CLIENT_SECRET'] = os.getenv("LICHESS_CLIENT_SECRET")
app.config['LICHESS_ACCESS_TOKEN_URL'] = 'https://oauth.lichess.org/oauth'
app.config['LICHESS_AUTHORIZE_URL'] = 'https://oauth.lichess.org/oauth/authorize'

pusher_client = pusher.Pusher(
  app_id = os.getenv("PUSHER_APP_ID"),
  key = os.getenv("PUSHER_KEY"),
  secret = os.getenv("PUSHER_SECRET"),
  cluster = os.getenv("PUSHER_CLUSTER"),
  ssl = True
)

oauth = OAuth(app)
oauth.register('lichess')

@app.route('/')
@app.route('/success')
def home():
    return render_template("index.html")

@app.route('/register')
def login():
    redirect_uri = url_for("authorize", _external=True)
    """
    If you need to append scopes to your requests, add the `scope=...` named argument
    to the `.authorize_redirect()` method. For admissible values refer to https://lichess.org/api#section/Authentication. 
    Example with scopes for allowing the app to read the user's email address:
    `return oauth.lichess.authorize_redirect(redirect_uri, scope="email:read")`
    """
    return oauth.lichess.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = oauth.lichess.authorize_access_token()
    bearer = token['access_token']
    headers = {'Authorization': f'Bearer {bearer}'}
    response = requests.get("https://lichess.org/api/account", headers=headers)
    pusher_client.trigger('registrations', 'signup', response.json())
    return redirect('/success')
    # return jsonify(**response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = int(os.environ.get("PORT", 5000)))
