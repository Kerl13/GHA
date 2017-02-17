###############################################################################
#                                                                             #
#                                GitLabHooks.py                               #
#                                   by Niols                                  #
#                                                                             #
#  BEERWARE License:                                                          #
#  <niols@niols.net> wrote this file. As long as you retain this notice you   #
#  can do whatever you want with this stuff. If we meet some day, and you     #
#  think this stuff is worth it, you can buy me a beer in return.             #
#                                                       –– Poul-Henning Kamp  #
#                                                                             #
###############################################################################


"""
This module describes the internal representations of Gitlab's hooks.
"""


from writer.common import RichTextMixin, RichTextList


# ---
# Base objects
# ---


class User():
    def __init__(self, name="unknown", email="unknown"):
        self.name = name
        self.email = email

    def __str__(self):
        return self.name


class Project():
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __str__(self):
        return self.name


class Commit(RichTextMixin):
    TEMPLATE = "{id} {author}: {message}"

    def __init__(self, id, message, url, author):
        self.id = id
        self.message = message
        self.url = url
        self.author = author


class Event():
    def __init__(self, user, project):
        self.user = user
        self.project = project


# ---
# The available hooks
# ---


class Push(Event, RichTextMixin):
    TEMPLATE = (
        "[{project}] {user} pushed {nb} commits to {branch}. ({url})\n"
        "{commits}"
    )

    def __init__(self, branch, commits, url, **kwargs):
        Event.__init__(self, **kwargs)
        self.branch = branch
        self.commits = RichTextList(commits)
        self.url = url

    def get_context(self):
        context = RichTextMixin.get_context(self)
        context["nb"] = len(self.commits)
        return context


class Tag(Event, RichTextMixin):
    TEMPLATE = "[{project}] {user} added the tag {tag_name}"

    def __init__(self, name, **kwargs):
        Event.__init__(self, **kwargs)
        self.tag_name = name


class Issue(Event, RichTextMixin):
    TEMPLATE = (
        "[{project}] {user} {action} issue #{id}: {title}. ({url})"
    )

    def __init__(self, id, title, action, url, **kwargs):
        Event.__init__(self, **kwargs)
        self.id = id
        self.title = title
        self.action = action
        self.url = url


class MergeRequest(Event, RichTextMixin):
    TEMPLATE = (
        "[{project}] {user} {action} merge request !{id}: {title}. ({url})"
    )

    def __init__(self, id, title, action, url, **kwargs):
        Event.__init__(self, **kwargs)
        self.id = id
        self.title = title
        self.action = action
        self.url = url
