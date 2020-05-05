# smart_combine_variants
Python tool for smart combining of genomic variants

SmartCombineVariants (SCV) is a Python tool that performs combining variants of two VCF files. 
The tool supports the combining of VCF originating from different variant callers and with different headers. 
Information stored in headers of two VCF files should also be combined. 
SCV should also support the combining of VCFs with multiple samples. 
When samples do not match it is possible to configure which samples will be combined through an input key-value parameter.
Many different scenarios exist within combining variants and all of them should be resolved as in GATK CombineVariants 3.7 tool and according to VCF 4.2 standard. Input VCF files must be sorted and indexed to enable faster search and manipulation. Input VCFs are optionally compressed with Tabix tool (VCF.GZ). Indices must be provided as an input for both VCFs, .IDX for VCF or Tabix index (TBI) for compressed VCF. All necessary input arguments of SCV must be well documented. 
The entire code is published on Github under the MIT license.  
For each combine-VCFs scenario, write a set of test VCF files with few variants that would represent a manifest of that scenario. For example, VCF files with different INFO fields or one of the VCF files contain multiallelic variant (A -> T,C). The SCV code should be modular and every function should have a test code which proves its functionality.
Wrapp SCV in CWL and publish it as Public App on Cancer Genomics Cloud platform (send request it will be approved). Execute a few combine-VCFs scenarios as tasks on CGC platform. (10 points).
slides (Google Slides or Powerpoint presentation) with summarized work being done.

