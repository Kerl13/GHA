import unittest
import os
import json

from parsing.gitlab import parse
from models import Push, Tag, Issue, MergeRequest


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestGitlabParsing(unittest.TestCase):
    INPUTS = [
        ("push", "push.json"),
        ("tag", "tag.json"),
        ("issue", "issue.json"),
        ("merge_request", "merge_request.json"),
    ]

    def setUp(self):
        for attr, filename in self.INPUTS:
            with open(os.path.join(DATA_DIR, filename), 'r') as file:
                hook = json.load(file)
                setattr(self, attr, hook)

    def test_push(self):
        git_obj = parse(self.push)
        self.assertIsInstance(git_obj, Push)
        self.assertEqual(git_obj.branch, "master")
        self.assertEqual(len(git_obj.commits), 2)
        self.assertTrue(
            -1
            < git_obj.url.find(git_obj.project.url)
            < git_obj.url.find(self.push["before"])
            < git_obj.url.find(self.push["after"])
        )

    def test_tag(self):
        git_obj = parse(self.tag)
        self.assertIsInstance(git_obj, Tag)
        self.assertEqual(git_obj.tag_name, "v1.0.0")

    def test_issue(self):
        git_obj = parse(self.issue)
        self.assertIsInstance(git_obj, Issue)
        self.assertEqual(git_obj.id, 301)
        self.assertEqual(git_obj.title, "New API: create/update/delete file")
        self.assertEqual(git_obj.action, "open")
        self.assertEqual(git_obj.url, "http://example.com/diaspora/issues/23")

    def test_merge_request(self):
        git_obj = parse(self.merge_request)
        self.assertIsInstance(git_obj, MergeRequest)
        self.assertEqual(git_obj.id, 99)
        self.assertEqual(git_obj.title, "MS-Viewport")
        self.assertEqual(git_obj.action, "open")
        self.assertEqual(
            git_obj.url,
            "http://example.com/diaspora/merge_requests/1"
        )
