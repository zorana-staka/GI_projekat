import gzip
import re
import os

from Body_header_line import Body_header_line
from Body_record import Body_record
from Generate_idx_and_Sort import generate_idx
from Generic_header import Generic_header


class Input_file:
    """
        Class that represents input VCF files.
        This class contains all relevant information about file and methods for manipulation.
        Both, uncompressed (.vcf) and compressed (.vcf.gz) input files are supported.
    """

    def __init__(self, path, list_of_samples_to_be_combined):
        """ Create and initialize a input_file.
        :param path: path to the file
        :param list_of_samples_to_be_combined: samples that are of interest, ie. samples that need to be combined
        """
        self.path = path
        self.path_to_idx = ""
        self.indices = {}
        self.file = None
        self.compressed = self.path.endswith('vcf.gz') or self.path.endswith('vcf.GZ')
        self.version = None
        self.body_header_line = None
        self.list_of_header_objects_without_ID = list()
        self.list_of_contigs = list()
        self.list_of_header_objects = list()
        self.list_of_body_records_chrom = list()
        self.list_of_samples_to_be_combined = list_of_samples_to_be_combined
        self.convert = lambda text: int(text) if text.isdigit() else text
        self.alphanum_key = lambda key: [self.convert(c) for c in re.split('([0-9]+)', key)]
        self.invalid = False
        self.check_indices()
        self.error_message = ""

    def check_indices(self):
        """ Checks to see if there is file that contains information about indices.
            If such file doesn't exists it creates new onw according to the appropriate VCF or VCF.GZ file.
        """
        if self.compressed:
            self.path_to_idx = f'{self.path}.scvtbi'
        else:
            self.path_to_idx = f'{self.path}.scvidx'

        if os.path.isfile(self.path_to_idx):
            self.extract_indices()
        else:
            generate_idx(self.path)
            self.extract_indices()

    def extract_indices(self):
        """ Reads an appropriate file containing information about indices and stores that
            information in dictionary indices. """
        with open(self.path_to_idx) as idx_file:
            list_of_lines = idx_file.readlines()

        if len(list_of_lines) > 0:
            if "Positions of Chroms:" in list_of_lines[0]:
                list_of_lines = list_of_lines[1:]
                for list_item in list_of_lines:
                    attributes = list_item.rstrip(';\n').split(':')
                    self.indices[attributes[0]] = attributes[1].replace(' ', '')

    def read_header_of_file(self):
        """ Opens and reads a file regarding type of the file (compressed or uncompressed). """
        if self.compressed:
            with gzip.open(self.path) as self.file:
                line_of_file = (str(self.file.readline(), 'utf-8'))
                if line_of_file.startswith('##fileformat'):
                    self.version = line_of_file
                else:
                    self.invalid = True
                    self.error_message = f'There is no first mandatory header line in file expressing ' \
                                         f'version of file in file: {self.path}'
                    return
                self.read_header_in_gz_file()
                self.verify_start_of_header_for_body()
                if self.invalid is True:
                    self.error_message = f'There is no second header line specifiying data in the ' \
                                         f'body in file: {self.path}'

        else:
            with open(self.path) as self.file:
                line_of_file = self.file.readline()
                if line_of_file.startswith('##fileformat'):
                    self.version = line_of_file
                else:
                    self.invalid = True
                    self.error_message = f'There is no first mandatory header line in file expressing version ' \
                                         f'of file in file: {self.path}'
                    return
                self.read_header_in_file()
                self.verify_start_of_header_for_body()
                if self.invalid is True:
                    self.error_message = f'There is no second header line specifiying data in the ' \
                                         f'body in file: {self.path}'

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
        """
        generic_header_object = Generic_header(line_of_file)
        if generic_header_object.ID is not None and generic_header_object.tag != 'contig':
            self.list_of_header_objects.append(generic_header_object)
        elif generic_header_object.ID is None:
            self.list_of_header_objects_without_ID.append(generic_header_object)
        else:
            self.list_of_contigs.append(generic_header_object)

    def read_specific_chrom_body_of_file(self, chrom):
        """ Reads all body lines in compressed or uncompressed file and creates appropriate Body_record object.
            Object is placed in the list list_of_body_records_chrom.
        """
        self.list_of_body_records_chrom = []
        try:
            if chrom in self.indices.keys():
                if self.compressed:
                    with gzip.open(self.path) as self.file:
                        self.file.seek(int(self.indices[chrom]))
                        for line in self.file:
                            if line.startswith(f'{chrom}\t'.encode('utf-8')):
                                self.list_of_body_records_chrom.append(
                                    Body_record(str(line, 'utf-8'), self.body_header_line))
                            else:
                                break
                    self.verify_body_records()
                else:
                    with open(self.path) as self.file:
                        self.file.seek(int(self.indices[chrom]))
                        for line in self.file:
                            if line.startswith(f'{chrom}\t'):
                                self.list_of_body_records_chrom.append(Body_record(line, self.body_header_line))
                            else:
                                break
                    self.verify_body_records()

        finally:
            pass

    def verify_start_of_header_for_body(self):
        """ Verifies start of header for body. Header must start with #CHROM. If it doesn't invalid is set to True
            and appropriate error message is set. """
        if self.compressed:
            next_line = str(self.file.readline(), 'utf-8')
        else:
            next_line = self.file.readline()

        if next_line.startswith(f'#CHROM'):
            self.body_header_line = Body_header_line(next_line)
            if self.body_header_line.invalid is True:
                self.invalid = True
                self.error_message = self.body_header_line.error_message
        else:
            self.invalid = True
            self.error_message = f'There is no second header line specifiying data in the body in file: {self.path}'

    def verify_body_records(self):
        """ Verifies if all body records have different ref and alt field. If there is record that has same
            ref and alt field the file is invalid and appropriate error message is set. """
        if sum(body_record.ref == body_record.alt for body_record in self.list_of_body_records_chrom) > 0:
            self.invalid = True
            self.error_message = f'At least of of the records have same REF and ALT field.'
