#!/usr/bin/env python
# coding: utf-8

# In[3]:



"""
SmartCombineVariants (SCV) v1.0 by Zorana Štaka and Darko Pjević
Copyright (c) ETF Beograd

Usage: Merge_VCF_docopt_8.3.py CombineVariants (-I <inputVCF.vcf>)...

Options:
  -h --help 
  -I  input vcf file

"""
import collections
import re
import time
from docopt import docopt




ukupno = 0
total = 0

class Input_file:
    current_tag = ""

    def __init__(self, path):
        self.path = path
        self.has_current_tag = False
        self.header_read = False
        self.eof = False
        self.file = None
        self.next_tag = None

    def set_file(self, file):
        self.file = file

    def set_next_tag(self, next_tag):
        self.next_tag = next_tag

    def set_value_has_current_tag(self):
        self.has_current_tag = (self.current_tag == self.next_tag)


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
    def __hash__(self):
        return self.line


class Generic_header_object:
    def __init__(self, line):
        self.line = line
        self.data = {}
        self.extract_line_data()

    def extract_line_data(self):

        try:
            line_parse = self.line.split('=',1)[1]
            attributes = line_parse.split(',')
            for item in attributes:
                if item.count('=') >= 1:
                    splitted = item.split('=', 1)
                    self.data[splitted[0].lstrip('<,"')] = splitted[1].rstrip('>')
        except:
            pass

    def __eq__(self, other):
        return self.line == other.line
    
    def get_line(self):
        return self.line



def read_specific_tag_header_in_files(list_of_lines):
     
    for item in list_of_files:
       
        previous_position_of_file = item.file.tell()
        line_of_file = item.file.readline()
        
        while line_of_file.startswith('##'):
            list_of_lines.append(line_of_file)
            previous_position_of_file = item.file.tell()
            line_of_file = item.file.readline()
            
        item.file.seek(previous_position_of_file)
        
    list_of_lines = sorted(set(list_of_lines))
    for list_item in list_of_lines:
        generic_header_object = Generic_header_object(list_item) 
        list_of_objects.append(generic_header_object)
    
         
def read_specific_chrom_in_files(ukupno,list_of_lines):
    
    for item in list_of_files: 
        for item_file in item.file:   
            list_of_lines.append(item_file)
    
    list_of_lines = sorted(set(list_of_lines))
    for list_item in list_of_lines:
            body_object = Body_object(list_item) 
            list_of_objects.append(body_object)
           
    
convert = lambda text: int(text) if text.isdigit() else text
alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
        
def write_chrom_in_file():
    list_of_objects.sort(key=lambda x : alphanum_key(x.line))
    for value in list_of_objects:
        merged_vcf_file.write(value.line)
    list_of_objects.clear() 
    
        
        
def write_tag_in_file():
    #list_of_objects.sort(key = lambda x : x.line)
    for value in list_of_objects:
        merged_vcf_file.write(value.line)    
    
    list_of_objects.clear() 
    list_of_lines.clear() 
      

def verify_start_of_header():
    for item in list_of_files:
        next_line = item.file.readline()
        if next_line.startswith("#CHROM"): 
            pass
        else:
            return False
    
    merged_vcf_file.write(next_line)
    return True
        


first_file_path = "./Fajlovi/t1.vcf"
second_file_path = "./Fajlovi/t2.vcf"

merged_vcf_file = open("merged.vcf","w+")             
        
first_file = Input_file(first_file_path) 
second_file = Input_file(second_file_path)

list_of_files = [first_file, second_file]

list_of_lines = list()
list_of_objects = list()
list_of_versions = []


if __name__ == '__main__':
    arguments = docopt(__doc__)
    print(arguments)
    #print(arguments['<inputVCF.vcf>'])
    files = arguments['<inputVCF.vcf>']
    start_time = time.time()        
    
    with open(files[0]) as list_of_files[0].file:
        with open(files[1]) as list_of_files[1].file:
        
        
            for item in list_of_files: 
                previous_position_of_file = item.file.tell()
                line_of_file = item.file.readline()
                if line_of_file.startswith('##fileformat'):
                    list_of_versions.append(line_of_file)
                else:
                    item.file.seek(previous_position_of_file)
            
        
            merged_vcf_file.write(list_of_versions[0])  
            read_specific_tag_header_in_files(list_of_lines)
            write_tag_in_file() 
             
        
            if verify_start_of_header():     
                read_specific_chrom_in_files(ukupno,list_of_lines)
                write_chrom_in_file() 
        
    print("--- %s seconds ---" % (time.time() - start_time))
        #total += time.time() - start_time 
        #print(total)

