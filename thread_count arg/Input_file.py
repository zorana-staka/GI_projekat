import gzip
import re

from Body_header_line import Body_header_line
from Body_record import Body_record
from Generic_header import Generic_header


class Input_file:
    """
        Class that represents input VCF files.
        This class contains all relevant information about file and methods for manipulation.
        Both, uncompressed (.vcf) and compressed (.vcf.gz) input files are supported.
    """

    def __init__(self, path, list_of_samples_to_be_combined, number_of_threads):
        """ Create and initialize a input_file.
        :param path: path to the file
        :param list_of_samples_to_be_combined: samples that are of interest, ie. samples that need to be combined
        """
        self.path = path
        self.number_of_threads = number_of_threads
        self.file = None
        self.compressed = self.path.endswith('vcf.gz') or self.path.endswith('vcf.GZ')
        self.version = None
        self.body_header_line = None
        self.list_of_header_objects_without_ID = list()
        self.list_of_contigs = list()
        self.list_of_header_objects = list()
        self.list_of_body_objects = list()
        self.list_of_samples_to_be_combined = list_of_samples_to_be_combined
        self.convert = lambda text: int(text) if text.isdigit() else text
        self.alphanum_key = lambda key: [self.convert(c) for c in re.split('([0-9]+)', key)]
        self.invalid = False

    def open_and_read_file(self):
        """ Opens and reads a file regarding type of the file (compressed or uncompressed).

        """
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

    def read_header_in_file(self):
        """ Reads a header part of uncompressed file. """
        previous_position_of_file = self.file.tell()
        line_of_file = self.file.readline()

        while line_of_file.startswith('##'):
            self.process_header_line(line_of_file)
            previous_position_of_file = self.file.tell()
            line_of_file = self.file.readline()

        self.file.seek(previous_position_of_file)

    def read_header_in_gz_file(self):
        """ Reads a header part of compressed file. """
        previous_position_of_file = self.file.tell()
        line_of_file = str(self.file.readline(), 'utf-8')
        while line_of_file.startswith('##'):
            self.process_header_line(line_of_file)
            previous_position_of_file = self.file.tell()
            line_of_file = str(self.file.readline(), 'utf-8')

        self.file.seek(previous_position_of_file)

    def process_header_line(self, line_of_file):
        """ Creates object of type of Generic_header and places it in appropriate list, regarding the tag.

        :param line_of_file: line that will be processed
        :return:
        """
        generic_header_object = Generic_header(line_of_file)
        if generic_header_object.ID is not None and generic_header_object.tag != 'contig':
            self.list_of_header_objects.append(generic_header_object)
        elif generic_header_object.ID is None:
            self.list_of_header_objects_without_ID.append(generic_header_object)
        else:
            self.list_of_contigs.append(generic_header_object)

    """
        Read all body lines in all files. 
        Delete all duplicates.
        After reading create objects type of Body_record according to list_of_header_lines.
    """

    def read_body_in_file(self):
        """ Reads all body lines in uncompressed file and creates appropriate Body_record object.
            Object is places in the list list_of_body_objects.
        """

        #list_test = list(map(str, self.file))
        #print("LIST TEST: " + str(list_test))

        #self.list_of_body_objects = [Body_record(x, self.body_header_line) for x in list_test]
        self.list_of_body_objects = list(map(lambda x: Body_record(x, self.body_header_line), self.file))
        #for line in self.file:
        #    body_record_object = Body_record(line, self.body_header_line)
        #    self.list_of_body_objects.append(body_record_object)
        self.verify_body_records()

    def create_body_record_object(self, line):
        return Body_record(line, self.body_header_line)

    def read_body_in_gz_file(self):
        """ Reads all body lines in compressed file and creates appropriate Body_record object.
            Object is places in the list list_of_body_objects.
        """
        for line in self.file:
            body_record_object = Body_record(str(line, 'utf-8'), self.body_header_line)
            self.list_of_body_objects.append(body_record_object)
        self.verify_body_records()

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

    def verify_body_records(self):
        if sum(body_record.ref == body_record.alt for body_record in self.list_of_body_objects) > 0:
            self.invalid = True
            print("Error")
