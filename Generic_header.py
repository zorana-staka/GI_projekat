"""
    Represents line in header part of VCF file.
"""
class Generic_header:
    def __init__(self, line):
        self.line = line
        self.data = {}
        self.extract_line_data()

    def extract_line_data(self):

        try:
            line_parse = self.line.split('=',1)[1]
            attributes = line_parse.split(',')
            for item in attributes:
                if item.count('=') >= 1:
                    splitted = item.split('=', 1)
                    self.data[splitted[0].lstrip('<,"')] = splitted[1].rstrip('>')
        except:
            pass

    def __eq__(self, other):
        return self.line == other.line

    def get_line(self):
        return self.line