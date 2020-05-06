#!/usr/bin/env python
# coding: utf-8


"""
SmartCombineVariants (SCV) v1.0 by Zorana Štaka and Darko Pjević
Copyright (c) ETF Beograd

Usage: Generate_IDX.py (-i <inputVCF.vcf>)...

Options:
  -h --help
  
  -i,--input_file <inputVCF.vcf>                                        Input vcf file
                         

"""

import time
from docopt import docopt
import gzip
import re


class Generic_header:

    def __init__(self, line):
        self.line = line
        self.tag = ""
        self.ID = ""
        self.hasID = False
        self.getID()
        self.get_tag()
        self.tag_and_ID = ""

    def get_tag(self):
        line_parse = self.line.split('=', 1)[0]
        self.tag = line_parse[2:]
        self.tag_and_ID = self.tag + "_" + self.ID

    def getID(self):
        line_parse = self.line.split('=', 1)[1]
        attributes = line_parse.split(',')
        if attributes[0].count('=') >= 1:
            splitted = attributes[0].split('=', 1)
            self.ID = splitted[1].rstrip('>')
            self.hasID = True


class Body_record:
    """ Class representing line in body part of VCF file. """

    def __init__(self, line):
        """ Create and initialize a new Body_record.

        :param line:  line in body part of VCF file. Mold for this class.
        :param body_header_line: Header line in corresponding VCF file.
        """
        self.line = line
        if "\n" not in line:
            self.line = line + "\n"
        self.chrom = ""
        self.extract_data_from_line()

    def extract_data_from_line(self):
        """ Get separate fields in line according to the Header line for the body. """
        self.line = self.line.replace('\n', '')
        fields_in_body_record = self.line.split('\t')
        self.chrom = fields_in_body_record[0]

        self.line = self.line + '\n'


class Input_file:
    """
        Class that represents input VCF files.
        This class contains all relevant information about file and methods for manipulation.
        Both, uncompressed (.vcf) and compressed (.vcf.gz) input files are supported.
    """
    def __init__(self, path):
        """ Create and initialize a input_file.
            :param path: path to the file
            :param list_of_samples_to_be_combined: samples that are of interest, ie. samples that need to be combined
        """
        self.path = path
        self.file = None
        self.compressed = self.path.endswith('vcf.gz') or self.path.endswith('vcf.GZ')
        self.version = None
        self.body_header_line = None
        self.list_of_contigs = list()
        self.list_of_header_objects = list()
        self.list_of_body_objects = list()
        self.convert = lambda text: int(text) if text.isdigit() else text
        self.alphanum_key = lambda key: [self.convert(c) for c in re.split('([0-9]+)', key)]
        self.open_and_read_file()

    def open_and_read_file(self):
        """ Opens and reads compressed or uncompressed file. """
        if self.compressed:
            with gzip.open(self.path) as self.file:
                previous_position_of_file = self.file.tell()
                line_of_file = (str(self.file.readline(), 'utf-8'))
                if line_of_file.startswith('##fileformat'):
                    self.version = line_of_file
                else:
                    self.file.seek(previous_position_of_file)
                self.read_header_in_gz_file()
                self.arrange_header()
                if self.verify_start_of_header():
                    self.read_body_in_gz_file()
                    self.arrange_body()

        else:
            with open(self.path) as self.file:
                previous_position_of_file = self.file.tell()
                line_of_file = self.file.readline()
                if line_of_file.startswith('##fileformat'):
                    self.version = line_of_file
                else:
                    self.file.seek(previous_position_of_file)
                self.read_header_in_file()
                self.arrange_header()
                if self.verify_start_of_header():
                    self.read_body_in_file()
                    self.arrange_body()

    def read_header_in_file(self):
        """ Reads header in compressed file. """
        previous_position_of_file = self.file.tell()
        line_of_file = self.file.readline()

        while line_of_file.startswith('##'):
            generic_header_object = Generic_header(line_of_file)
            if generic_header_object.tag != 'contig':
                self.list_of_header_objects.append(generic_header_object)
            else:
                self.list_of_contigs.append(generic_header_object)
            previous_position_of_file = self.file.tell()
            line_of_file = self.file.readline()

        self.file.seek(previous_position_of_file)

    def read_header_in_gz_file(self):
        """ Reads header in uncompressed file. """
        previous_position_of_file = self.file.tell()
        line_of_file = str(self.file.readline(), 'utf-8')
        while line_of_file.startswith('##'):
            generic_header_object = Generic_header(line_of_file)
            if generic_header_object.tag != 'contig':
                self.list_of_header_objects.append(generic_header_object)
            else:
                self.list_of_contigs.append(generic_header_object)
            previous_position_of_file = self.file.tell()
            line_of_file = str(self.file.readline(), 'utf-8')

        self.file.seek(previous_position_of_file)

    def read_body_in_file(self):
        """ Reads body in uncompressed file. """
        for line in self.file:
            body_record_object = Body_record(line)
            self.list_of_body_objects.append(body_record_object)

    def read_body_in_gz_file(self):
        """ Reads body in compressed file. """
        for line in self.file:
            body_record_object = Body_record(str(line, 'utf-8'))
            self.list_of_body_objects.append(body_record_object)

    def verify_start_of_header(self):
        """ Verifies start of header for body. Header must start with #CHROM. """
        if self.compressed:
            next_line = str(self.file.readline(), 'utf-8')
        else:
            next_line = self.file.readline()

        if next_line.startswith("#CHROM"):
            self.body_header_line = next_line
            return True
        else:
            return False

    def arrange_header(self):
        """ Sorts lists for header. """
        self.list_of_header_objects.sort(key=lambda x: x.line)
        self.list_of_header_objects.extend(self.list_of_contigs)
        self.list_of_header_objects.sort(key=lambda x: x.tag, reverse=False)

    def arrange_body(self):
        """ Sorts list of body records. """
        self.list_of_body_objects.sort(key=lambda x: self.alphanum_key(x.line))


