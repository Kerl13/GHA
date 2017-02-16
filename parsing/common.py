from models import User


class UnknownKindError(Exception):
    def __init__(self, source, kind):
        super().__init__(
            "Unknown {:s} hook kind: {:s}"
            .format(source, kind)
        )


class ParserContext():
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
