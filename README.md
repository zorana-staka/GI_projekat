# Smart Combine Variants

Python tool for smart combining of genomic variants

SmartCombineVariants (SCV) is a Python tool that performs combining variants of two VCF files. The tool supports the combining of VCF originating from different variant callers and with different headers. SCV should also support the combining of VCFs with multiple samples. When samples do not match it is possible to configure which samples will be combined through an input key-value parameter.
Usage: Smart_combine_variants.py (-i <inputVCF.vcf>)... [-s <sample_name>]... [-f <output_format>] [-o <out>]

Options:
  -h --help
  -i,--input_file <inputVCF.vcf>       Input vcf files
  -s, --sample_name <sample_name>      Name of the sample(s) to be combined
  -f,--output_format <output_format>   Output file format: COMPRESSED, UNCOMPRESSED or SAME_AS_INPUT (default)
  -o,--out <out>                       Output file name

## Usage examples
```
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -s NORMAL -f UNCOMPRESSED -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf    -i data/test/v2.vcf -s NORMAL -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -s NORMAL -f COMPRESSED -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -i v3.vcf -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf    -i data/test/v2.vcf.gz
```
In case there are none of the Sample names provided as an input, samples in all input files must be the same if present. 
If the output format is not provided in input command the format will be the same format as the first input files. 
If the output file is not provided in the input command, stdout will be used. 
If not present special files with extension .scvidx or .scvtbi will be created, if not already present. 
