"""
    Represents record or one line in body part of VCF file.

"""


class Body_record:

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
        self.info = ""
        self.info_fields = None
        self.samples = {}
        self.data_from_info = {}
        self.body_header_line = body_header_line
        self.extract_data_from_line()
        self.extract_data_from_info()
        #print(self.data_from_info)

    def update_line(self):
        self.line = self.chrom + "\t" + str(self.pos) + "\t" + self.id + "\t" + self.ref + "\t" + self.alt + "\t" + self.qual + \
                    "\t" + str(self.filter) + "\t" + str(self.info)

        for key, value in self.samples.items():
            self.line += "\t" + value

    def extract_data_from_line(self):
        splitted_line = self.line.split("\t")
        self.chrom = splitted_line[0]
        self.pos = splitted_line[1]
        self.id = splitted_line[2]
        self.ref = splitted_line[3]
        self.alt = splitted_line[4]
        self.qual = splitted_line[5]
        self.filter = splitted_line[6]
        self.info = splitted_line[7]

        index = 7
        for sample in self.body_header_line.samples_names:
            index += 1
            self.samples[sample] = splitted_line[index].replace('\n', '')

    def extract_data_from_info(self):
        
        self.data_from_info[self.info.split(';',1)[0]] = True
        line_parse = self.info.split(';',1)[1]
        attributes = line_parse.split(';')
        for item in attributes:
            if item.count('=') >= 1:
                splitted = item.split('=', 1)
                self.data_from_info[splitted[0]] = splitted[1]
        
		


    def __eq__(self, other):
        return self.line == other.line

    def __hash__(self):
        return self.line
