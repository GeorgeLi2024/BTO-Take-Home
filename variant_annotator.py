import sys
import requests
import csv
from typing import List, Dict, Optional

def read_rsids_from_file(file_path: str) -> List[str]:
    """Read RSIDs from input file, one per line."""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def get_variants_from_api(rsids: List[str]) -> Dict[str, Optional[Dict]]:
    """Fetch variant data from Ensembl API in a single batch request."""
    url = "https://rest.ensembl.org/vep/human/id"
    headers = {"Content-Type": "application/json"}
    
    try:
        # Send all RSIDs in one POST request
        response = requests.post(url, headers=headers, json={"ids": rsids})
        response.raise_for_status()
        api_response = response.json()
        
        # Take the first variant from API response for each RSID
        rsid_to_variant_data = {}
        seen_rsids = set()
        for variant in api_response:
            if variant and 'id' in variant and variant['id'] not in seen_rsids:
                rsid_to_variant_data[variant['id']] = variant
                seen_rsids.add(variant['id'])
                
        return rsid_to_variant_data
    except requests.exceptions.RequestException:
        # If API call fails, return None for all RSIDs
        return {rsid: None for rsid in rsids}

def get_gene_symbols_from_variant(variant_data: Dict) -> List[str]:
    """Extract unique gene symbols from the first variant's transcript consequences."""
    genes = set()
    transcript_consequences = variant_data.get('transcript_consequences', [])
    if transcript_consequences:
        for transcript in transcript_consequences:
            if 'gene_symbol' in transcript:
                genes.add(transcript['gene_symbol'])
    return sorted(list(genes))

def process_variants(input_file: str, output_file: str) -> None:
    """Process variants and write results to TSV file."""
    # Read input and get variant data from API in one batch
    rsids = read_rsids_from_file(input_file)
    rsid_to_variant_data = get_variants_from_api(rsids)
    
    # Write TSV with headers
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['RSID', 'Start', 'End', 'Most Severe Consequence', 'Genes'])
        
        # Process each RSID in input file order to maintain original sequence
        # and ensure we handle missing variants (write N/A)
        for rsid in rsids:
            variant_data = rsid_to_variant_data.get(rsid)
            if variant_data:
                # Extract genes and write all fields from API response
                genes = get_gene_symbols_from_variant(variant_data)
                writer.writerow([
                    rsid,
                    variant_data.get('start', 'N/A'),
                    variant_data.get('end', 'N/A'),
                    variant_data.get('most_severe_consequence', 'N/A'),
                    ', '.join(genes) if genes else 'N/A'
                ])
            else:
                # Write N/A for variants not found in API response
                writer.writerow([rsid, 'N/A', 'N/A', 'N/A', 'N/A'])

def main():
    """Main function to run the variant annotator."""
    if len(sys.argv) != 3:
        print("Usage: python variant_annotator.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    process_variants(input_file, output_file)
    print(f"Results written to {output_file}")

if __name__ == "__main__":
    main()