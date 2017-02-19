"""
This module performs the parsing of GitLab's hooks and internalizes them
using the classes described in ``models.py``.

The only function you should use is ``parse``, the others are called by
``parse`` depending on the entries.
"""

import warnings
from .common import ParserContext, UnknownKindWarning
from models import (
    Project, Push, Tag, Commit, Issue, MergeRequest, WikiPage, Wiki
)


def _preterit(action):
    if action in ["open"]:
        return "{}ed".format(action)
    elif action in ["update", "close", "create"]:
        return "{}d".format(action)


def parse(hook):
    """
    The main parser.
    The ``hook`` argument is the dictionary encoded as a json in Gitlab's POST
    request.
    """
    ctxt = ParserContext()
    kind = hook["object_kind"]
    if kind == "push":
        parse_project(ctxt, hook["project"])
        ctxt.user = (hook["user_name"], hook["user_email"])
        return parse_push(ctxt, hook)
    elif kind == "tag_push":
        parse_project(ctxt, hook["project"])
        ctxt.user = (hook["user_name"], None)
        return parse_tag(ctxt, hook)
    elif kind == "issue":
        parse_project(ctxt, hook["project"])
        ctxt.user = (hook["user"]["name"], None)
        return parse_issue(ctxt, hook)
    elif kind == "merge_request":
        parse_project(ctxt, hook["object_attributes"]["target"])
        ctxt.user = (hook["user"]["name"], None)
        return parse_merge_request(ctxt, hook)
    elif kind == "wiki_page":
        parse_project(ctxt, hook["project"])
        ctxt.user = (hook["user"]["name"], None)
        return parse_wiki(ctxt, hook)
    else:
        warnings.warn(
            "Unknown GitLab event: {}".format(kind),
            UnknownKindWarning
        )


def parse_project(ctxt, hook):
    ctxt.project = Project(
        name=hook["name"],
        url=hook["web_url"]
    )


def parse_push(ctxt, hook):
    # First generate the list of all commits
    commits = [
        Commit(
            id=commit["id"],
            message=commit["message"],
            url=commit["url"],
            author=ctxt.get_or_create_user(**commit["author"]),
        ) for commit in hook["commits"]
    ]
    return Push(
        branch=hook["ref"].split('/')[-1],
        commits=commits,
        url=(
            "{}/compare/{}...{}"
            .format(hook["project"]["web_url"],
                    hook["before"],
                    hook["after"])
        ),
        user=ctxt.user,
        project=ctxt.project,
    )


def parse_tag(ctxt, hook):
    return Tag(
        user=ctxt.user,
        project=ctxt.project,
        name=hook["ref"].split('/')[-1]
    )


def parse_issue(ctxt, hook):
    attrs = hook["object_attributes"]
    return Issue(
        user=ctxt.user,
        project=ctxt.project,
        id=attrs["id"],
        title=attrs["title"],
        action=_preterit(attrs["action"]),
        url=attrs["url"]
    )


def parse_merge_request(ctxt, hook):
    attrs = hook["object_attributes"]
    return MergeRequest(
        id=attrs["id"],
        title=attrs["title"],
        action=_preterit(attrs["action"]),
        url=attrs["url"],
        user=ctxt.user,
        project=ctxt.project
    )


def parse_wiki(ctxt, hook):
    page = hook["object_attributes"]
    page = WikiPage(
        name=page["slug"],
        title=page["title"],
        action=_preterit(page["action"]),
        url=page["url"]
    )
    return Wiki(
        user=ctxt.user,
        project=ctxt.project,
        pages=[page]
    )
