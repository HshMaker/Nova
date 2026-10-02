class Module:

    def __init__(
        self,
        exports
    ):
        self.exports: dict = exports

    def get_property(self, name):
        if name in self.exports:
            return self.exports[name]
        raise RuntimeError(
            f"Unknown Property: {name}"
        )
