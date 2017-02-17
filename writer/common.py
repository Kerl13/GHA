import requests
import warnings
from .irc import Color as C, CONFIG


class RichTextError(Exception):
    pass


class RichTextMixin():
    """
    TODO: explain
    """
    TEMPLATE = ""

    def render_simple(self):
        template = self._get_template()
        context = self.get_context()
        for key, value in context.items():
            if isinstance(value, RichTextList):
                context[key] = value.render_simple()
        return template.format(**context)

    def render_irccolors(self):
        template = self._get_template()
        context = self.get_context()
        for key, value in context.items():
            if key in CONFIG:
                # XXX: should be optional
                if key == "url":
                    context[key] = C(shorten_url(value), CONFIG[key])
                elif isinstance(value, RichTextList):
                    context[key] = value.render_irccolors()
                else:
                    pass
            else:
                warnings.warn(
                    "No config option for keyword \{{key}\}",
                    RuntimeWarning
                )
        return template.format(**context)

    def _get_template(self):
        if not self.TEMPLATE:
            raise RichTextError("No template provided")
        else:
            return self.TEMPLATE

    def get_context(self):
        return self.__dict__


class RichTextList():
    def __init__(self, lines):
        assert isinstance(lines, list)
        if lines:
            assert isinstance(lines[0], RichTextMixin)
        self.lines = lines

    # ---
    # These methods reproduce the behaviour of a list
    # ---

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, key):
        return self.lines[key]

    # ---
    # These methods define how the list should be displayed.
    # This is the "RichText" part of the class.
    # ---

    def render_simple(self):
        return "\n".join([
            line.render_simple() for line in self.lines
        ])

    def render_irccolors(self):
        return "\n".join([
            line.render_irccolors() for line in self.lines
        ])


def shorten_url(url):
    short_url = requests.get(
        "http://is.gd/create.php",
        {"format": "simple", "url": url}
    )
    return short_url.content.decode("utf-8")
