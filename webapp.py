import os

import requests
from flask import Flask, redirect, request

app = Flask(__name__)

client_id = '7f3dbf9890fcc37cd678'
redirect_uri = 'http://localhost:5000/hello'
client_secret = '9adbe614b33907e6ed074e8bf9101e3b72f4475e'


@app.route('/')
def redirect_to_github_auth():
    return redirect(f'https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}')


@app.route('/hello')
def get_access_token():
    code = request.args['code']
    response = requests.post(f'https://github.com/login/oauth/access_token', data={'client_id': client_id,
                                                                                   'client_secret': client_secret,
                                                                                   'code': code},
                             headers={'Accept': 'application/json'})
    access_token = response.json().get('access_token')
    auth_header = f'Authorization: token {access_token}'
    g=requests.get('https://api.github.com/user', headers={'Authorization': f'token {access_token}'})
    return g.content

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
