"""
This module performs the parsing of Gitlab's hooks and internalizes them
using the classes described in ``models.py``.
"""


from models import User, Project, Push, Tag, Commit, Issue, MergeRequest


class UnknownKindError(Exception):
    def __init__(self, kind):
        super().__init__("Unknown gitlab hook kind: {:s}".format(kind))


class ParserContext():
    def __init__(self, user=None, project=None):
        self._user = user
        self.users = dict()
        if self._user:
            self.users.append(self._user)

    def get_or_create_user(self, name, email):
        # We bet that every user has a different name
        if name in self.users:
            return self.users[name]
        else:
            user = User(name=name, email=email)
            self.users[name] = user
            return user

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        name, email = value
        user = User(name=name, email=email)
        self.users[name] = User(name=name, email=email)
        self._user = user


def parse(hook):
    """
    The main parser.
    The ``hook`` argument is the dictionary encoded as a json in Gitlab's POST
    request.
    """
    ctxt = ParserContext()
    kind = hook["object_kind"]
    if kind == "push":
        ctxt.project = Project(name=hook["project"]["name"])
        ctxt.user = (hook["user_name"], hook["user_email"])
        return parse_push(ctxt, hook)
    elif kind == "tag_push":
        ctxt.project = Project(name=hook["project"]["name"])
        ctxt.user = (hook["user_name"], None)
        return parse_tag(ctxt, hook)
    elif kind == "issue":
        ctxt.project = Project(name=hook["project"]["name"])
        ctxt.user = (hook["user"]["name"], None)
        return parse_issue(ctxt, hook)
    elif kind == "merge_request":
        ctxt.project = Project(
            name=hook["object_attributes"]["target"]["name"]
        )
        ctxt.user = (hook["user"]["name"], None)
        return parse_merge_request(ctxt, hook)
    else:
        raise UnknownKindError(kind)


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
        url="{}/compare/{}...{}"
            .format(hook["project"]["web_url"],
                    hook["before"],
                    hook["after"]),
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
        action=attrs["action"],
        url=attrs["url"]
    )


def parse_merge_request(ctxt, hook):
    attrs = hook["object_attributes"]
    return MergeRequest(
        id=attrs["id"],
        title=attrs["title"],
        action=attrs["action"],
        url=attrs["url"],
        user=ctxt.user,
        project=ctxt.project
    )