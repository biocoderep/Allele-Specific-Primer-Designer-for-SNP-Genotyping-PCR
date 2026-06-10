import os
import tempfile
import traceback
from pathlib import Path
from flask import Flask, render_template, request, send_file, jsonify

from allele_designer.io import read_fasta, read_snp_data
from allele_designer.core import design_inner_reverse_primers
import pandas as pd

app = Flask(__name__)
# Set maximum upload size to 50MB
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/design', methods=['POST'])
def design_primers():
    try:
        if 'fasta' not in request.files or 'snps' not in request.files:
            return jsonify({'error': 'Missing FASTA or SNPs file'}), 400
            
        fasta_file = request.files['fasta']
        snps_file = request.files['snps']
        
        primer_length = int(request.form.get('length', 20))
        
        if fasta_file.filename == '' or snps_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        # Create temporary directory to process files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            fasta_path = temp_dir_path / fasta_file.filename
            snps_path = temp_dir_path / snps_file.filename
            
            fasta_file.save(fasta_path)
            snps_file.save(snps_path)
            
            # Read inputs
            sequences = read_fasta(str(fasta_path))
            if not sequences:
                return jsonify({'error': 'No sequences found in FASTA file'}), 400
                
            snp_df = read_snp_data(str(snps_path))
            if snp_df is None or snp_df.empty:
                return jsonify({'error': 'No valid SNP data found in file'}), 400
                
            results_data = []
            success_count = 0
            error_count = 0
            
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
                
                if seq_name not in sequences:
                    result_row['Status'] = 'ERROR'
                    result_row['Error_Message'] = f"Sequence '{seq_name}' not found in FASTA file"
                    results_data.append(result_row)
                    error_count += 1
                    continue
                
                ref_primer, alt_primer = design_inner_reverse_primers(
                    sequences[seq_name], snp_pos, ref_allele, alt_allele, primer_length
                )
                
                if ref_primer is None or alt_primer is None:
                    result_row['Status'] = 'ERROR'
                    result_row['Error_Message'] = 'Failed to design primers'
                    results_data.append(result_row)
                    error_count += 1
                    continue
                
                result_row['Status'] = 'SUCCESS'
                result_row['Ref_Primer_Sequence'] = ref_primer
                result_row['Alt_Primer_Sequence'] = alt_primer
                
                results_data.append(result_row)
                success_count += 1
                
            results_df = pd.DataFrame(results_data)
            output_path = temp_dir_path / 'primers_output.xlsx'
            results_df.to_excel(output_path, index=False)
            
            return send_file(
                output_path, 
                as_attachment=True,
                download_name='primers_output.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
