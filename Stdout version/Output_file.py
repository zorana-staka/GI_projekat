import gzip
import re
import toolz
import bisect

from Body_record import Body_record
from Generic_header import Generic_header
from Input_file import Input_file


class Output_file:

    def __init__(self, arguments):
        self.path = ""
        self.file = None
        self.compressed = None
        self.version = None
        self.body_header_line = None
        self.list_of_header_lines = list()
        self.list_of_body_lines = list()
        self.list_of_header_objects = list()
        self.list_of_other_header_objects = list()
        self.list_of_body_objects = list()
        self.list_of_contigs = list()
        self.list_of_input_files_paths = list()
        self.list_of_input_files = list()
        self.arguments = arguments
        self.extract_info_from_arguments()
        self.convert = lambda text: int(text) if text.isdigit() else text
        self.alphanum_key = lambda key: [self.convert(c) for c in re.split('([0-9]+)', key)]

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

    def read_input_files(self):
        for input_file in self.list_of_input_files:  
            input_file.open_and_read_file()

            self.list_of_header_objects.extend(input_file.list_of_header_objects)
            self.list_of_other_header_objects.extend(input_file.list_of_other_header_objects)
            self.list_of_contigs.extend(input_file.list_of_contigs)
            self.list_of_body_objects.extend(input_file.list_of_body_objects)
		
        
        self.filter_header_lines()
        self.filter_body_lines()
        
        self.list_of_header_objects = list(self.list_of_header_objects)
        self.list_of_other_header_objects = list(self.list_of_other_header_objects)
        self.list_of_contigs = list(self.list_of_contigs)
        self.list_of_header_objects.extend(self.list_of_other_header_objects)
		
        self.arrange_header()
        self.list_of_header_objects.extend(self.list_of_contigs)
        self.sort_all_by_tag()
        self.arrange_body()

        self.verify_header()
        self.verify_body()

    # izbacititi duplikate
    def filter_header_lines(self):
        self.list_of_header_objects = toolz.unique(self.list_of_header_objects, key=lambda x: x.tag_and_ID)
        self.list_of_other_header_objects = toolz.unique(self.list_of_other_header_objects, key=lambda x: x.line)
        self.list_of_contigs = toolz.unique(self.list_of_contigs, key=lambda x: x.line)
    # izbacititi duplikate
    def filter_body_lines(self):
        self.list_of_body_objects = toolz.unique(self.list_of_body_objects, key=lambda x: x.line)
	
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
        print("Len: " + str(len(self.list_of_body_objects)))
        print("Verify: " + str(type(self.list_of_body_objects[0])))
        while index < len(self.list_of_body_objects):

            # same referent and alternate base on the same mutation - then it is not a mutation
            if self.list_of_body_objects[index].ref == self.list_of_body_objects[index].alt:
                print("Error")

            if index + 1 < len(self.list_of_body_objects):
                # same pos and chromosome
                if (self.list_of_body_objects[index].pos == self.list_of_body_objects[index + 1].pos and
                        self.list_of_body_objects[index].chrom == self.list_of_body_objects[index + 1].chrom and
                        self.list_of_body_objects[index].ref == self.list_of_body_objects[index + 1].ref):

                    if self.list_of_body_objects[index].id == self.list_of_body_objects[index + 1].id:
                        if self.list_of_body_objects[index].alt == self.list_of_body_objects[index + 1].alt:
                            pass
                            # to be continued

                        else:
                            self.list_of_body_objects[index].alt = self.list_of_body_objects[index].alt + "," + \
                                                                   self.list_of_body_objects[index + 1].alt
                            self.list_of_body_objects[index].update_line()
                            del self.list_of_body_objects[index + 1]


                    elif self.list_of_body_objects[index].id != '.' and self.list_of_body_objects[index + 1].id == '.':

                        if self.list_of_body_objects[index].alt == self.list_of_body_objects[index + 1].alt:
                            pass
                            # to be continued

                        else:
                            self.list_of_body_objects[index].alt = self.list_of_body_objects[index].alt + "," + \
                                                                   self.list_of_body_objects[index + 1].alt
                            self.list_of_body_objects[index].update_line()

                        del self.list_of_body_objects[index + 1]

                    elif self.list_of_body_objects[index].id == '.' and self.list_of_body_objects[index + 1].id != '.':
                        self.list_of_body_objects[index].id = self.list_of_body_objects[index + 1].id
                        self.list_of_body_objects[index].update_line()

                        if self.list_of_body_objects[index].alt == self.list_of_body_objects[index + 1].alt:
                            pass
                            # to be continued

                        else:
                            self.list_of_body_objects[index].alt = self.list_of_body_objects[index].alt + "," + \
                                                                   self.list_of_body_objects[index + 1].alt
                            self.list_of_body_objects[index].update_line()

                        del self.list_of_body_objects[index + 1]

                    elif self.list_of_body_objects[index].id != self.list_of_body_objects[index + 1].id:
                        self.list_of_body_objects[index].id = self.list_of_body_objects[index].id + "," + \
                                                              self.list_of_body_objects[
                                                                  index + 1].id
                        self.list_of_body_objects[index].update_line()

                elif (self.list_of_body_objects[index].pos == self.list_of_body_objects[index + 1].pos and
                      self.list_of_body_objects[index].chrom == self.list_of_body_objects[index + 1].chrom and
                      self.list_of_body_objects[index].ref != self.list_of_body_objects[index + 1].ref):

                    if len(self.list_of_body_objects[index].ref) == len(self.list_of_body_objects[index + 1].ref):
                        print("Error")

                    elif len(self.list_of_body_objects[index].ref) < len(self.list_of_body_objects[index + 1].ref):
                        if self.list_of_body_objects[index + 1].ref[0:len(self.list_of_body_objects[index].ref)] == \
                                self.list_of_body_objects[index].ref:
                            pass
                        else:
                            print("Error")

                    else:
                        if self.list_of_body_objects[index].ref[0:len(self.list_of_body_objects[index + 1].ref)] == \
                                self.list_of_body_objects[index + 1].ref:
                            pass
                        else:
                            print("Error")

            index += 1
