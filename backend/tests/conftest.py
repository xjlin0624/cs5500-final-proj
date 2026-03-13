class FakeResult:
    def __init__(self, values):
        if isinstance(values, list):
            self._values = values
        elif values is None:
            self._values = []
        else:
            self._values = [values]

    def scalars(self):
        return self

    def all(self):
        return list(self._values)

    def scalar_one_or_none(self):
        return self._values[0] if self._values else None


class FakeSession:
    def __init__(self, values=None):
        self._values = values
        self.added = []
        self.committed = False
        self.rolled_back = False

    def execute(self, _stmt):
        return FakeResult(self._values)

    def add(self, value):
        self.added.append(value)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True
