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

1. Clone this repository or copy the script to your local machine:

   ```bash
   git clone <repository-url>
   cd <repository-folder># Redact PDF Tool

This tool provides redaction and compression capabilities for PDF files using PyMuPDF and PikePDF. It searches for specific text in a PDF document, replaces it with a replacement string, applies redaction, and saves the updated document. Additionally, the modified PDF is compressed for optimization.

## Features
- Search and redact specific text in PDF files.
- Replace the redacted text with customizable replacement strings.
- Compress the redacted PDF for smaller file size.

## Installation
To use this script, you need to have Python installed on your system along with the required dependencies.

1. Clone this repository or copy the script to your local machine:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Install the dependencies using pip:

    ```bash
    pip install pymupdf pikepdf
    ```
    or
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
python redact_pdf_tool.py input.pdf redacted_output.pdf "sensitive_text" "REDACTED"
```

## Arguments
- `input.pdf`: The source PDF file containing the text.
- `redacted_output.pdf`: The name of the file to which the redacted PDF will be saved.
- `sensitive_text`: Text to search for in the PDF document to be redacted.
- `REDACTED`: The replacement text that will replace the redacted area.

## Output
- `redacted_output.pdf`: The redacted PDF file.
- `redacted_output.pdf_compressed.pdf`: A compressed version of the redacted PDF for optimized size.

## Example Output Logs
```plaintext
Redaction complete. Saved as 'redacted_output.pdf'.
PDF compression complete. Saved as 'redacted_output.pdf_compressed.pdf'.
```

## Notes
- Redacted areas will have a white background.
- Ensure you use proper file paths while providing arguments.
- This redaction method only works for redacting text content in PDFs.

## Dependencies
The script uses the following Python libraries:

- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/) - Handles PDF reading, text searching, and redaction.
- [PikePDF](https://pikepdf.readthedocs.io/en/latest/) - Used for compressing the pdf output.

Install them with:
```bash
pip install pymupdf pikepdf
```
or
```bash
pip install -r requirements.txt
```
