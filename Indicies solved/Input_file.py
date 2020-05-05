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
        self.list_of_body_objects = list()
        self.list_of_samples_to_be_combined = list_of_samples_to_be_combined
        self.convert = lambda text: int(text) if text.isdigit() else text
        self.alphanum_key = lambda key: [self.convert(c) for c in re.split('([0-9]+)', key)]
        self.invalid = False
        self.check_indices()
        self.error_message = ""

    def check_indices(self):
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
                previous_position_of_file = self.file.tell()
                line_of_file = (str(self.file.readline(), 'utf-8'))
                if line_of_file.startswith('##fileformat'):
                    self.version = line_of_file
                else:
                    self.file.seek(previous_position_of_file)
                self.read_header_in_gz_file()
                if self.verify_start_of_header():
                    return True

        else:
            
            with open(self.path) as self.file:
                previous_position_of_file = self.file.tell()
                line_of_file = self.file.readline()
                if line_of_file.startswith('##fileformat'):
                    self.version = line_of_file
                else:
                    self.invalid
                    self.error_message = f'There is no first mandatory header line in file expressing version of file in file: {self.path}'
                self.read_header_in_file()
                if self.verify_start_of_header():
                    return True

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

    def read_specific_chrom_body_of_file(self, chrom):
        """ Reads all body lines in uncompressed file and creates appropriate Body_record object.
            Object is placed in the list list_of_body_objects.
        """
        self.list_of_body_objects = []
        try:
            if chrom in self.indices.keys():
                with open(self.path) as self.file:
                    self.file.seek(int(self.indices[chrom]))
                    i = 0
                    for line in self.file:
                        if line.startswith(f'{chrom}\t'):
                            self.list_of_body_objects.append(Body_record(line, self.body_header_line))
                        else:
                            break
                self.verify_body_records()

        finally:
            pass

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
