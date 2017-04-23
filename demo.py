import os
import json

from parsing.gitlab import parse as gitlab_parse
from parsing.github import parse as github_parse

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "tests",
    "data"
)

GITLAB_INPUTS = [
    ("push", "push.json"),
    ("tag", "tag.json"),
    ("issue", "issue.json"),
    ("merge_request", "merge_request.json"),
    ("create", "creation.json"),
    ("delete", "deletion.json"),
]

GITHUB_INPUTS = [
    ("push", "push.json"),
    ("issues", "issue.json"),
    ("pull_request", "merge_request.json"),
    ("create", "creation.json"),
    ("delete", "deletion.json"),
]


def demo_from_inputs(namespace, inputs, parser):
    for name, filename in inputs:
        data = None
        with open(os.path.join(DATA_DIR, namespace, filename), "r") as file:
            data = json.load(file)
        print("=> {}".format(name))
        git_obj = parser(name, data)
        print(git_obj.render_simple(), end="\n\n")


if __name__ == "__main__":
    # GitLab
    print("====================")
    print("=== GitLab Hooks ===")
    print("====================")
    print("")
    demo_from_inputs(
        "gitlab",
        GITLAB_INPUTS,
        lambda name, hook: gitlab_parse(hook)
    )

    # GitHub
    print("====================")
    print("=== GitHub Hooks ===")
    print("====================")
    print("")
    demo_from_inputs(
        "github",
        GITHUB_INPUTS,
        lambda name, hook: github_parse({"X-GitHub-Event": name}, hook)
    )
