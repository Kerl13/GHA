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
        return self._get_template().format(**self.get_context())

    def render_irccolors(self):
        template = self._get_template()
        context = self.get_context()
        for key, value in context.items():
            if key in CONFIG:
                # XXX: should be optional
                if key == "url":
                    value = shorten_url(value)
                context[key] = C(value, CONFIG[key])
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


def shorten_url(url):
    short_url = requests.get(
        "http://is.gd/create.php",
        {"format": "simple", "url": url}
    )
    return short_url.content.decode("utf-8")
