import unittest
import os
import json

from parsing.gitlab import parse as gitlab_parse
from parsing.github import parse as github_parse
from models import (Push, Tag, Issue, MergeRequest, Creation, Deletion,
                    WikiPage, Wiki)


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestParsing(unittest.TestCase):
    INPUTS = []

    @classmethod
    def setUpClass(cls):
        for attr, filename in cls.INPUTS:
            with open(os.path.join(DATA_DIR, filename), 'r') as file:
                hook = json.load(file)
                setattr(cls, attr, hook)


class TestGitlabParsing(TestParsing):
    INPUTS = [
        ("push", "gitlab/push.json"),
        ("creation", "gitlab/creation.json"),
        ("deletion", "gitlab/deletion.json"),
        ("tag", "gitlab/tag.json"),
        ("issue", "gitlab/issue.json"),
        ("merge_request", "gitlab/merge_request.json"),
        ("wiki", "gitlab/wiki.json"),
    ]

    def test_push(self):
        git_obj = gitlab_parse(self.push)
        self.assertIsInstance(git_obj, Push)
        self.assertEqual(git_obj.branch, "master")
        self.assertEqual(len(git_obj.commits), 2)
        self.assertTrue(
            -1
            < git_obj.url.find(git_obj.project.url)
            < git_obj.url.find(self.push["before"])
            < git_obj.url.find(self.push["after"])
        )

    def test_creation(self):
        git_obj = gitlab_parse(self.creation)
        self.assertIsInstance(git_obj, Creation)
        self.assertEqual(git_obj.branch, "new")
        self.assertEqual(len(git_obj.commits), 2)
        self.assertTrue(
            -1
            < git_obj.url.find(git_obj.project.url)
            < git_obj.url.find("master")
            < git_obj.url.find(self.push["after"])
        )

    def test_deletion(self):
        git_obj = gitlab_parse(self.deletion)
        self.assertIsInstance(git_obj, Deletion)
        self.assertEqual(git_obj.branch, "deleted")

    def test_tag(self):
        git_obj = gitlab_parse(self.tag)
        self.assertIsInstance(git_obj, Tag)
        self.assertEqual(git_obj.tag_name, "v1.0.0")

    def test_issue(self):
        git_obj = gitlab_parse(self.issue)
        self.assertIsInstance(git_obj, Issue)
        self.assertEqual(git_obj.id, 23)
        self.assertEqual(git_obj.title, "New API: create/update/delete file")
        self.assertEqual(git_obj.action, "opened")
        self.assertEqual(git_obj.url, "http://example.com/diaspora/issues/23")

    def test_merge_request(self):
        git_obj = gitlab_parse(self.merge_request)
        self.assertIsInstance(git_obj, MergeRequest)
        self.assertEqual(git_obj.id, 1)
        self.assertEqual(git_obj.title, "MS-Viewport")
        self.assertEqual(git_obj.action, "opened")
        self.assertEqual(
            git_obj.url,
            "http://example.com/diaspora/merge_requests/1"
        )

    def test_wiki(self):
        git_obj = gitlab_parse(self.wiki)
        self.assertIsInstance(git_obj, Wiki)
        self.assertEqual(len(git_obj.wiki_pages), 1)
        page = git_obj.wiki_pages[0]
        self.assertIsInstance(page, WikiPage)
        self.assertEqual(page.page_name, "awesome")
        self.assertEqual(page.title, "Awesome")
        self.assertEqual(page.action, "created")
        self.assertEqual(
            page.url,
            "http://example.com/root/awesome-project/wikis/awesome"
        )


class TestGithubParsing(TestParsing):
    INPUTS = [
        ("push", "github/push.json"),
        ("creation", "github/creation.json"),
        ("deletion", "github/deletion.json"),
        ("issue", "github/issue.json"),
        ("merge_request", "github/merge_request.json"),
        ("wiki", "github/wiki.json"),
    ]

    def test_push(self):
        git_obj = github_parse(
            {"X-GitHub-Event": "push"},
            self.push
        )
        self.assertIsInstance(git_obj, Push)
        self.assertEqual(git_obj.branch, "changes")
        self.assertEqual(
            git_obj.url,
            "https://github.com/baxterthehacker/public-repo/compare/"
            "9049f1265b7d...0d1a26e67d8f"
        )
        self.assertEqual(len(git_obj.commits), 1)

    def test_creation(self):
        git_obj = github_parse(
            {"X-GitHub-Event": "create"},
            self.creation
        )
        self.assertIsInstance(git_obj, Creation)
        self.assertEqual(git_obj.branch, "new")
        self.assertEqual(
            git_obj.url,
            "https://github.com/baxterthehacker/public-repo/tree/new"
        )

    def test_deletion(self):
        git_obj = github_parse(
            {"X-GitHub-Event": "delete"},
            self.deletion
        )
        self.assertIsInstance(git_obj, Deletion)
        self.assertEqual(git_obj.branch, "deleted")

    def test_issue(self):
        git_obj = github_parse(
            {"X-GitHub-Event": "issues"},
            self.issue
        )
        self.assertIsInstance(git_obj, Issue)
        self.assertEqual(git_obj.id, 73464126)
        self.assertEqual(git_obj.title, "Spelling error in the README file")
        self.assertEqual(git_obj.action, "opened")
        self.assertEqual(
            git_obj.url,
            "https://api.github.com/repos/baxterthehacker/public-repo/issues/2"
        )

    def test_merge_request(self):
        git_obj = github_parse(
            {"X-GitHub-Event": "pull_request"},
            self.merge_request
        )
        self.assertIsInstance(git_obj, MergeRequest)
        self.assertEqual(git_obj.id, 34778301)
        self.assertEqual(
            git_obj.title,
            "Update the README with new information"
        )
        self.assertEqual(git_obj.action, "opened")
        self.assertEqual(
            git_obj.url,
            "https://github.com/baxterthehacker/public-repo/pull/1"
        )

    def test_wiki(self):
        git_obj = github_parse(
            {"X-GitHub-Event": "gollum"},
            self.wiki
        )
        self.assertIsInstance(git_obj, Wiki)
        self.assertEqual(len(git_obj.wiki_pages), 1)
        page = git_obj.wiki_pages[0]
        self.assertIsInstance(page, WikiPage)
        self.assertEqual(page.title, "Home")
        self.assertEqual(page.page_name, "Home")
        self.assertEqual(page.action, "created")
