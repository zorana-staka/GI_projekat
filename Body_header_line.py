"""
    This class represents the header line starting with #.
    The first eight fields CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO are mandatory.
    Besides these in file there can be one or more other fields.
    In this class we extract names as samples_names
"""
class Body_header_line:
    def __init__(self, line):
        self.line = line
        self.samples_names = []
        self.extract_sample_names()

    def extract_sample_names(self):
        splitted_line = self.line.split("\t")
        self.samples_names = splitted_line[8:]