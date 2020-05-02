import gzip
import re

from Body_header_line import Body_header_line
from Body_record import Body_record
from Generic_header import Generic_header


class Input_file:

    def __init__(self, path, list_of_samples_to_be_combined):
        self.path = path
        self.file = None
        self.compressed = False
        self.set_file_type()
        self.version = None
        self.body_header_line = None
        self.list_of_other_header_objects = list()
        self.list_of_contigs = list()
        self.list_of_header_objects = list()
        self.list_of_body_objects = list()
        self.list_of_infos = list()
        self.list_of_samples_to_be_combined = list_of_samples_to_be_combined
        self.convert = lambda text: int(text) if text.isdigit() else text
        self.alphanum_key = lambda key: [self.convert(c) for c in re.split('([0-9]+)', key)]
        self.invalid = False

    def set_file_type(self):
        if self.path.endswith('vcf.gz') or self.path.endswith('vcf.GZ'):
            self.compressed = True
        elif self.path.endswith('.vcf'):
            self.compressed = False
        else:
            self.compressed = None

    def open_and_read_file(self):
        if self.compressed:
            with gzip.open(self.path) as self.file:
                previous_position_of_file = self.file.tell()
                line_of_file = (str(self.file.readline(), 'utf-8'))
                if line_of_file.startswith('##fileformat'):
                    self.version = line_of_file
                else:
                    self.file.seek(previous_position_of_file)
                self.read_header_in_gz_file()
                if self.verify_start_of_header():
                    self.read_body_in_gz_file()

        else:
            with open(self.path) as self.file:

                previous_position_of_file = self.file.tell()
                line_of_file = self.file.readline()
                if line_of_file.startswith('##fileformat'):
                    self.version = line_of_file
                else:
                    self.file.seek(previous_position_of_file)
                self.read_header_in_file()
                if self.verify_start_of_header():
                    self.read_body_in_file()

        self.verify_body_objects()

    def read_header_in_file(self):
        previous_position_of_file = self.file.tell()
        line_of_file = self.file.readline()

        while line_of_file.startswith('##'):
            generic_header_object = Generic_header(line_of_file)
            if generic_header_object.hasID and generic_header_object.tag != 'contig':
                self.list_of_header_objects.append(generic_header_object)
                if generic_header_object.tag == 'INFO':
                    self.list_of_infos.append(generic_header_object)
            elif not generic_header_object.hasID and generic_header_object.tag != 'contig':
                self.list_of_other_header_objects.append(generic_header_object)
            else:
                self.list_of_contigs.append(generic_header_object)
            previous_position_of_file = self.file.tell()
            line_of_file = self.file.readline()

        self.file.seek(previous_position_of_file)

    """
        Read all header lines in all compressed files. 
        Delete all duplicates.
        After reading create objects type of Generic_header according to list_of_header_lines.

    """

    def read_header_in_gz_file(self):
        previous_position_of_file = self.file.tell()
        line_of_file = str(self.file.readline(), 'utf-8')
        while line_of_file.startswith('##'):
            generic_header_object = Generic_header(line_of_file)
            if generic_header_object.hasID and generic_header_object.tag != 'contig':
                self.list_of_header_objects.append(generic_header_object)
                if generic_header_object.tag == 'INFO':
                    self.list_of_infos.append(generic_header_object)
            elif not generic_header_object.hasID and generic_header_object.tag != 'contig':
                self.list_of_other_header_objects.append(generic_header_object)
            else:
                self.list_of_contigs.append(generic_header_object)
            previous_position_of_file = self.file.tell()
            line_of_file = str(self.file.readline(), 'utf-8')

        self.file.seek(previous_position_of_file)

    """
        Read all body lines in all files. 
        Delete all duplicates.
        After reading create objects type of Body_record according to list_of_header_lines.
    """

    def read_body_in_file(self):
        for line in self.file:
            body_record_object = Body_record(line, self.body_header_line)
            self.list_of_body_objects.append(body_record_object)

    """
        Read all body lines in all compressed files. 
        Delete all duplicates.
        After reading create objects type of Body_record according to list_of_header_lines.

    """

    def read_body_in_gz_file(self):
        for line in self.file:
            body_record_object = Body_record(str(line, 'utf-8'), self.body_header_line)
            self.list_of_body_objects.append(body_record_object)

    def verify_start_of_header(self):

        if self.compressed:
            next_line = str(self.file.readline(), 'utf-8')
        else:
            next_line = self.file.readline()

        if next_line.startswith("#CHROM"):
            self.body_header_line = Body_header_line(next_line)
            if self.body_header_line.invalid:
                self.invalid = True
                return False
        else:
            self.invalid = True
            return False

        return self.check_if_header_body_line_contains_samples()

    def check_if_header_body_line_contains_samples(self):
        for sample_name in self.list_of_samples_to_be_combined:
            if sample_name not in self.body_header_line.line:
                self.invalid = True
                print("NEVALIDAN")
                return False
        return True

    def verify_body_objects(self):
        index = 0
        while index < len(self.list_of_body_objects):
            if self.list_of_body_objects[index].ref == self.list_of_body_objects[index].alt:
                self.invalid = True
                print("Error")
            index += 1