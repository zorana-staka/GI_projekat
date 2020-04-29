#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""
SmartCombineVariants (SCV) v1.0 by Zorana Štaka and Darko Pjević
Copyright (c) ETF Beograd

Usage: Merge_VCF_docopt_8.6.py (-i <inputVCF.vcf>)... [-f <output_format>] [-o <out>]

Options:
  -h --help
  
  -i,--input_file <inputVCF.vcf>                                        Input vcf file 
  
  -f,--output_format <output_format>                                    Output file format:
                                                                        COMPRESSED, UNCOMPRESSED or SAME_AS_INPUT
  
  -o,--out <out>                                                        Output file

"""



import time
from docopt import docopt
from Output_file import Output_file



start_time = time.time()
output_file = None

if __name__ == '__main__':
    arguments = docopt(__doc__)
    print(arguments)

    output_file = Output_file(arguments)

    output_file.read_input_files()

    output_file.write_output_file()

    print("--- %s seconds ---" % (time.time() - start_time))
    

