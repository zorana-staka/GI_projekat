"""
    This class represents the header line starting with #.
    The first eight fields CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO are mandatory.
    Besides these in file there can be one or more other fields.
    In this class we extract names as samples_names
"""

class Body_header_line:
    list_of_samples_to_be_combined = []

    def __init__(self, line):
        self.line = line
        self.has_format_field = False
        self.samples_names = []
        self.invalid = True
        self.warning_message = ""
        if line:
            self.extract_sample_names()
            self.update_line()

    def extract_sample_names(self):
        self.line = self.line.replace("\n", "")
        splitted_line = self.line.split("\t")
        if len(splitted_line) > 0:
            self.has_format_field = True
            self.samples_names = splitted_line[9:]

    def update_line(self):
        self.line = "#CHROM" + "\t" + "POS" + "\t" + "ID" + "\t" + "REF" + "\t" + "ALT" + "\t" + "QUAL" + "\t" + "FILTER" + "\t" + "INFO"

        if self.has_format_field:
            self.line += "\t" + "FORMAT"

        for sample in Body_header_line.list_of_samples_to_be_combined:
            if sample in self.samples_names:
                self.line += '\t' + sample
                self.invalid = False

        if len(Body_header_line.list_of_samples_to_be_combined) == 0:
            self.invalid = False
            for sample in self.samples_names:
                self.line += '\t' + sample

        self.line += "\n"

        if self.invalid:
            self.warning_message = "The names of samples in "

