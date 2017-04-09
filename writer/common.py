"""
This module contains some utilities for outputing text.

The ``RichTextMixin`` does the major part of the work: to be able to display
something, you have to make it inherit from this mixin. The different available
output formats correspond to the ``render_*`` methods.
"""

import requests
import warnings
from .irc import Color as C, CONFIG


class RichTextError(Exception):
    """
    This error is raised when something goes wrong in RichTextMixin.
    """
    pass


class RichTextMixin():
    """
    ``RichTextMixin`` adds rendering methods to an object.

    To make it work you have to set a class variable called ``TEMPLATE``. It
    must be a string containing tags like ``{user}`` (this is basically because
    we use the ``.format`` function) where each tag has to correspond to a key
    of the dictionary ``self.get_context()``.
    By default, ``get_context`` will return ``self.__dict__``. If you want to
    add some stuff to the context, you have to override this method.
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
        """
        The same output as ``render_simple`` with some colorization for IRC.

        See the writer.irc module for details.
        """
        template = self._get_template()
        context = self.get_context()
        for key, value in context.items():
            if key in CONFIG:
                # XXX: should be optional
                if key == "url":
                    context[key] = C(shorten_url(value), CONFIG[key])
                else:
                    context[key] = C(value, CONFIG[key])
            else:
                warnings.warn(
                    "No config option for keyword \{{key}\}",
                    RuntimeWarning
                )
            if isinstance(value, RichTextList):
                context[key] = value.render_irccolors()
        return template.format(**context)

    def _get_template(self):
        if not self.TEMPLATE:
            raise RichTextError("No template provided")
        else:
            return self.TEMPLATE

    def get_context(self):
        """
        This method is called by the ``render_*`` methods to get the context
        they will use to fill the template.

        You have to override it in order to alter the rendering context.
        """
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
