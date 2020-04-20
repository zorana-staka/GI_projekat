class Input_file:
    current_tag = ""

    def __init__(self, path):
        self.path = path
        self.has_current_tag = False
        self.header_read = False
        self.eof = False
        self.file = None
        self.next_tag = None

    def set_file(self, file):
        self.file = file

    def set_next_tag(self, next_tag):
        self.next_tag = next_tag

    def set_value_has_current_tag(self):
        self.has_current_tag = (self.current_tag == self.next_tag)