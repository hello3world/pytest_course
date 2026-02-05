class DocumentEditor:
    def __init__(self):
        self.content = ""
        self.history = []

    def write(self, text):
        self.history.append(self.content)
        self.content += text

    def clear(self):
        self.history.append(self.content)
        self.content = ""

    def is_empty(self):
        return self.content == ""

    def get_last_content(self):
        if len(self.history) == 0:
            raise ValueError(
                """Content is empty, 
                no previous operations 
                were done""")
        return self.history[-1]
