# Redact PDF Tool

This tool supports redaction of text content from PDF files. It searches for specific text in a PDF document, replaces it with a replacement string, applies redaction, and saves the updated document. Additionally, the modified PDF is compressed for size optimization.

- [Redact PDF Tool](#redact-pdf-tool)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Example Command](#example-command)
    - [Arguments](#arguments)
    - [Output](#output)
  - [Example Output Logs](#example-output-logs)
  - [Notes](#notes)
  - [Dependencies](#dependencies)


## Features
- Search and redact specific text in PDF files.
- Replace the redacted text with customizable replacement strings.
- Compress the redacted PDF for smaller file size.

## Installation
To use this script, you need to have Python installed on your system along with the required dependencies.

1. Clone this repository:
   ```bash
   git clone https://github.com/79man/redact_pdf
   cd redact_pdf
   ```
2. Install the dependencies using pip:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
The script can be run via the command-line interface. The following arguments are required:
- `src_file`: The source PDF file you want to redact.
- `dest_file`: The destination file to save the redacted PDF.
- `needle`: The text you want to search for and redact.
- `replacement`: The text that will replace the redacted text.

## Example Command
```bash
# Search all email addresses in input_test.pdf and replace with ***REDACTED***
python redact_pdf.py -i input_test.pdf -o redacted_output.pdf -s "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}" -v -f
```

### Arguments
```
  -h, --help            show this help message and exit
  -i SRC_FILE, --src_file SRC_FILE
                        Path to the source PDF file.
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Path to save the output PDF.
  -s SEARCHES [SEARCHES ...], --searches SEARCHES [SEARCHES ...]
                        Text to redact (multiple values allowed). Regex format is also allowed
  -c, --ignore-case     Enable case-insensitive search for redaction, default=[False]
  -r REPLACEMENT, --replacement REPLACEMENT
                        Replacement text for redacted content. Leave empty for no replacement.
  -v, --verbose         Increase output Verbosity, default=[False]
  -f, --overwrite       Overwrite destination PDF if it alreday exists, default=[False]
```

### Output
- `redacted_output.pdf`: The redacted PDF file.

## Example Output Logs
```bash
$ python redact_pdf.py -i input_test.pdf -o redacted_output.pdf -s "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}" -v -f
Redacting: 100%|████████████████████████████████████████████████| 102/102 [00:01<00:00, 70.50page/s]
PDF Redaction Completed.
PDF compression complete. Final file saved as 'redacted_output.pdf'.
```

## Notes
- Redacted areas will have a white background.
- Ensure you use proper file paths while providing arguments.
- This redaction method only works for redacting text content in PDFs.

## Dependencies
The script uses the following Python libraries:

- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/) - Handles PDF reading, text searching, and redaction.
- [PikePDF](https://pikepdf.readthedocs.io/en/latest/) - Used for compressing the pdf output.

