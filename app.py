import os

from github import Github
from flask import Flask, redirect, request, render_template
import requests
from requests.exceptions import RequestException

app = Flask(__name__)

CLIENT_ID = os.environ.get('client_id')
CLIENT_SECRET = os.environ.get('client_secret')
# Name of the new repo in user's github repository with the replicated code
NEW_REPO_NAME = 'self_replicating_github_app'


@app.errorhandler(RequestException)
def handle_exception(error):
    return f'An error occured: {error}'


@app.route('/')
def redirect_to_github_auth():
    return redirect(f'https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=public_repo')


@app.route('/replicating_code', methods=['GET', 'POST'])
def replicate_app_code():
    code = request.args['code']
    response = requests.post(f'https://github.com/login/oauth/access_token',
                             headers={'Accept': 'application/json'},
                             data={'client_id': CLIENT_ID,
                                   'client_secret': CLIENT_SECRET,
                                   'code': code},
                             )
    response.raise_for_status()
    access_token = response.json().get('access_token')
    headers = {'Authorization': f'token {access_token}'}
    # Authorized PyGitHub client object
    github_client = Github(access_token)
    auth_user_name = github_client.get_user().login
    # Create empty public GitHub repository
    new_repo_for_auth_user = requests.post('https://api.github.com/user/repos',
                                           headers=headers,
                                           json={'name': NEW_REPO_NAME,
                                                 'private': False, })
    new_repo_for_auth_user.raise_for_status()
    # Get new repo as Github.Repository object
    new_app_repo = github_client.get_repo(f'{auth_user_name}/{NEW_REPO_NAME}')
    # Get repo with the app code as Github.Repository object
    app_repo = github_client.get_repo('alisa-test/replication_app_1')
    contents = app_repo.get_contents('')
    # Copy all files from app_repo to new_app_repo
    for file_content in contents:
        if file_content.type == 'dir':
            contents.extend(app_repo.get_contents(file_content.path))
        else:
            new_app_repo.create_file(file_content.path, 'Add replication app code', file_content.decoded_content)
    return render_template('end_view.html', user=auth_user_name, repo_name=NEW_REPO_NAME)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
