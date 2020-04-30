import gzip
import re

import toolz

from Input_file import Input_file

"""
    Class containing important information about output file ie. merged VCF.
"""


class Output_file:

    def __init__(self, arguments):
        self.path = ""
        self.file = None
        self.compressed = None
        self.version = None
        self.body_header_line = None
        self.list_of_header_objects = list()
        self.list_of_other_header_objects = list()
        self.list_of_body_objects = list()
        self.list_of_contigs = list()
        self.list_of_infos = list()
        self.list_of_input_files_paths = list()
        self.list_of_input_files = list()
        self.arguments = arguments
        self.extract_info_from_arguments()
        self.convert = lambda text: int(text) if text.isdigit() else text
        self.alphanum_key = lambda key: [self.convert(c) for c in re.split('([0-9]+)', key)]

    """
        Determinate attributes from respective user input parameters. 
    """

    def extract_info_from_arguments(self):

        for file_path in self.arguments['--input_file']:
            file_object = Input_file(file_path)
            self.list_of_input_files.append(file_object)
            self.list_of_input_files_paths.append(file_path)

        if self.arguments['--out']:

            if self.arguments['--output_format'] == 'COMPRESSED':
                self.file = gzip.open(self.arguments['--out'] + '.gz', "r+b")
                self.compressed = True
            elif self.arguments['--output_format'] == 'UNCOMPRESSED':
                self.file = open(self.arguments['--out'], "r+")
                self.compressed = False
            else:
                if self.list_of_input_files[0].compressed:
                    self.file = gzip.open(self.arguments['--out'] + '.gz', "r+b")
                    self.compressed = True
                else:
                    self.file = open(self.arguments['--out'], "r+")

    """
        This method reads all of the input files by calling method open_and_read_file of Input_file class. 
        After reading each file objects for header and body parts are added to the convenient list of objects.
        Contig tags has a separate list, because the sorting rules do not apply for them.
        Filter methods are used to delete duplicates. 
        Arrange methods are used to sort header and body part. 
        Verify methods are used to check if rules for VCF files are respected.  
    """
    def read_input_files(self):
        for input_file in self.list_of_input_files:
            input_file.open_and_read_file()

            self.list_of_header_objects.extend(input_file.list_of_header_objects)
            self.list_of_other_header_objects.extend(input_file.list_of_other_header_objects)
            self.list_of_contigs.extend(input_file.list_of_contigs)
            self.list_of_infos.extend(input_file.list_of_infos)
            self.list_of_body_objects.extend(input_file.list_of_body_objects)

        self.filter_header_objects()
        self.filter_body_objects()

        for body_record in self.list_of_body_objects:
            body_record.extract_data_from_info()

        self.list_of_header_objects.extend(self.list_of_other_header_objects)
        self.arrange_header()
        self.list_of_header_objects.extend(self.list_of_contigs)
        self.sort_all_by_tag()
        self.arrange_body()

        self.verify_header()
        self.verify_body()


    def filter_header_objects(self):
        self.list_of_header_objects = list(toolz.unique(self.list_of_header_objects, key=lambda x: x.tag_and_ID))
        self.list_of_header_objects = list(toolz.unique(self.list_of_header_objects, key=lambda x: x.tag_and_ID))
        self.list_of_other_header_objects = list(toolz.unique(self.list_of_other_header_objects, key=lambda x: x.line))
        self.list_of_contigs = list(toolz.unique(self.list_of_contigs, key=lambda x: x.line))
        self.list_of_infos = list(toolz.unique(self.list_of_infos, key=lambda x: x.line))


    def filter_body_objects(self):
        self.list_of_body_objects = list(toolz.unique(self.list_of_body_objects, key=lambda x: x.line))

    def sort_all_by_tag(self):
        self.list_of_header_objects.sort(key=lambda x: x.tag, reverse=False)

    def arrange_header(self):
        self.list_of_header_objects.sort(key=lambda x: x.line)

    def arrange_body(self):
        self.list_of_body_objects = list(self.list_of_body_objects)
        self.list_of_body_objects.sort(key=lambda x: self.alphanum_key(x.line))

    def write_output_file(self):
        if self.compressed:
            self.write_header_in_gz_file()
            self.write_body_in_gz_file()
        else:
            self.write_header()
            self.write_body()

    def write_header(self):
        if self.arguments['--out']:
            for list_item in self.list_of_header_objects:
                self.file.write(list_item.line)
        else:
            for list_item in self.list_of_header_objects:
                print(list_item.line)

    def write_body(self):
        if self.arguments['--out']:
            for list_item in self.list_of_body_objects:
                self.file.write(list_item.line)
        else:
            for list_item in self.list_of_body_objects:
                print(list_item.line)

    def write_header_in_gz_file(self):
        if self.arguments['--out']:
            for list_item in self.list_of_header_objects:
                self.file.write(list_item.line.encode('utf-8'))
        else:
            for list_item in self.list_of_header_objects:
                print(list_item.line.encode('utf-8'))

    def write_body_in_gz_file(self):
        if self.arguments['--out']:
            for list_item in self.list_of_body_objects:
                self.file.write(list_item.line.encode('utf-8'))
        else:
            for list_item in self.list_of_body_objects:
                print(list_item.line.encode('utf-8'))

    def verify_header(self):
        pass

    def verify_body(self):
        index = 0
        while index < len(self.list_of_body_objects):

            if index + 1 < len(self.list_of_body_objects):
                # same pos and chromosome
                if (self.list_of_body_objects[index].pos == self.list_of_body_objects[index + 1].pos and
                        self.list_of_body_objects[index].chrom == self.list_of_body_objects[index + 1].chrom):

                    print("DUPLICATE: " + self.list_of_body_objects[index].chrom + ", " +self.list_of_body_objects[index].pos)
                    # samo u ovom slučaju možemo ići na spajanje dvije linije, inače ne
                    if self.list_of_body_objects[index].ref == self.list_of_body_objects[index + 1].ref:

                        if self.list_of_body_objects[index].filter == self.list_of_body_objects[index + 1].filter:
                            self.list_of_body_objects[index].id = self.determinate_id(
                                self.list_of_body_objects[index].id, self.list_of_body_objects[index + 1].id)

                            self.list_of_body_objects[index].alt = self.determinate_alt(
                                self.list_of_body_objects[index].alt, self.list_of_body_objects[index + 1].alt)

                            self.list_of_body_objects[index].qual = self.determinate_qual(
                                self.list_of_body_objects[index].qual, self.list_of_body_objects[index + 1].qual)

                            self.list_of_body_objects[index].info = self.determinate_info(
                                self.list_of_body_objects[index].info, self.list_of_body_objects[index + 1].info)

                            self.list_of_body_objects[index].update_line()

                            del self.list_of_body_objects[index + 1]

                        elif self.list_of_body_objects[index].filter == "PASS" or self.list_of_body_objects[
                            index + 1].filter == "PASS":
                            self.list_of_body_objects[index].filter = "PASS"

                            self.list_of_body_objects[index].id = self.determinate_id(
                                self.list_of_body_objects[index].id, self.list_of_body_objects[index + 1].id)

                            self.list_of_body_objects[index].alt = self.determinate_alt(
                                self.list_of_body_objects[index].alt, self.list_of_body_objects[index + 1].alt)

                            self.list_of_body_objects[index].qual = self.determinate_qual(
                                self.list_of_body_objects[index].qual, self.list_of_body_objects[index + 1].qual)

                            self.list_of_body_objects[index].info = self.determinate_info(
                                self.list_of_body_objects[index].info, self.list_of_body_objects[index + 1].info)

                            self.list_of_body_objects[index].update_line()

                            del self.list_of_body_objects[index + 1]

                        else:
                            return False

                    elif self.list_of_body_objects[index].ref != self.list_of_body_objects[index + 1].ref and \
                            len(str(self.list_of_body_objects[index].ref)) == \
                            len(str(self.list_of_body_objects[index + 1].ref)):
                        return False

            index += 1

        return True

    def determinate_id_alt_qual_info(self, record_one, record_two):
        pass

    def determinate_info(self, data_from_info_one, data_from_info_two):
        # return dict(data_from_info_one.items() & data_from_info_two.items())
        pass

    def determinate_id(self, id_one, id_two):
        if id_one == id_two:
            return id_one
        if id_one == ".":
            return id_two
        if id_two == ".":
            return id_one
        return id_one + "," + id_two

    def determinate_qual(self, qual_one, qual_two):
        if qual_one == qual_two:
            return qual_one
        if qual_one == ".":
            return qual_two
        if qual_two == ".":
            return qual_one
        if float(qual_one) < float(qual_two):
            return qual_one
        return qual_one

    # obraditi i za * i za N
    def determinate_alt(self, alt_one, alt_two):
        if alt_one == alt_two:
            return alt_one
        if alt_one == ".":
            return alt_two
        if alt_two == ".":
            return alt_one
        return alt_one + "," + alt_two
