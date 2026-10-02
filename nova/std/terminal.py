class Terminal:

    def get_property(self, name):
        if (name == "log"):
            return self.log
        elif (name == "warn"):
            return self.warn
        elif (name == "err"):
            return self.err
        elif (name == "write"):
            return self.write
        elif (name == "clear"):
            return self.clear

        raise RuntimeError(
            f"Unknown Property: {name}"
        )

    def log(self, *text):
        output = " ".join(
            str(item)
            for item in text
        )
        print(f"\033[0m{output}")

    def warn(self, *text):
        output = " ".join(
            str(item)
            for item in text
        )
        print(f"\033[33m[WARN] {output}\033[0m")

    def err(self, text):
        output = " ".join(
            str(item)
            for item in text
        )
        print(f"\033[31m[ERROR] {output}\033[0m")

    def write(self, text=""):
        return input(text)

    def clear(self):
        print("\033[2J\033[H", end="")
