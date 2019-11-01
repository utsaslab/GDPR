import os
import json
import requests

class GithubIssueFactory():
    def __init__(self, auth=None, repo=None):
        self.auth = auth
        self.repo = repo

    def set_auth(self, username, password):
        self.auth = (username, password)

    def set_repo(self, owner, name):
        self.repo = (owner, name)

    def create(self, title, body=None, milestone=None, labels=[], assignees=[]):
        if self.auth is None:
            raise ValueError('Github auth credentials are not defined. Please provide username and password.')

        if self.repo is None:
            raise ValueError('Github repo information is not defined. Please provide repo owner and name.')

        url = 'https://api.github.com/repos/%s/%s/issues' % (self.repo[0], self.repo[1])

        session = requests.Session()
        session.auth = self.auth

        issue = {
            'title': title,
            'body': body,
            'milestone': milestone,
            'labels': labels,
            'assignees': assignees
        }
        response = session.post(url, json.dumps(issue))

        status_code = response.status_code
        if status_code != 201:
            raise ValueError('Could not create Github Issue with title: "%s"' % title)
            #error_message = response.content

        return issue
