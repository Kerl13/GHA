"""
TODO
"""

import unittest

from models import (
    Project, User, Push, Commit, Tag, Issue, MergeRequest, WikiPage, Wiki
)


class TestSimpleRendering(unittest.TestCase):
    def setUp(self):
        self.project = Project(name="My Project",
                               url="http://example.com/project")
        self.user = User(name="Mrs Foobar", email="dev@foobar.net")

    def test_push(self):
        commits = [Commit(id="1d8d58ec4c8865394cd5ff91ce8e54b1d598346f",
                          message="Fix py2 compat",
                          url="http://example.com/project/commit/...",
                          author=self.user)]
        push = Push(
            user=self.user,
            project=self.project,
            branch="hotfix/Issue214",
            commits=commits,
            url="too long don't write"
        )
        self.assertEqual(
            push.render_simple(),
            "[My Project] Mrs Foobar pushed 1 commits to hotfix/Issue214. "
            "(too long don't write)\n"
            "1d8d58e Mrs Foobar: Fix py2 compat"
        )

    def test_tag(self):
        tag = Tag(name="v2", user=self.user, project=self.project)
        self.assertEqual(
            tag.render_simple(),
            "[My Project] Mrs Foobar added the tag v2"
        )

    def test_issue(self):
        issue = Issue(
            user=self.user,
            project=self.project,
            id=42,
            title="Wrong encoding",
            action="opened",
            url="http://bugtracker.example.com/issue/42"
        )
        self.assertEqual(
            issue.render_simple(),
            "[My Project] Mrs Foobar opened issue #42: Wrong encoding. "
            "(http://bugtracker.example.com/issue/42)"
        )

    def test_merge_request(self):
        mr = MergeRequest(
            user=self.user,
            project=self.project,
            id=5,
            title="Use utf-8",
            action="updated",
            url="http://example.com/project/mr/5"
        )
        self.assertEqual(
            mr.render_simple(),
            "[My Project] Mrs Foobar updated merge request !5: Use utf-8. "
            "(http://example.com/project/mr/5)"
        )

    def test_wiki(self):
        pages = [
            WikiPage(
                name="home",
                title="Home page of my project's wiki",
                action="created",
                url="example.com/wiki/home"
            )
        ]
        wiki = Wiki(
            user=self.user,
            project=self.project,
            pages=pages
        )
        self.assertEqual(
            wiki.render_simple(),
            "[My Project] Mrs Foobar updated the wiki\n"
            "created page home: Home page of my project's wiki. "
            "(example.com/wiki/home)"
        )
