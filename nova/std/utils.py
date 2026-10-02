class Utils:

    def get_property(self, name):
        if (name == "toString"):
            return self.toString
        elif (name == "toInt"):
            return self.toInt
        elif (name == "toFloat"):
            return self.toFloat
        elif (name == "typeOf"):
            return self.typeOf
        raise RuntimeError(
            f"Unknown Property: {name}"
        )

    def toString(self, value):
        try:
            return str(value)
        except ValueError:
            raise RuntimeError(
                f"Cannot convert {value} to string"
            )

    def toInt(self, value):
        try:
            return int(value)
        except ValueError:
            if (type(value) == float):
                import math
                return math.floor(value)
            raise RuntimeError(
                f"Cannot convert {value} to int"
            )

    def toFloat(self, value):
        try:
            return float(value)
        except ValueError:
            raise RuntimeError(
                f"Cannot convert {value} to float"
            )

    def typeOf(self, value):
        return type(value).__name__
