import os
import requests
from flask import Flask, redirect, request, render_template
from github import Github

app = Flask(__name__,)

CLIENT_ID = os.environ.get('client_id')
CLIENT_SECRET = os.environ.get('client_secret')
REDIRECT_URI = 'http://0.0.0.0:5000/forking_repo'


@app.route('/')
def redirect_to_github_auth():
    return redirect(f'https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=public_repo')


@app.route('/forking_repo', methods=['GET', 'POST'])
def get_access_token():
    code = request.args['code']
    response = requests.post(f'https://github.com/login/oauth/access_token', data={'client_id': CLIENT_ID,
                                                                                   'client_secret': CLIENT_SECRET,
                                                                                   'code': code},
                                                                            headers={'Accept': 'application/json'})
    access_token = response.json().get('access_token')
    headers = {'Authorization': f'token {access_token}'}

    repo_name = 'test_repo_alisa_5'
    #new_repo = requests.post('https://api.github.com/user/repos', headers=headers, json={'name': repo_name, 'private': False,})

    g = Github(access_token)
    user = g.get_user().login
    repo = g.get_repo('alisazosimova/test')
    repo2 = g.get_repo(f'{user}/{repo_name}')
    contents = repo.get_contents('')
    for file_content in contents:
        if file_content.type == 'dir':
            contents.extend(repo.get_contents(file_content.path))
        else:
            repo2.create_file(file_content.path, 'Add replication app code', file_content.decoded_content)
    return render_template('end_view.html', user=user, repo_name=repo_name)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
