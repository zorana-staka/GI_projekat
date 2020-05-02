"""
    Represents record or one line in body part of VCF file.

"""

class Body_record:
    list_of_samples_to_be_combined = []

    def __init__(self, line, body_header_line):
        self.line = line
        if "\n" not in line:
            self.line = line + "\n"
        self.chrom = ""
        self.pos = 0
        self.id = ""
        self.ref = ""
        self.alt = ""
        self.qual = ""
        self.filter = ""
        self.filter_data = []
        self.info = ""
        self.format = ""
        self.has_format_field = False
        self.invalid = True
        self.samples = {}
        self.data_from_info = {}
        self.body_header_line = body_header_line
        self.extract_data_from_line()
        self.extract_data_from_info()

    def set_samples_to_be_combined(self, list_of_samples_to_be_combined):
        self.list_of_samples_to_be_combined = list_of_samples_to_be_combined

    def update_line(self):
        self.line = self.chrom + "\t" + str(
            self.pos) + "\t" + self.id + "\t" + self.ref + "\t" + self.alt + "\t" + self.qual + \
                    "\t" + str(self.filter) + "\t" + str(self.info)

        if self.has_format_field:
            self.line += "\t" + self.format

        for sample in Body_record.list_of_samples_to_be_combined:
            if sample in self.samples.keys():
                self.line += '\t' + self.samples[sample]
                self.invalid = False

        self.line += "\n"

        return self.line

    def extract_data_from_line(self):
        self.line = self.line.replace('\n', '')
        fields_in_body_record = self.line.split('\t')
        self.chrom = fields_in_body_record[0]
        self.pos = fields_in_body_record[1]
        self.id = fields_in_body_record[2]
        self.ref = fields_in_body_record[3]
        self.alt = fields_in_body_record[4]
        self.qual = fields_in_body_record[5]
        self.filter = fields_in_body_record[6]
        self.info = fields_in_body_record[7]

        if len(fields_in_body_record) > 8:
            self.has_format_field = True
            self.format = fields_in_body_record[8]
            index = 8
            for sample in self.body_header_line.samples_names:
                index += 1
                self.samples[sample] = fields_in_body_record[index]

    def extract_data_from_info(self):
        attributes = self.info.split(';')
        for item in attributes:
            if item.count('=') == 1:
                splitted = item.split('=')
                self.data_from_info[splitted[0]] = splitted[1]
                splitted.clear()
            else:
                self.data_from_info[item] = True

        self.data_from_info = dict(sorted(self.data_from_info.items()))
        self.update_info_field()
        self.update_line()

    def update_info_field(self):
        self.info = ""
        for key, value in self.data_from_info.items():
            if value != '':
                if str(value) == "True" or str(value) == "False":
                    self.info += key + ";"
                else:
                    self.info += key + "=" + str(value) + ";"

        self.info = self.info[:-1]

    def __eq__(self, other):
        return self.line == other.line

    def __hash__(self):
        return self.line
