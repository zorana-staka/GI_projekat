#!/usr/bin/env python
# coding: utf-8

"""
SmartCombineVariants (SCV) v1.0 made with Python by Zorana Štaka and Darko Pjević
This tools performs combining of two or more vcf files into one according to the perspective rules.
Copyright (c) ETF Beograd

Usage: 
    Smart_combine_variants.py (-i <inputVCF.vcf>)... [-s <sample_name>]... [-f <output_format>] [-o <out>]
Options:
    -h --help
    -i,--input_file <inputVCF.vcf>       Input vcf file
    -s, --sample_name <sample_name>      Name of the sample(s) to be combined
    -f,--output_format <output_format>   Output file format: COMPRESSED, UNCOMPRESSED or SAME_AS_INPUT [default: SAME_AS_INPUT]
    -o,--out <out>                       Output file
Example:
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -s NORMAL -f UNCOMPRESSED -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf    -i data/test/v2.vcf -s NORMAL -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -s NORMAL -f COMPRESSED -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -i v3.vcf -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf    -i data/test/v2.vcf.gz

"""

import time
from docopt import docopt
from Output_file import Output_file
from sys import stderr


start_time = time.time()

if __name__ == '__main__':
    arguments = docopt(__doc__)

    output_file = Output_file(arguments)

    if output_file.process_input_files() is False:
        print(output_file.error_message)

    print("--- %s seconds ---" % (time.time() - start_time), file=stderr)
