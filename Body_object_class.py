
class Body_object:

    def __init__(self, line):
        self.line = line
        if "\n" not in line:
            self.line = line + "\n"
        self.chrom = ""
        self.id = ""
        self.ref = ""
        self.alt = ""
        self.qual = ""
        self.filter = ""
        self.info = ""
        self.extract_data_from_line()

    def extract_data_from_line(self):
        splitted_line = self.line.split("\t")
        self.chrom = splitted_line[0]
        self.id = splitted_line[1]
        self.ref = splitted_line[2]
        self.alt = splitted_line[3]
        self.qual = splitted_line[4]
        self.filter = splitted_line[5]
        self.info = splitted_line[6]

    #dodati odgovarajuća pravila za spajanje
    #vidjeti u GATK kako rade različiti scenariji
    def __eq__(self, other):
        return self.line == other.line

