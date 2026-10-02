from dataclasses import dataclass


@dataclass
class Pack:
    name: str
    # fields: dict
    methods: dict
    special_methods: dict


class PackInstance:

    def __init__(
        self,
        pack,
        properties
    ):
        self.pack: Pack = pack
        self.properties: dict = properties

    def get_property(self, name):

        if name in self.properties:
            return self.properties[name]

        method = self.pack.methods.get(name)

        if method:
            return (self, method)

        raise RuntimeError(
            f"Unknown property: {name}"
        )

    def __repr__(self):
        return f"{self.pack.name}"
