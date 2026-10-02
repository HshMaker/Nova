class Object:
    def __init__(self, properties=None):
        self.properties = properties or {}

    def get_property(self, name):
        if (name in self.properties):
            return self.properties[name]

    def __str__(self):
        return str(self.properties)

    __repr__ = __str__
