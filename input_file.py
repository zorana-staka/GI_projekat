import gzip
import re

from body_header_line import Body_header_line
from body_record import Body_record
from generic_header import Generic_header


class Input_file:
    """
        Class that represents input VCF files.
        This class contains all relevant information about input_vcf_file and methods for manipulation.
        Both, uncompressed (.vcf) and compressed (.vcf.gz) input files are supported.
    """

    def __init__(self, path, list_of_samples_to_be_combined):
        """ Create and initialize a input_file.
        :param path: path to the input_vcf_file
        :param list_of_samples_to_be_combined: samples that are of interest, ie. samples that need to be combined
        """
        self.path = path
        self.path_to_idx = ""
        self.chromosomes_positions = {}
        self.input_vcf_file = None
        self.compressed = self.path.endswith('vcf.gz') or self.path.endswith('vcf.GZ')
        self.version = None
        self.body_start_position = None
        self.body_header_line = None
        self.list_of_header_objects_without_ID = list()
        self.list_of_contigs = list()
        self.list_of_header_objects = list()
        self.list_of_body_records_chrom = list()
        self.list_of_samples_to_be_combined = list_of_samples_to_be_combined
        self.convert = lambda text: int(text) if text.isdigit() else text
        self.alphanum_key = lambda key: [self.convert(c) for c in re.split('([0-9]+)', key)]
        self.invalid = False
        self.error_message = ""

    def read_header_of_file(self):
        """ Opens and reads a input_vcf_file regarding type of the input_vcf_file (compressed or uncompressed). """
        if self.compressed:
            with gzip.open(self.path) as self.input_vcf_file:
                line_of_file = (str(self.input_vcf_file.readline(), 'utf-8'))
                if line_of_file.startswith('##fileformat'):
                    self.version = line_of_file
                else:
                    self.invalid = True
                    self.error_message = f'There is no first mandatory header line in input_vcf_file expressing ' \
                                         f'version of input_vcf_file in input_vcf_file: {self.path}'
                    return
                self.read_header_in_gz_file()
                self.verify_start_of_header_for_body()
                if self.invalid is True:
                    self.error_message = f'There is no second header line specifying data in the ' \
                                         f'body in input_vcf_file: {self.path}'
        else:
            with open(self.path) as self.input_vcf_file:
                line_of_file = self.input_vcf_file.readline()
                if line_of_file.startswith('##fileformat'):
                    self.version = line_of_file
                else:
                    self.invalid = True
                    self.error_message = f'There is no first mandatory header line in input_vcf_file expressing version ' \
                                         f'of input_vcf_file in input_vcf_file: {self.path}'
                    return
                self.read_header_in_file()
                self.verify_start_of_header_for_body()
                if self.invalid is True:
                    self.error_message = f'There is no second header line specifiying data in the ' \
                                         f'body in input_vcf_file: {self.path}'

    def read_header_in_file(self):
        """ Reads a header part of uncompressed input_vcf_file. """
        previous_position_of_file = self.input_vcf_file.tell()
        line_of_file = self.input_vcf_file.readline()
        while line_of_file.startswith('##'):
            self.process_header_line(line_of_file)
            previous_position_of_file = self.input_vcf_file.tell()
            line_of_file = self.input_vcf_file.readline()

        self.input_vcf_file.seek(previous_position_of_file)

    def read_header_in_gz_file(self):
        """ Reads a header part of compressed input_vcf_file. """
        previous_position_of_file = self.input_vcf_file.tell()
        line_of_file = str(self.input_vcf_file.readline(), 'utf-8')
        while line_of_file.startswith('##'):
            self.process_header_line(line_of_file)
            previous_position_of_file = self.input_vcf_file.tell()
            line_of_file = str(self.input_vcf_file.readline(), 'utf-8')

        self.input_vcf_file.seek(previous_position_of_file)

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
        """ Reads all body lines in compressed or uncompressed input_vcf_file and creates appropriate Body_record object.
            Object is placed in the list list_of_body_records_chrom.
        """
        self.list_of_body_records_chrom = []
        try:
            if chrom in self.chromosomes_positions.keys():
                if self.compressed:
                    with gzip.open(self.path) as self.input_vcf_file:
                        for position in self.chromosomes_positions[chrom]:
                            self.input_vcf_file.seek(int(position))
                            for line in self.input_vcf_file:
                                if line.startswith(f'{chrom}\t'.encode('utf-8')):
                                    self.list_of_body_records_chrom.append(
                                        Body_record(str(line, 'utf-8'), self.body_header_line))
                                else:
                                    break
                    self.verify_body_records()
                else:
                    with open(self.path) as self.input_vcf_file:
                        for position in self.chromosomes_positions[chrom]:
                            self.input_vcf_file.seek(int(position))
                            for line in self.input_vcf_file:
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
            next_line = str(self.input_vcf_file.readline(), 'utf-8')
        else:
            next_line = self.input_vcf_file.readline()

        if next_line.startswith(f'#CHROM'):
            self.body_header_line = Body_header_line(next_line)
            self.body_start_position = self.input_vcf_file.tell()
            if self.body_header_line.invalid is True:
                self.invalid = True
                self.error_message = self.body_header_line.error_message
        else:
            self.invalid = True
            self.error_message = f'There is no second header line specifying data in the body in input_vcf_file: {self.path}'

    def extract_indices_for_chromosomes(self):
        if self.compressed:
            with gzip.open(self.path) as self.input_vcf_file:
                self.input_vcf_file.seek(self.body_start_position)
                line_of_file = str(self.input_vcf_file.readline(), 'utf-8')

                current_chrom = (line_of_file.split('\t'))[0]
                if current_chrom not in self.chromosomes_positions.keys():
                    self.chromosomes_positions[current_chrom] = list()
                self.chromosomes_positions[current_chrom].append(self.body_start_position)

                while line_of_file != '':
                    if line_of_file.startswith(f'{current_chrom}\t'):
                        pass
                    else:
                        current_chrom = (line_of_file.split('\t'))[0]
                        if current_chrom not in self.chromosomes_positions.keys():
                            self.chromosomes_positions[current_chrom] = list()
                        self.chromosomes_positions[current_chrom].append(previous_position_of_file)
                    previous_position_of_file = self.input_vcf_file.tell()
                    line_of_file = str(self.input_vcf_file.readline(), 'utf-8')
        else:
            with open(self.path) as self.input_vcf_file:
                self.input_vcf_file.seek(self.body_start_position)
                line_of_file = self.input_vcf_file.readline()

                current_chrom = (line_of_file.split('\t'))[0]
                if current_chrom not in self.chromosomes_positions.keys():
                    self.chromosomes_positions[current_chrom] = list()
                self.chromosomes_positions[current_chrom].append(self.body_start_position)

                while line_of_file != '':
                    if line_of_file.startswith(f'{current_chrom}\t'):
                        pass
                    else:
                        current_chrom = (line_of_file.split('\t'))[0]
                        if current_chrom not in self.chromosomes_positions.keys():
                            self.chromosomes_positions[current_chrom] = list()
                        self.chromosomes_positions[current_chrom].append(previous_position_of_file)
                    previous_position_of_file = self.input_vcf_file.tell()
                    line_of_file = self.input_vcf_file.readline()

    def verify_body_records(self):
        """ Verifies if all body records have different ref and alt field. If there is record that has same
            ref and alt field the input_vcf_file is invalid and appropriate error message is set. """
        if sum(body_record.ref == body_record.alt for body_record in self.list_of_body_records_chrom) > 0:
            self.invalid = True
            self.error_message = f'At least of of the records have same REF and ALT field.'
