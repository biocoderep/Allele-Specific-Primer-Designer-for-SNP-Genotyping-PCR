Allele-Specific Primer Designer for SNP Genotyping PCR

A Python tool for designing allele-specific inner reverse primers for SNP genotyping PCR assays. This script processes FASTA sequences and SNP data from Excel/CSV files to generate reference and alternate allele-specific primers automatically.

Features
Reads DNA sequences from FASTA files
Reads SNP information from Excel (.xlsx, .xls) or CSV files
Designs allele-specific inner reverse primers
Generates separate primers for:
Reference allele
Alternate allele
Exports results to Excel format
Error handling for:
Missing sequences
Invalid SNP positions
Invalid nucleotides
Insufficient sequence length
Installation
Clone the Repository
git clone https://github.com/yourusername/allele-specific-primer-designer.git
cd allele-specific-primer-designer
Install Dependencies
pip install pandas openpyxl
Requirements
Python 3.7+
pandas
openpyxl
Installation
Clone the Repository
git clone https://github.com/yourusername/allele-specific-primer-designer.git
cd allele-specific-primer-designer
Install Dependencies
pip install pandas openpyxl
Requirements
Python 3.7+
pandas
openpyxl
Input File Formats
1. FASTA File

Example:
>seq1
ATGCGTACGTAGCTAGCTAGCTAGCTAGCTAGCTA

>seq2
CGTAGCTAGCTAGGCTAGCTAGCTAACGATCGATC
2. SNP File (Excel or CSV)

Required columns:
| sequence_name | snp_position | ref_allele | alt_allele |
| ------------- | ------------ | ---------- | ---------- |
| seq1          | 10           | A          | G          |
| seq2          | 15           | C          | T          |
Column Description
| Column          | Description             |
| --------------- | ----------------------- |
| `sequence_name` | Must match FASTA header |
| `snp_position`  | 1-based SNP position    |
| `ref_allele`    | Reference nucleotide    |
| `alt_allele`    | Alternate nucleotide    |
Usage
Basic Command
python script.py -f sequences.fasta -s snps.xlsx
Specify Primer Length
python script.py -f sequences.fasta -s snps.csv -l 25
Specify Output File
python script.py -f sequences.fasta -s snps.xlsx -o results.xlsx
Command-Line Arguments
Argument	Description
-f, --fasta	Input FASTA file
-s, --snps	SNP Excel/CSV file
-l, --length	Primer length (default: 20 bp)
-o, --output	Output Excel filename
Primer Design Logic

The script designs allele-specific inner reverse primers using the following method:

Extracts a sequence region starting at the SNP position
Takes reverse complement of the region
Modifies the 3′ terminal base to match:
Complement of reference allele
Complement of alternate allele

This creates allele-specific discrimination during PCR amplification.

Example Output
SNP_Number	Sequence_Name	SNP_Position	Ref_Allele	Alt_Allele	Ref_Primer_Sequence	Alt_Primer_Sequence	Status
1	seq1	10	A	G	ATCGTAGCTAGCTAGCTT	ATCGTAGCTAGCTAGCTC	SUCCESS
Error Handling

The script reports errors for:

SNP position outside sequence range
Sequence missing from FASTA file
Invalid nucleotide characters
Insufficient sequence length for primer generation

Errors are included in the output Excel file.

Output

The program generates an Excel file containing:

SNP information
Designed reference primer
Designed alternate primer
Status (SUCCESS or ERROR)
Error messages (if applicable)

Default output filename:

primers_output.xlsx
Example Workflow
python script.py \
    -f genome_sequences.fasta \
    -s snp_data.xlsx \
    -l 22 \
    -o designed_primers.xlsx
Future Improvements

Potential enhancements:

GC content calculation
Melting temperature (Tm) estimation
Primer dimer checking
Secondary structure prediction
Mismatch introduction at penultimate base
Support for tetra-primer ARMS-PCR
Batch visualization reports
Citation

If you use this tool in your research, please cite the repository or acknowledge the software in your publication.

License

This project is licensed under the MIT License.

Author

Developed for SNP genotyping and allele-specific PCR primer design workflows in bioinformatics and molecular biology research.

