"""
Parsing tools
"""

from models import User


class UnknownKindWarning(Warning):
    """
    Warning raised when the parser cannot identify the event described by the
    hook.
    """
    pass


class UnknownActionWarning(Warning):
    """
    Warning raised when the parser cannot conjugate an action.
    """
    pass


class ParserContext():
    """
    This class stores
    - The list of known users
    - The user at the origin of the event
    - The project involved
    """
    def __init__(self, user=None, project=None):
        self._user = user
        self.users = dict()
        if self._user:
            self.users.append(self._user)

    def get_or_create_user(self, name, email):
        # We bet that every user has a different name
        if name in self.users:
            return self.users[name]
        else:
            user = User(name=name, email=email)
            self.users[name] = user
            return user

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        name, email = value
        user = User(name=name, email=email)
        self.users[name] = User(name=name, email=email)
        self._user = user
