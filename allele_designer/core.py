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
