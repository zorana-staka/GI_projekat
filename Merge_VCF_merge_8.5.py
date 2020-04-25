#!/usr/bin/env python
# coding: utf-8

# In[8]:


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
import gzip
from docopt import docopt
from Body_header_line import Body_header_line
from Body_record import Body_record
from Generic_header import Generic_header

"""
    Read all header lines in all files. 
    Delete all duplicates.
    After reading create objects type of Generic_header according to list_of_lines.
    
"""
def read_headers_in_files(list_of_lines):
     
    for item in file_objects:
        previous_position_of_file = item.tell()
        line_of_file = item.readline()
        
        while line_of_file.startswith('##'):
            list_of_lines.append(line_of_file)
            previous_position_of_file = item.tell()
            line_of_file = item.readline()
            
        item.seek(previous_position_of_file)
        
    list_of_lines = sorted(set(list_of_lines))
    for list_item in list_of_lines:
        generic_header_object = Generic_header(list_item)
        list_of_objects.append(generic_header_object)

"""
    Read all header lines in all compressed files. 
    Delete all duplicates.
    After reading create objects type of Generic_header according to list_of_lines.
    
"""
def read_headers_in_gz_files(list_of_lines):

    for item in file_objects:
        previous_position_of_file = item.tell()
        line_of_file = (str(item.readline(), 'utf-8'))

        while line_of_file.startswith('##'):
            list_of_lines.append(line_of_file)
            previous_position_of_file = item.tell()
            line_of_file = (str(item.readline(), 'utf-8'))

        item.seek(previous_position_of_file)

    list_of_lines = sorted(set(list_of_lines))
    for list_item in list_of_lines:
        generic_header_object = Generic_header(list_item)
        list_of_objects.append(generic_header_object)

"""
    Verify that there is no collision between records itself and other record with same chrom and pos.
    Will be more developed and more comprehensive, after testing all possible cases.
    
"""
def verify_records():
    index = 0
    check_mutations = True
    while index < len(list_of_objects):
        
        #same referent and alternate base on the same mutation - then it is not a mutation
        if list_of_objects[index].ref == list_of_objects[index].alt:
            print("Error")
        
        
        if index + 1 < len(list_of_objects):
            #same pos and chromosome
            if(list_of_objects[index].pos == list_of_objects[index + 1].pos and
                list_of_objects[index].chrom == list_of_objects[index + 1].chrom and
                  list_of_objects[index].ref == list_of_objects[index + 1].ref):
        
                if list_of_objects[index].id == list_of_objects[index + 1].id:
                    if list_of_objects[index].alt == list_of_objects[index + 1].alt:
                        pass 
                        #to be continued
                
                    else:
                        list_of_objects[index].alt = list_of_objects[index].alt + "," + list_of_objects[index + 1].alt
                        list_of_objects[index].update_line()
                        del list_of_objects[index + 1]
                
                
                elif list_of_objects[index].id != '.' and list_of_objects[index + 1].id == '.':
                    
                    if list_of_objects[index].alt == list_of_objects[index + 1].alt:
                        pass
                        #to be continued
                
                    else:
                        list_of_objects[index].alt = list_of_objects[index].alt + "," + list_of_objects[index + 1].alt
                        list_of_objects[index].update_line()
                        
                    del list_of_objects[index + 1]
                        
                elif list_of_objects[index].id == '.' and list_of_objects[index + 1].id != '.':
                    list_of_objects[index].id = list_of_objects[index + 1].id
                    list_of_objects[index].update_line()
                    
                    if list_of_objects[index].alt == list_of_objects[index + 1].alt:
                        pass
                        #to be continued
                
                    else:
                        list_of_objects[index].alt = list_of_objects[index].alt + "," + list_of_objects[index + 1].alt
                        list_of_objects[index].update_line()
                        
                    del list_of_objects[index + 1]            
                
                elif list_of_objects[index].id != list_of_objects[index + 1].id:
                    list_of_objects[index].id = list_of_objects[index].id + "," + list_of_objects[index + 1].id
                    list_of_objects[index].update_line()
             
            elif(list_of_objects[index].pos == list_of_objects[index + 1].pos and
                list_of_objects[index].chrom == list_of_objects[index + 1].chrom and
                  list_of_objects[index].ref != list_of_objects[index + 1].ref):
                
                if len(list_of_objects[index].ref) == len(list_of_objects[index + 1].ref):
                    print("Error")
                    
                elif len(list_of_objects[index].ref) < len(list_of_objects[index + 1].ref):
                    if list_of_objects[index + 1].ref[0:len(list_of_objects[index].ref)] == list_of_objects[index].ref:
                        pass
                    else:
                        print("Error")
                        
                else:
                    if list_of_objects[index].ref[0:len(list_of_objects[index + 1].ref)] == list_of_objects[index + 1].ref:
                        pass
                    else:
                        print("Error")        
                    
        index += 1
       
                    
