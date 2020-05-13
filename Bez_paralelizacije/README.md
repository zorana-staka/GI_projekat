# Smart Combine Variants

Python tool for smart combining of genomic variants

SmartCombineVariants (SCV) is a Python tool that performs combining variants of two VCF files. The tool supports the combining of VCF originating from different variant callers and with different headers. SCV should also support the combining of VCFs with multiple samples. When samples do not match it is possible to configure which samples will be combined through an input key-value parameter.

Usage: Smart_combine_variants.py (-i <inputVCF.vcf>)... [-s <sample_name>]... [-f <output_format>] [-o <out>]

Options:
  -h --help
  -i,--input_file <inputVCF.vcf>        Input vcf files
  -s,--sample_name <sample_name>        Name of the sample(s) to be combined. If no sample names have not been provided
                                        all input files have to have matching sample names (order is not important).
                                        If the sample name is provided it must be in all input files. Otherwise, the
                                        error will occur.
  -f,--output_format <output_format>    Output file format: COMPRESSED, UNCOMPRESSED or SAME_AS_INPUT (default)
  -o,--out <out>                        Output file name
  -v,--verbose                          Printing test data to stderr [default: False]
## Usage examples
```
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -s NORMAL -f UNCOMPRESSED -o combined.vcf -v
Smart_combine_variants.py -i data/test/v1.vcf    -i data/test/v2.vcf -s NORMAL -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -s NORMAL -s TUMOR -f COMPRESSED -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -o combined.vcf -v
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -i v3.vcf -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf    -i data/test/v2.vcf.gz -v
```
In case there are none of the Sample names provided as an input, samples in all input files must be the same if present. 
If the output format is not provided in input command the format will be the same as the first input files. 
If the output file is not provided in the input command, stdout will be used.  
In no sample names have not been provided all samples from all input files must match (order is not important). 
It is important that if one sample is present in one file it must be present in all other input files. Sample names are
provided by writing -s in front of each sample name. The output file will have samples separated by a tab, as in input
files. 
