import argparse
import sys
from pathlib import Path
from .io import read_fasta, read_snp_data
from .core import design_inner_reverse_primers

# we import pandas to save the results, it will already be checked in io.py
try:
    import pandas as pd
except ImportError:
    pass # handled in io.py

def main():
    parser = argparse.ArgumentParser(
        description="Design allele-specific inner reverse primers for SNP genotyping PCR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Input file formats:

1. FASTA file (-f): Contains sequences with headers
   >sequence_name1
   ATCGATCG...
   >sequence_name2
   GCTAGCTA...

2. SNP file (-s): Excel (.xlsx, .xls) or CSV file with columns:
   - sequence_name: Name matching FASTA headers
   - snp_position: 1-based position of SNP
   - ref_allele: Reference allele (A, T, G, or C)
   - alt_allele: Alternate allele (A, T, G, or C)

Examples:
   allele-designer -f sequences.fasta -s snps.xlsx -o results.xlsx
   allele-designer -f sequences.fasta -s snps.csv -l 25 -o results.xlsx
        """
    )
    
    # Required input files
    parser.add_argument('-f', '--fasta', type=str, required=True,
                       help='FASTA file containing sequences')
    parser.add_argument('-s', '--snps', type=str, required=True,
                       help='Excel or CSV file containing SNP data')
    
    # Primer design options
    parser.add_argument('-l', '--length', type=int, default=20,
                       help='Primer length in bp (default: 20)')
    parser.add_argument('-o', '--output', type=str,
                       help='Output file (default: primers_output.xlsx)')
    
    args = parser.parse_args()
    
    # Check if input files exist
    if not Path(args.fasta).exists():
        print(f"Error: FASTA file '{args.fasta}' not found")
        return 1
    
    if not Path(args.snps).exists():
        print(f"Error: SNP file '{args.snps}' not found")
        return 1
    
    # Read input files
    print("Reading FASTA file...")
    sequences = read_fasta(args.fasta)
    if not sequences:
        print("Error: No sequences found in FASTA file")
        return 1
    
    print(f"Found {len(sequences)} sequences in FASTA file")
    
    print("Reading SNP data...")
    snp_df = read_snp_data(args.snps)
    if snp_df is None or snp_df.empty:
        print("Error: No valid SNP data found")
        return 1
    
    print(f"Found {len(snp_df)} SNPs in data file")
    
    # Prepare data for Excel output
    results_data = []
    success_count = 0
    error_count = 0
    
    # Process each SNP
    for idx, row in snp_df.iterrows():
        seq_name = row['sequence_name']
        snp_pos = row['snp_position']
        ref_allele = row['ref_allele']
        alt_allele = row['alt_allele']
        
        result_row = {
            'SNP_Number': idx + 1,
            'Sequence_Name': seq_name,
            'SNP_Position': snp_pos,
            'Ref_Allele': ref_allele,
            'Alt_Allele': alt_allele,
            'Ref_Primer_Sequence': '',
            'Alt_Primer_Sequence': '',
            'Status': '',
            'Error_Message': ''
        }
        
        # Check if sequence exists
        if seq_name not in sequences:
            result_row['Status'] = 'ERROR'
            result_row['Error_Message'] = f"Sequence '{seq_name}' not found in FASTA file"
            results_data.append(result_row)
            error_count += 1
            continue
        
        # Design primers
        ref_primer, alt_primer = design_inner_reverse_primers(
            sequences[seq_name], snp_pos, ref_allele, alt_allele, args.length
        )
        
        if ref_primer is None or alt_primer is None:
            result_row['Status'] = 'ERROR'
            result_row['Error_Message'] = 'Failed to design primers'
            results_data.append(result_row)
            error_count += 1
            continue
        
        # Fill in successful results
        result_row['Status'] = 'SUCCESS'
        result_row['Ref_Primer_Sequence'] = ref_primer
        result_row['Alt_Primer_Sequence'] = alt_primer
        
        results_data.append(result_row)
        success_count += 1
    
    # Create DataFrame and save to Excel
    results_df = pd.DataFrame(results_data)
    
    # Determine output filename
    if args.output:
        excel_filename = args.output
        if not excel_filename.endswith(('.xlsx', '.xls')):
            excel_filename += '.xlsx'
    else:
        excel_filename = 'primers_output.xlsx'
    
    # Save to Excel
    try:
        results_df.to_excel(excel_filename, index=False)
    except Exception as e:
        print(f"Error saving to Excel: {e}")
        print("Note: saving to .xlsx requires 'openpyxl'. Try: pip install openpyxl")
        return 1
    
    print(f"\nResults saved to: {excel_filename}")
    print(f"Successfully designed primers for: {success_count} SNPs")
    print(f"Errors encountered: {error_count} SNPs")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
