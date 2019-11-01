import os
import json
from ..repositories.github_issue_repository import GithubIssueRepository
from ..policies.github_issue_title_policy import GithubIssueTitlePolicy

def is_satisfied_by(dpa):
    satisfied = True

    gh_issue_repository = GithubIssueRepository()
    gh_issue_repository.set_auth(username=os.environ['gh-username'], password=os.environ['gh-password'])
    gh_issue_repository.set_repo(owner=os.environ['gh-repo-owner'], name=os.environ['gh-repo-name'])
    open_issues = gh_issue_repository.for_state('open')

    gh_issue_title_policy = GithubIssueTitlePolicy()
    title = gh_issue_title_policy.dpa_html_reachability_title(dpa)

    for issue in open_issues:
        cand_title = issue['title']

        """key_matches = 0
        for key in keywords:
            if key in title:
                key_matches += 1"""

        """if key_matches == len(keywords):
            satisfied = False
            break"""
        if title == cand_title:
            satisfied = False
            break

    return satisfied
