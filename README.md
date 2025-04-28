# Variant Annotator

A simple Python CLI tool to annotate genetic variants using the Ensembl API.

## Setup

1. Install Python 3.6 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script with an input file containing RSIDs (one per line) and specify an output file:

```bash
python variant_annotator.py variants.txt annotations.tsv
```

The script will:
1. Read RSIDs from the input file
2. Send a single batch request to the Ensembl API
3. Create a TSV file with the following columns:
   - RSID
   - Start position
   - End position
   - Most severe consequence
   - List of affected genes

## Notes

- The script uses batch processing for efficiency
- If a variant cannot be found or there's an error, 'N/A' will be shown in the output
- For each variant, a unique list of genes is extracted from its transcript consequences
- Gene symbols are deduplicated and sorted alphabetically