def write_header(file_object, sort_file):
    """ Writes header in uncompressed file. """
    for list_item in file_object.list_of_header_objects:
        sort_file.write(list_item.line)
    sort_file.write(file_object.body_header_line)


def write_body(file_object, sort_file, index_file):
    """ Writes body in uncompressed file and write specific chromosome and position in index file. """
    chrom = file_object.list_of_body_objects[0].chrom
    position = sort_file.tell()
    index_file.write((str(chrom) + ': ' + str(position) + ';\n').encode('utf-8'))
    for list_item in file_object.list_of_body_objects:
        position = sort_file.tell()
        sort_file.write(list_item.line)
        if list_item.chrom != chrom:
            chrom = list_item.chrom
            index_file.write((str(chrom) + ': ' + str(position) + ';\n').encode('utf-8'))
        else:
            pass


def write_header_in_gz_file(file_object, sort_file):
    """ Writes header in compressed file. """
    for list_item in file_object.list_of_header_objects:
        sort_file.write(list_item.line.encode('utf-8'))
    sort_file.write(file_object.body_header_line.encode('utf-8'))


def write_body_in_gz_file(file_object, sort_file, index_file):
    """ Writes body in compressed file and write specific chromosome and position in index file. """
    chrom = file_object.list_of_body_objects[0].chrom
    position = sort_file.tell()
    index_file.write((str(chrom) + ': ' + str(position) + ';\n').encode('utf-8'))
    for list_item in file_object.list_of_body_objects:
        position = sort_file.tell()
        sort_file.write(list_item.line.encode('utf-8'))
        if list_item.chrom != chrom:
            chrom = list_item.chrom
            index_file.write((str(chrom) + ': ' + str(position) + ';\n').encode('utf-8'))
        else:
            pass


def generate_idx(file_path):
    """ Generate index file according to the input file."""
    file_object = Input_file(file_path)
    if file_object.compressed:
        sort_file = gzip.open(file_path, "w+b")
        index_file = open(file_path + '.scvtbi', "w+b")
        sort_file.write(file_object.version.encode('utf-8'))
        index_file.write(('Positions of Chroms:\n').encode('utf-8'))
        write_header_in_gz_file(file_object, sort_file)
        write_body_in_gz_file(file_object, sort_file, index_file)
    else:
        sort_file = open(file_path, "w+")
        index_file = open(file_path + '.scvidx', "w+b")
        sort_file.write(file_object.version)
        index_file.write(('Positions of Chroms:\n').encode('utf-8'))
        write_header(file_object, sort_file)
        write_body(file_object, sort_file, index_file)

    sort_file.close()
    index_file.close()


if __name__ == '__main__':

    start_time = time.time()

    arguments = docopt(__doc__)

    print(arguments)

    for file_path in arguments['--input_file']:
        generate_idx(file_path)

    print("--- %s seconds ---" % (time.time() - start_time))
