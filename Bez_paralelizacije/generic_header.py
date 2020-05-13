class Generic_header:
    """ Represents line in header of VCF file.
        Contains all relevant information about line and methods for manipulation.
    """
    def __init__(self, line):
        self.line = line
        self.tag = ""
        self.ID = None
        self.tag_and_ID = ""
        self.data = {}
        self.extract_line_data()

    def extract_line_data(self):
        """ If possible divides line into two parts at the place of = (equal sign).
            Sets ID and tag name.
        """
        try:
            line_parse = self.line.split('=', 1)
            self.tag = (line_parse[0])[2:]
            attributes = line_parse[1].split(',')
            for item in attributes:
                if item.count('=') >= 1:
                    splitted = item.split('=', 1)
                    self.data[splitted[0].lstrip('<,"')] = splitted[1].rstrip('>')

            if 'ID' in self.data:
                self.ID = self.data['ID']
                self.tag_and_ID = f'{self.tag}_{self.ID}'

        finally:
            pass

    def __eq__(self, other):
        """ Overridden equal operator. Compering is done by line attribute.
            :param other: other Generic_header to be compared with.
        """
        return self.line == other.line

