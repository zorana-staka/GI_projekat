class Info_field:
    def __init__(self, header_line):
        self.id = ""
        self.type = ""
        self.value = None
        self.header_line = header_line
        self.extract_values_from_header_line()

    def extract_values_from_header_line(self):
        # TODO naći vrijednosti za ID i Type
        pass