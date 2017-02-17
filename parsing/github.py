###############################################################################
#                                                                             #
#                                GitHubHooks.py                               #
#                                   by Niols                                  #
#                                                                             #
#  BEERWARE License:                                                          #
#  <niols@niols.net> wrote this file. As long as you retain this notice you   #
#  can do whatever you want with this stuff. If we meet some day, and you     #
#  think this stuff is worth it, you can buy me a beer in return.             #
#                                                       –– Poul-Henning Kamp  #
#                                                                             #
###############################################################################

import warnings
from .common import ParserContext, UnknownKindWarning
from models import Project, Commit, Push, Issue, MergeRequest


def parse(header, hook):
    """
    The main parser.
    ``header`` and ``hook`` are respectively the header and the json body of
    Gtihub's POST request. They are both dictionaries.
    """
    ctxt = ParserContext()
    parse_project(ctxt, hook["repository"])
    kind = header.get("X-GitHub-Event")
    if kind == "push":
        ctxt.user = (hook["pusher"]["name"], hook["pusher"]["email"])
        return parse_push(ctxt, hook)
    elif kind == "issues":
        ctxt.user = (hook["sender"]["login"], None)
        return parse_issue(ctxt, hook)
    elif kind == "pull_request":
        ctxt.user = (hook["pull_request"]["user"]["login"], None)
        return parse_merge_request(ctxt, hook)
    else:
        warnings.warn(
            "Unknown GitHub event: {}".format(kind),
            UnknownKindWarning
        )


def parse_project(ctxt, hook):
    ctxt.project = Project(
        name=hook["name"],
        url=hook["url"]
    )


def parse_push(ctxt, hook):
    commits = [
        Commit(
            id=commit["id"],
            message=commit["message"],
            url=commit["url"],
            author=ctxt.get_or_create_user(
                commit["committer"]["name"],
                commit["committer"]["email"]
            )
        ) for commit in hook["commits"]
    ]
    return Push(
        branch=hook["ref"].split('/')[-1],
        commits=commits,
        url=hook["compare"],
        user=ctxt.user,
        project=ctxt.project
    )


def parse_issue(ctxt, hook):
    issue = hook["issue"]
    return Issue(
        user=ctxt.user,
        project=ctxt.project,
        id=issue["id"],
        title=issue["title"],
        action=hook["action"],
        url=issue["url"]
    )


def parse_merge_request(ctxt, hook):
    mr = hook["pull_request"]
    return MergeRequest(
        user=ctxt.user,
        project=ctxt.project,
        id=mr["id"],
        title=mr["title"],
        action=hook["action"],
        url=mr["html_url"],
    )
