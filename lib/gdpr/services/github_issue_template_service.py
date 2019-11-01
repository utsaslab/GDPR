import json
import os
import sys
import platform
from ..services.py_line_inspector_service import py_line_inspector_service
from ..services.github_permalink_service import github_permalink_service
from ..policies.github_issue_title_policy import GithubIssueTitlePolicy

class GithubIssueTemplateService():
    def dpa_html_reachability_issue(self, dpa, reachability, commit=None):
        name = dpa.name
        country = dpa.country

        source = dpa.sources[0]
        host = source['host']
        start_path = source['start_path']

        body = ""

        body += "Issue tracker is **ONLY** used for reporting bugs. New features should be discussed on our slack channel. Please use [stackoverflow](https://stackoverflow.com) for supporting issues.\n\n"

        body += "## Expected Behavior\n\n"
        body += f"The DPA was expected to get the docs from the source: {host}{start_path}\n"

        body += "## Current Behavior\n"
        body += f"The docs, of the DPA in question, is no longer reachable due to changes in the html source structure.\n"

        body += "## Possible Solution\n"
        body += "To reflect the changes of the html source structure in the DPA's source code, human analysis is needed."
        body += " **Take a look at the *failed* XPath sample tests to get an idea of what element needs to get changed.**\n\n"

        body += "## Steps to Reproduce\n"
        body += "1. Get instance of gdpr class.\n"
        body += f"2. Get instance of dpa class for eu member: {country}.\n"
        body += "3. Check if important dpa html elements are reachable through service.\n"
        body += "4. Given the reachability output from step 3., check if there's any reachability_flag set to 0 for any of the XPaths.\n"
        body += "5. Lastly, following step 4., if there's a reachability_flag set to 0, the dpa cannot get the docs.\n"

        body += "## Context (Environment)\n"
        body += "Python Version:\t%s.%s.%s\n" % (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
        body += "Platform:\t%s %s\n" % (platform.system(), platform.release())

        body += "## Detailed Description\n"
        body += "#### XPath sample tests:\n"
        for iso_code, xpath, label, reachability_flag in reachability:
            body += "- [PASS] " if reachability_flag == 1 else "- [FAIL] "
            body += f"{xpath} ({label})\n"
        lines = py_line_inspector_service(f"./gdpr/dpa/" + country.lower() + "/__init__.py", 'def', 'get_docs') # country.lower()
        if lines != (-1, -1) and commit != None:
            sha = commit['sha']

            permalink = github_permalink_service(
                        repo_owner=os.environ['gh-repo-owner'],
                        repo_name=os.environ['gh-repo-name'],
                        commit_id=sha,
                        project_path='lib/gdpr/dpa/' + country.lower() + '/__init__.py',
                        start_line=lines[0],
                        end_line=lines[1]
                    )
            body += "\n"
            body += "#### DPA source code:\n"
            body += permalink
        body += "\n"

        body += "#### Learn more:\n"
        body += "**What is XPath?**\n"
        body += "> XPath can be used to navigate through elements and attributes in an XML document. XPath uses path expressions to select nodes or node-sets in an XML document. These path expressions look very much like the path expressions you use with traditional computer file systems.\n"
        body += "> Source: [w3schools](https://www.w3schools.com/xml/xpath_intro.asp)\n\n"
        body += "We use XPath to sample test if certain elements are reachable from the DPA's html source structure."
        body += " If important elements are no longer reachable, the source code of the DPA will not be able to get the docs."

        # body += "## Possible Implementation\n"

        gh_issue_title_policy = GithubIssueTitlePolicy()
        title = gh_issue_title_policy.dpa_html_reachability_title(dpa)
        labels = ['bug', 'help wanted']

        assignees = []
        if commit != None:
            committer = commit['committer']['login']
            assignees.append(committer)

        issue = {
            'title': title,
            'body': body,
            'labels': labels,
            'assignees': assignees
        }
        return issue
