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


class Project(RichTextMixin):
    TEMPLATE = "[{name}]"

    def __init__(self, name, url):
        self.name = name
        self.url = url


class Commit(RichTextMixin):
    TEMPLATE = "{id} {author}: {message}"

    def __init__(self, id, message, url, author):
        assert isinstance(author, User)
        self.id = id
        self.message = message
        self.url = url
        self.author = author

    def get_context(self):
        context = RichTextMixin.get_context(self)
        context["id"] = context["id"][:7]
        context["message"] = context["message"].split('\n')[0]
        return context


class Event():
    def __init__(self, user, project):
        assert isinstance(user, User)
        assert isinstance(project, Project)
        self.user = user
        self.project = project


# ---
# The available hooks
# ---


class PushEvent(Event, RichTextMixin):
    def __init__(self, branch, commits, url, **kwargs):
        assert isinstance(commits, list)
        assert all(isinstance(commit, Commit) for commit in commits)
        Event.__init__(self, **kwargs)
        self.branch = branch
        self.commits = RichTextList(commits)
        self.url = url

    def get_context(self):
        context = RichTextMixin.get_context(self)
        context["commits"] = context["commits"][-5:]
        context["nb"] = len(self.commits)
        return context


class Push(PushEvent, RichTextMixin):
    TEMPLATE = (
        "{project} {user} pushed {nb} commits to {branch}. ({url})\n"
        "{commits}"
    )


class Creation(PushEvent, RichTextMixin):
    TEMPLATE = (
        "{project} {user} created branch {branch} with {nb} commits. ({url})\n"
        "{commits}"
    )



class Tag(Event, RichTextMixin):
    TEMPLATE = "{project} {user} added the tag {tag_name}"

    def __init__(self, name, **kwargs):
        Event.__init__(self, **kwargs)
        self.tag_name = name


class Issue(Event, RichTextMixin):
    TEMPLATE = (
        "{project} {user} {action} issue #{id}: {title}. ({url})"
    )

    def __init__(self, id, title, action, url, **kwargs):
        Event.__init__(self, **kwargs)
        self.id = id
        self.title = title
        self.action = action
        self.url = url


class MergeRequest(Event, RichTextMixin):
    TEMPLATE = (
        "{project} {user} {action} merge request !{id}: {title}. ({url})"
    )

    def __init__(self, id, title, action, url, **kwargs):
        Event.__init__(self, **kwargs)
        self.id = id
        self.title = title
        self.action = action
        self.url = url


class Deletion(Event, RichTextMixin):
    TEMPLATE = (
        "{project} {user} deleted branch {branch}."
    )

    def __init__(self, branch, **kwargs):
        Event.__init__(self, **kwargs)
        self.branch = branch

# ---
# Wiki related models
# ---


class WikiPage(RichTextMixin):
    TEMPLATE = "{action} page {page_name}: {title}. ({url})"

    def __init__(self, name, title, action, url):
        self.page_name = name
        self.title = title
        self.action = action
        self.url = url


class Wiki(Event, RichTextMixin):
    TEMPLATE = "{project} {user} updated the wiki\n{wiki_pages}"

    def __init__(self, pages, **kwargs):
        Event.__init__(self, **kwargs)
        self.wiki_pages = RichTextList(pages)
