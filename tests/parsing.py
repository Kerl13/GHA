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

    def test_tag(self):
        git_obj = parse(self.tag)
        self.assertIsInstance(git_obj, Tag)

    def test_issue(self):
        git_obj = parse(self.issue)
        self.assertIsInstance(git_obj, Issue)

    def test_merge_request(self):
        git_obj = parse(self.merge_request)
        self.assertIsInstance(git_obj, MergeRequest)