"""
    Read all body lines in all files. 
    Delete all duplicates.
    After reading create objects type of Body_record according to list_of_lines.
    
"""
def read_bodies_in_files(list_of_lines):
    
    for file in file_objects:
        for line in file:   
            list_of_lines.append(line)

    list_of_lines = sorted(set(list_of_lines))
    for list_item in list_of_lines:
        body_object = Body_record(list_item)
        list_of_objects.append(body_object)

    verify_records()

"""
    Read all body lines in all compressed files. 
    Delete all duplicates.
    After reading create objects type of Body_record according to list_of_lines.
    
"""
def read_bodies_in_gz_files(list_of_lines):
    
    for file in file_objects:
        for line in file:   
            list_of_lines.append(str(line, 'utf-8'))
    
    list_of_lines = sorted(set(list_of_lines))
    for list_item in list_of_lines:
        body_object = Body_record(list_item)
        list_of_objects.append(body_object)   
            
    verify_records() 

"""
    Sorting objects by line and writing objects in output file. 
    
"""
        
def write_header_in_file():
    list_of_objects.sort(key = lambda x : x.line)
    for value in list_of_objects:
        merged_vcf_file.write(value.line)    
         
    list_of_objects.clear() 
    list_of_lines.clear() 


"""
    Sorting objects by chromosome and then by position and writing objects in output file. 
    
"""
def write_body_in_file():
    list_of_objects.sort(key = lambda x : alphanum_key(x.line))
    for value in list_of_objects:
        merged_vcf_file.write(value.line)
    list_of_objects.clear() 

def verify_start_of_gz_header():
    for item in file_objects:
        next_line = str(item.readline(), 'utf-8')
        if next_line.startswith("#CHROM"): 
            Body_record.body_header_line = Body_header_line(next_line)
        else:
            return False
    
    merged_vcf_file.write(next_line)
    return True

def verify_start_of_header():
    for item in file_objects:
        next_line = item.readline()
        if next_line.startswith("#CHROM"): 
            Body_record.body_header_line = Body_header_line(next_line)
        else:
            return False
    
    merged_vcf_file.write(next_line)
    return True
        

merged_vcf_file = open("merged.vcf","w+")             

list_of_lines = list()
list_of_objects = list()
list_of_versions = []
files_path = ['./Fajlovi/t1.vcf','./Fajlovi/t2.vcf']
start_time = time.time()  
file_objects = []
        
convert = lambda text: int(text) if text.isdigit() else text
alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 


"""
    If files are .vcf.gz then we need to read bytes and convert it to string
"""
if __name__ == '__main__':
    arguments = docopt(__doc__)
    files = arguments['<inputVCF.vcf>']

    if files[0].endswith('vcf.gz') and files[1].endswith('vcf.gz'):
        with gzip.open(files[0]) as file1:
            with gzip.open(files[1]) as file2:

                file_objects.append(file1)
                file_objects.append(file2)
                
                for item in file_objects:
                    previous_position_of_file = item.tell()
                    line_of_file = str(item.readline(), 'utf-8')
                    if line_of_file.startswith('##fileformat'):
                         list_of_versions.append(line_of_file)
                    else:
                         item.seek(previous_position_of_file)

                merged_vcf_file.write(list_of_versions[0]) 
                read_headers_in_gz_files(list_of_lines) 
                write_header_in_file() 
        
                if verify_start_of_gz_header():
                    read_bodies_in_gz_files(list_of_lines)
                    write_body_in_file() 

    elif files[0].endswith('.vcf') and files[1].endswith('.vcf'):
        with open(files[0]) as file1:
            with open(files[1]) as file2:
            
                file_objects.append(file1)
                file_objects.append(file2)
                
                for item in file_objects:
                    previous_position_of_file = item.tell()
                    line_of_file = item.readline()
                    if line_of_file.startswith('##fileformat'):
                         list_of_versions.append(line_of_file)
                    else:
                         item.seek(previous_position_of_file)
            
        
                merged_vcf_file.write(list_of_versions[0]) 
                read_headers_in_files(list_of_lines)
                write_header_in_file() 
             
        
                if verify_start_of_header():
                    read_bodies_in_files(list_of_lines)
                    write_body_in_file() 
    else:
        print('Invalid input format!')
    print("--- %s seconds ---" % (time.time() - start_time))


# In[ ]:





# In[ ]:




