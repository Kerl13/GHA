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
        template = self.get_template()
        context = self.get_context()
        for key, value in context.items():
            if key in CONFIG:
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
