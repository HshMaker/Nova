class Text:
    selectedFile = ""

    def get_property(self, name):
        if (name == "select"):
            return self.select
        elif (name == "readAll"):
            return self.readAll

    def select(self, fileName):
        self.selectedFile = open(fileName, 'r', encoding='utf-8')

    def readAll(self):
        return self.selectedFile.read()
