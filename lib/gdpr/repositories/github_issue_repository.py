import os
import requests
import json

class GithubIssueRepository():
    def __init__(self, auth=None, repo=None):
        self.auth = auth
        self.repo = repo

    def set_auth(self, username, password):
        self.auth = (username, password)

    def set_repo(self, owner, name):
        self.repo = (owner, name)

    def for_id(self, issue_number, params={}):
        if self.auth is None:
            raise ValueError('Github auth credentials are not defined. Please provide username and password.')

        if self.repo is None:
            raise ValueError('Github repo information is not defined. Please provide repo owner and name.')

        url = 'https://api.github.com/repos/%s/%s/issues/%s' % (self.repo[0], self.repo[1], issue_number)

        session = requests.Session()
        session.auth = self.auth

        response = session.get(url, params=params)
        status_code = response.status_code
        if status_code != 200:
            raise ValueError('Could not get Github issue')
            # error_message = response.content
        issues = response.json()
        return issues

    def for_state(self, state, params={}):
        if state != 'open' and state != 'closed':
            raise ValueError('State is not defined. Should be either open or closed.')

        if self.auth is None:
            raise ValueError('Github auth credentials are not defined. Please provide username and password.')

        if self.repo is None:
            raise ValueError('Github repo information is not defined. Please provide repo owner and name.')

        url = 'https://api.github.com/repos/%s/%s/issues?state=%s' % (self.repo[0], self.repo[1], state)

        session = requests.Session()
        session.auth = self.auth

        response = session.get(url, params=params)
        status_code = response.status_code
        if status_code != 200:
            raise ValueError('Could not get Github issue')
            # error_message = response.content
        issues = response.json()
        return issues
