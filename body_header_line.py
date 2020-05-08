class Body_header_line:
    """ Represents a header line for body that starts with a single #.
        The first eight fields CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO are mandatory.
        Besides there fields there can be a FORMAT and samples fields.
    """
    list_of_samples_to_be_combined = []

    def __init__(self, line):
        """ Create and initialize a new body header line """
        self.line = line
        self.has_format_field = False
        self.samples_names = []
        self.invalid = None
        self.error_message = None
        self.position = None
        if line != "":
            self.extract_sample_names()
            self.update_line()

    def extract_sample_names(self):
        """ Get the values for fields separated by a tab. """
        self.line = self.line.replace('\n', '')
        splitted_line = self.line.split('\t')
        if len(splitted_line) > 0:
            self.has_format_field = True
            self.samples_names = splitted_line[9:]

    def update_line(self):
        """ Updates the line according to the changes. """
        self.line = f'#CHROM \t POS \t ID \t REF \t ALT \t QUAL \t FILTER \t INFO'

        if self.has_format_field:
            self.line += f'\t FORMAT'

        for sample in Body_header_line.list_of_samples_to_be_combined:
            if sample in self.samples_names:
                self.line += f'\t {sample}'
                self.invalid = False

        if len(Body_header_line.list_of_samples_to_be_combined) == 0:
            self.invalid = False
            for sample in self.samples_names:
                self.line += f'\t {sample}'

        if self.invalid is True:
            self.error_message = f'There is no samples {Body_header_line.list_of_samples_to_be_combined} in file.'

        self.line += '\n'
