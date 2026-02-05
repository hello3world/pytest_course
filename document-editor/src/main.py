class DocumentEditor:
    def __init__(self):
        self.content = ""
        self.history = []

    def write(self, text):
        self.history.append(self.content)
        self.content += text

    def clear(self):
        self.content = ""

    def is_empty(self):
        return self.content == ""

    def get_last_content(self):
        return self.history[-1]
