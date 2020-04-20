class Generic_header_object:
    def __init__(self, line, tag):
        self.line = line
        self.tag = tag
        self.data = {}
        self.extract_line_data()

    def extract_line_data(self):

        try:
            line_parse = self.line[len(self.tag) + 3: -1]
            attributes = line_parse.split(',')
            for item in attributes:
                if item.count('=') >= 1:
                    splitted = item.split('=', 1)
                    self.data[splitted[0].lstrip('<,"')] = splitted[1].rstrip('>')
        except:
            pass

    def __eq__(self, other):
        return self.line == other.line