# PDF Redacter Tool

This package supports redaction of text content from PDF files. It searches for specific text in a PDF document, replaces it with a replacement string, applies redaction, and saves the updated document. Additionally, the modified PDF is compressed for size optimization.

- [PDF Redacter Tool](#pdf-redacter-tool)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Command Syntax](#command-syntax)
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
    pip install .
    ```

## Usage
The tool exposes a CLI command named pdf_redacter. Use this command to process PDF files via the command line.

### Command Syntax
```shell
pdf_redacter -i SRC_FILE -o OUTPUT_FILE -s SEARCHES [SEARCHES ...] [-c] [-r REPLACEMENT] [-v] [-f]
```

## Example Command
```bash
# The following example redacts all email addresses from input_test.pdf and saves the compressed redacted version in redacted_output.pdf:

pdf_redacter -i input_test.pdf -o redacted_output.pdf -s "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}" -v -f
```

### Arguments
```shell
  -h, --help            show this help message and exit
  -i SRC_FILE, --src_file SRC_FILE
                        Path to the source PDF file. (Required)
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Path to save the output PDF. (Required)
  -s SEARCHES [SEARCHES ...], --searches SEARCHES [SEARCHES ...]
                        Text to redact (multiple values allowed). Regex format is also allowed. (Required)
  -c, --ignore-case     Enable case-insensitive search for redaction, default=[False]
  -r REPLACEMENT, --replacement REPLACEMENT
                        Replacement text for redacted content. default=[***REDACTED***]
  -v, --verbose         Increase output Verbosity, default=[False]
  -f, --overwrite       Overwrite destination PDF if it alreday exists, default=[False]
  -P [{email,phone,ssn,credit_card} ...], --predefined-patterns [{email,phone,ssn,credit_card} ...]
                        Use predefined patterns for common redaction scenarios
  --validate-patterns   Validate regex patterns before processing (default: True)
  -d, --pattern-info    Show stats about matched patterns before exit
```

### Output
- `redacted_output.pdf`: The redacted PDF file.

## Example Output Logs
```bash
pdf_redacter -i input_test.pdf -o redacted_output.pdf -s "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}" -v -f
```
```log
INFO - YYYY-MM-DD HH:MM:SS,msec : Namespace(src_file='input_test.pdf', output_file='output_test.pdf', searches=['[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}'], ignore_case=False, replacement='***REDACTED***', verbose=True, overwrite=True)
INFO - YYYY-MM-DD HH:MM:SS,msec : Regex patterns: [re.compile('[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}')]
Redacting: 100%|████████████████████████████████████████████████████████| 102/102 [00:01<00:00, 55.27page/s]
INFO - YYYY-MM-DD HH:MM:SS,msec : PDF Redaction Completed.
INFO - YYYY-MM-DD HH:MM:SS,msec : PDF compression complete. Final file saved as 'output_test.pdf'.
```

## Notes
- Redacted areas will have a white background.
- Ensure you use proper file paths while providing arguments.
- This redaction method only works for redacting text content in PDFs.

## Dependencies
This package uses the following Python libraries:

- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/) - Handles PDF reading, text searching, and redaction.
- [PikePDF](https://pikepdf.readthedocs.io/en/latest/) - Used for compressing the pdf output.

