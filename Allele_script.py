#!/usr/bin/env python3
"""
Allele-Specific Primer Designer for SNP Genotyping PCR
Designs inner reverse primers for reference and alternate alleles
Takes FASTA file for sequences and Excel/CSV file for SNP data
"""

import argparse
import sys
import pandas as pd
from pathlib import Path

def reverse_complement(sequence):
    """
    Return the reverse complement of a DNA sequence
    """
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 
                  'a': 't', 't': 'a', 'g': 'c', 'c': 'g',
                  'N': 'N', 'n': 'n'}
    
    try:
        rev_comp = ''.join(complement[base] for base in reversed(sequence))
        return rev_comp
    except KeyError as e:
        print(f"Error: Invalid nucleotide '{e.args[0]}' found in sequence")
        return None

def design_inner_reverse_primers(sequence, snp_position, ref_allele, alt_allele, primer_length=20):
    """
    Design allele-specific inner reverse primers
    
    1. Take sequence starting from SNP position for primer_length bp
    2. Get reverse complement of this sequence  
    3. Replace the last base (3' end) with complement of ref/alt allele
    
    Args:
        sequence (str): Reference DNA sequence
        snp_position (int): 1-based position of SNP
        ref_allele (str): Reference allele nucleotide
        alt_allele (str): Alternate allele nucleotide
        primer_length (int): Length of primer (default 20 bp)
    
    Returns:
        tuple: (ref_primer, alt_primer) or (None, None) if error
    """
    
    # Convert to 0-based indexing
    snp_pos_0based = snp_position - 1
    
    # Check if SNP position is valid
    if snp_pos_0based < 0 or snp_pos_0based >= len(sequence):
        print(f"Error: SNP position {snp_position} is out of range for sequence length {len(sequence)}")
        return None, None
    
    # Check if we have enough sequence from SNP position onwards
    primer_end_pos = snp_pos_0based + primer_length
    if primer_end_pos > len(sequence):
        print(f"Error: Not enough sequence from SNP position for {primer_length}bp primer")
        return None, None
    
    # Extract sequence from SNP position for primer_length bp
    primer_region = sequence[snp_pos_0based:primer_end_pos]
    
    # Get reverse complement of the primer region
    base_primer_rc = reverse_complement(primer_region)
    if base_primer_rc is None:
        return None, None
    
    # Get complements of the alleles
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
    ref_complement = complement.get(ref_allele.upper())
    alt_complement = complement.get(alt_allele.upper())
    
    if ref_complement is None or alt_complement is None:
        print(f"Error: Invalid alleles - ref: {ref_allele}, alt: {alt_allele}")
        return None, None
    
    # The SNP base (first base of primer_region) becomes the last base after reverse complement
    # Replace this last base (3' end) with complement of respective alleles
    ref_primer = base_primer_rc[:-1] + ref_complement
    alt_primer = base_primer_rc[:-1] + alt_complement
    
    return ref_primer, alt_primer

def read_fasta(file_path):
    """
    Read FASTA file and return dictionary of sequences
    """
    sequences = {}
    current_name = None
    current_seq = ""
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                # Save previous sequence if exists
                if current_name is not None:
                    sequences[current_name] = current_seq
                # Start new sequence
                current_name = line[1:].split()[0]  # Take first word after >
                current_seq = ""
            else:
                current_seq += line.upper()
    
    # Save last sequence
    if current_name is not None:
        sequences[current_name] = current_seq
    
    return sequences

def read_snp_data(file_path):
    """
    Read SNP data from Excel or CSV file
    Expected columns: sequence_name, snp_position, ref_allele, alt_allele
    """
    
    file_ext = Path(file_path).suffix.lower()
    
    try:
        if file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif file_ext == '.csv':
            df = pd.read_csv(file_path)
        else:
            print(f"Error: Unsupported file format '{file_ext}'. Use .xlsx, .xls, or .csv")
            return None
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return None
    
    # Check required columns
    required_cols = ['sequence_name', 'snp_position', 'ref_allele', 'alt_allele']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"Error: Missing required columns: {missing_cols}")
        print(f"Available columns: {list(df.columns)}")
        print(f"Required columns: {required_cols}")
        return None
    
    # Clean and validate data
    df = df.dropna(subset=required_cols)
    
    # Convert data types
    try:
        df['snp_position'] = df['snp_position'].astype(int)
        df['ref_allele'] = df['ref_allele'].astype(str).str.upper().str.strip()
        df['alt_allele'] = df['alt_allele'].astype(str).str.upper().str.strip()
        df['sequence_name'] = df['sequence_name'].astype(str).str.strip()
    except Exception as e:
        print(f"Error processing data types: {e}")
        return None
    
    # Validate alleles are single nucleotides
    valid_nucleotides = {'A', 'T', 'G', 'C'}
    invalid_ref = ~df['ref_allele'].isin(valid_nucleotides)
    invalid_alt = ~df['alt_allele'].isin(valid_nucleotides)
    
    if invalid_ref.any():
        print(f"Warning: Invalid reference alleles found: {df.loc[invalid_ref, 'ref_allele'].unique()}")
    if invalid_alt.any():
        print(f"Warning: Invalid alternate alleles found: {df.loc[invalid_alt, 'alt_allele'].unique()}")
    
    # Filter out invalid alleles
    df = df[df['ref_allele'].isin(valid_nucleotides) & df['alt_allele'].isin(valid_nucleotides)]
    
    return df

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
   python script.py -f sequences.fasta -s snps.xlsx -o results.xlsx
   python script.py -f sequences.fasta -s snps.csv -l 25 -o results.xlsx
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
    results_df.to_excel(excel_filename, index=False)
    
    print(f"\nResults saved to: {excel_filename}")
    print(f"Successfully designed primers for: {success_count} SNPs")
    print(f"Errors encountered: {error_count} SNPs")
    
    return 0

if __name__ == "__main__":
    # Check if pandas is available
    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas is required to read Excel/CSV files.")
        print("Install it with: pip install pandas openpyxl")
        sys.exit(1)
    
    sys.exit(main())
