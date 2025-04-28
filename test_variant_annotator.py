import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from variant_annotator import get_gene_symbols_from_variant, process_variants

class TestVariantAnnotator(unittest.TestCase):
    def test_get_gene_symbols_from_variant(self):
        """Test gene extraction from variant data."""
        # Test cases in one go
        test_cases = [
            ({'transcript_consequences': [{'gene_symbol': 'GENE1'}]}, ['GENE1']),
            ({'transcript_consequences': [{'gene_symbol': 'GENE1'}, {'gene_symbol': 'GENE1'}]}, ['GENE1']),
            ({'transcript_consequences': [{'gene_symbol': 'GENE1'}, {'gene_symbol': 'GENE2'}]}, ['GENE1', 'GENE2']),
            ({'transcript_consequences': []}, [])
        ]
        
        for variant_data, expected in test_cases:
            self.assertEqual(get_gene_symbols_from_variant(variant_data), expected)

    @patch('variant_annotator.requests.post')
    def test_full_process(self, mock_post):
        """Test complete workflow with mocked API."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                'id': 'rs1',
                'start': 100,
                'end': 100,
                'most_severe_consequence': 'missense_variant',
                'transcript_consequences': [{'gene_symbol': 'GENE1'}]
            }
        ]
        mock_post.return_value = mock_response

        # Create test files
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as input_file:
            input_file.write("rs1\n")
            input_path = input_file.name

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as output_file:
            output_path = output_file.name

        try:
            # Run the process
            process_variants(input_path, output_path)

            # Verify output
            with open(output_path, 'r') as f:
                lines = f.readlines()
            
            self.assertEqual(lines[0].strip(), 'RSID\tStart\tEnd\tMost Severe Consequence\tGenes')
            self.assertEqual(lines[1].strip(), 'rs1\t100\t100\tmissense_variant\tGENE1')

        finally:
            # Cleanup
            os.unlink(input_path)
            os.unlink(output_path)

if __name__ == '__main__':
    unittest.main() 