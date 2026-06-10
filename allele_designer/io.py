import sys
from pathlib import Path

# Fix: Attempt to import pandas gracefully at the module level
try:
    import pandas as pd
except ImportError:
    print("Error: pandas is required to read Excel/CSV files.")
    print("Install it with: pip install pandas openpyxl")
    sys.exit(1)

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
