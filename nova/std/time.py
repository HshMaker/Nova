class Time:

    def get_property(self, name):
        if (name == "now"):
            return self.now

    def now(self):
        import time

        return int(time.time())
