class Array:

    def __init__(self, elements, element_type="any"):
        self.elements: list = elements
        self.element_type = element_type

    def get_property(self, name):
        if (name == "push"):
            return self.push
        elif (name == "pull"):
            return self.pull
        elif (name == "clear"):
            return self.clear
        elif (name == "length"):
            return self.length
        elif (name == "sort"):
            return self.sort
        raise RuntimeError(
            f"Unknown Property: {name}"
        )

    def push(self, value):
        self.elements.append(value)
        return value

    def pull(self, index):
        return self.elements.pop(index)

    def clear(self):
        self.elements.clear()

    def length(self):
        return len(self.elements)

    def sort(self, reversed=False):
        self.elements.sort(reverse=reversed)
        return "null"

    def __str__(self):

        result = [x for x in self.elements]

        return str(result)

    __repr__ = __str__
