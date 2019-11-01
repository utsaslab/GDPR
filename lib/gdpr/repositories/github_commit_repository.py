import os
import requests
import json

class GithubCommitRepository():
    def __init__(self, auth=None, repo=None):
        self.auth = auth
        self.repo = repo

    def set_auth(self, username, password):
        self.auth = (username, password)

    def set_repo(self, owner, name):
        self.repo = (owner, name)

    def for_id(self, sha):
        if self.auth is None:
            raise ValueError('Github auth credentials are not defined. Please provide username and password.')

        if self.repo is None:
            raise ValueError('Github repo information is not defined. Please provide repo owner and name.')

        url = 'https://api.github.com/repos/%s/%s/commits/%s' % (self.repo[0], self.repo[1], sha)

        session = requests.Session()
        session.auth = self.auth

        response = session.get(url)
        status_code = response.status_code
        if status_code != 200:
            raise ValueError('Could not get Github commits')
            # error_message = response.content
        commit = response.json()
        return commit

    def list(self, params={}):
        if self.auth is None:
            raise ValueError('Github auth credentials are not defined. Please provide username and password.')

        if self.repo is None:
            raise ValueError('Github repo information is not defined. Please provide repo owner and name.')

        url = 'https://api.github.com/repos/%s/%s/commits' % (self.repo[0], self.repo[1])

        session = requests.Session()
        session.auth = self.auth

        response = session.get(url, params=params)
        status_code = response.status_code
        if status_code != 200:
            raise ValueError('Could not get Github commits')
            # error_message = response.content
        commits = response.json()
        return commits
