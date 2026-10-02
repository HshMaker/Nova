class NextException(Exception):
    pass


class OutException(Exception):
    pass


class ReturnException(Exception):
    def __init__(self, value):
        self.value = value
