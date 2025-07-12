# PDF Redacter Tool

This package supports redaction of text content from PDF files. It searches for specific text in a PDF document, replaces it with a replacement string, applies redaction, and saves the updated document. Additionally, the modified PDF is compressed for size optimization.

- [PDF Redacter Tool](#pdf-redacter-tool)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Command Syntax](#command-syntax)
  - [Configuration Files](#configuration-files)
  - [Example Commands](#example-commands)
    - [Basic Uasge](#basic-uasge)
    - [Using predefined patterns](#using-predefined-patterns)
    - [Configuration File Usage](#configuration-file-usage)
    - [Arguments](#arguments)
    - [Output](#output)
  - [Configuration File Examples](#configuration-file-examples)
    - [YAML Configuration (redaction\_config.yml)](#yaml-configuration-redaction_configyml)
    - [JSON Configuration (redaction\_config.json)](#json-configuration-redaction_configjson)
  - [Example Output Logs](#example-output-logs)
  - [Notes](#notes)
  - [Dependencies](#dependencies)
  - [Testing](#testing)
    - [Test Structure](#test-structure)
    - [Running Tests](#running-tests)
    - [Test Dependencies](#test-dependencies)
    - [Test Coverage](#test-coverage)
    - [Writing New Tests](#writing-new-tests)
  - [Notes](#notes-1)
    - [Wiki pages you might want to explore:](#wiki-pages-you-might-want-to-explore)


## Features
- Search and redact specific text in PDF files using custom regex patterns  
- Replace the redacted text with customizable replacement strings  
- Compress the redacted PDF for smaller file size  
- **Predefined pattern templates** for common redaction scenarios (email, phone, SSN, credit card)  
- **Configuration file support** (YAML/JSON) for reusable redaction settings  
- **Pattern validation** with detailed error messages  
- **Enhanced pattern matching** with caching and optimization  
- **Statistics tracking** showing redaction results and pattern usage  
- **Argument saving** to persist CLI settings for future use 

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
pdf_redacter [-h] [--config-file CONFIG_FILE] [--generate-sample-config GENERATE_SAMPLE_CONFIG]
             [--save-config SAVE_CONFIG] [-i SRC_FILE] [-o OUTPUT_FILE] [-s SEARCHES [SEARCHES ...]]
             [-c | --ignore-case | --no-ignore-case] [-r REPLACEMENT] [-v | --verbose | --no-verbose] 
             [-f | --overwrite | --no-overwrite] [-P [{email,phone,ssn,credit_card} ...]]
             [--validate-patterns | --no-validate-patterns] [-d | --print-stats | --no-print-stats]
```

## Configuration Files
You can use configuration files to store complex redaction settings and avoid repeating long command lines:

```bash
# Generate a sample (dummy) configuration file
pdf_redacter --generate-config my_config.yml
  
# Use configuration file (no overrides)
pdf_redacter --config my_config.yml -i document.pdf -o redacted.pdf  
  
# Use config with CLI overrides (verbose)
pdf_redacter --config my_config.yml -i document.pdf -o redacted.pdf --verbose
```
## Example Commands
### Basic Uasge
```shell
# Redact email addresses using custom regex
pdf_redacter -i input_test.pdf -o redacted_output.pdf -s "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}" -v -f
```
### Using predefined patterns
```shell
# Redact emails and phone numbers using predefined patterns
pdf_redacter -i document.pdf -o clean.pdf --predefined-patterns email phone -v  
  
# Combine custom patterns with predefined ones
pdf_redacter -i sensitive.pdf -o redacted.pdf -s "confidential" --predefined-patterns email ssn credit_card
```

### Configuration File Usage
```shell
# Save current arguments to config file  [header-8](#header-8)
pdf_redacter -i doc.pdf -o out.pdf -s "pattern1" "pattern2" --save-config my_settings.yml  
  
# Use saved configuration  [header-9](#header-9)
pdf_redacter --config my_settings.yml -i new_document.pdf -o new_output.pdf
```

### Arguments
```bash
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE
                        Path to configuration file (YAML or JSON)
  --generate-sample-config GENERATE_SAMPLE_CONFIG
                        Generate sample configuration file at specified path
  --save-config SAVE_CONFIG
                        Save Working Configuration to file at specified path
  -i SRC_FILE, --src_file SRC_FILE
                        Path to the source PDF file. (Required)
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Path to save the output PDF. (Required)
  -s SEARCHES [SEARCHES ...], --searches SEARCHES [SEARCHES ...]
                        Text to redact (multiple values allowed). Regex format is also allowed. (Optional)
  -c, --ignore-case, --no-ignore-case
                        Enable case-insensitive search for redaction, default=[False]
  -r REPLACEMENT, --replacement REPLACEMENT
                        Replacement text for redacted content. default=[***REDACTED***]
  -v, --verbose, --no-verbose
                        Increase output Verbosity, default=[False]
  -f, --overwrite, --no-overwrite
                        Overwrite destination PDF if it alreday exists, default=[False]
  -P [{email,phone,ssn,credit_card} ...], --predefined-patterns [{email,phone,ssn,credit_card} ...]
                        Use predefined patterns for common redaction scenarios
  --validate-patterns, --no-validate-patterns
                        Validate regex patterns before processing (default: True)
  -d, --print-stats, --no-print-stats
                        Show stats about matched patterns before exit
  --dry-run, --no-dry-run
                        Perform a dry run to validate settings, default=[False]
```

### Output
- `redacted_output.pdf`: The redacted PDF file.
- Optional statistics showing total matches, pages processed, and pattern usage.

## Configuration File Examples
### YAML Configuration (redaction_config.yml)
```yaml
# PDF Redaction Configuration
searches:  
  - "confidential"  
  - "proprietary"  
  - "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}"  # Email regex  
  - "\\b\\d{3}-\\d{2}-\\d{4}\\b"  # SSN regex  
  
predefined_patterns:  
  - "email"  
  - "phone"  
  - "ssn"  
  
replacement: "[REDACTED]"  
ignore_case: true  
verbose: true  
overwrite: false
```

### JSON Configuration (redaction_config.json)
```json
{  
  "searches": [  
    "confidential",  
    "proprietary",   
    "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}",  
    "\\b\\d{3}-\\d{2}-\\d{4}\\b"  
  ],  
  "predefined_patterns": ["email", "phone", "ssn"],  
  "replacement": "[REDACTED]",  
  "ignore_case": true,  
  "verbose": true,  
  "overwrite": false  
}
```

## Example Output Logs
```bash
pdf_redacter -i input_test.pdf -o redacted_output.pdf -s "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}" -v -f
```
```log
Setting log levels to DEBUG
DEBUG - 2025-07-11 20:06:55,961 : loaded from conf file: {}
DEBUG - 2025-07-11 20:06:55,961 : explicitly_provided in args: {'src_file', 'searches', 'verbose', 'output_file', 'overwrite'}
DEBUG - 2025-07-11 20:06:55,961 : Adding/overriding arg: src_file = input_test.pdf
DEBUG - 2025-07-11 20:06:55,961 : Adding/overriding arg: output_file = redacted_output.pdf
DEBUG - 2025-07-11 20:06:55,961 : Adding/overriding arg: searches = ['[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}']
DEBUG - 2025-07-11 20:06:55,961 : Adding/overriding arg: ignore_case = False
DEBUG - 2025-07-11 20:06:55,961 : Adding/overriding arg: replacement = ***REDACTED***
DEBUG - 2025-07-11 20:06:55,961 : Adding/overriding arg: verbose = True
DEBUG - 2025-07-11 20:06:55,961 : Adding/overriding arg: overwrite = True
DEBUG - 2025-07-11 20:06:55,961 : Adding/overriding arg: validate_patterns = True
DEBUG - 2025-07-11 20:06:55,969 : Adding/overriding arg: print_stats = False
DEBUG - 2025-07-11 20:06:55,969 : Adding/overriding arg: dry_run = False
DEBUG - 2025-07-11 20:06:55,969 : Adding/overriding arg: _explicitly_provided = {'src_file', 'searches', 'verbose', 'output_file', 'overwrite'}
DEBUG - 2025-07-11 20:06:55,970 : final_config: {'src_file': 'input_test.pdf', 'output_file': 'redacted_output.pdf', 'searches': ['[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}'], 'ignore_case': False, 'replacement': '***REDACTED***', 'verbose': True, 'overwrite': True, 'validate_patterns': True, 'print_stats': False, 'dry_run': False, '_explicitly_provided': {'src_file', 'searches', 'verbose', 'output_file', 'overwrite'}}
DEBUG - 2025-07-11 20:06:55,970 : Namespace(config_file=None, generate_sample_config=None, save_config=None, src_file='input_test.pdf', output_file='redacted_output.pdf', searches=['[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}'], ignore_case=False, replacement='***REDACTED***', verbose=True, overwrite=True, predefined_patterns=None, validate_patterns=True, print_stats=False, dry_run=False, _explicitly_provided={'src_file', 'searches', 'verbose', 'output_file', 'overwrite'})
DEBUG - 2025-07-11 20:06:55,971 : Loaded 1 patterns:
DEBUG - 2025-07-11 20:06:55,971 :   - Email Address: [A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}
Redacting: 100%|████████████████████████████████████████████████| 102/102 [00:01<00:00, 56.54page/s]
DEBUG - 2025-07-11 20:06:57,892 : PDF Redaction Completed. Total matches: 113
INFO - 2025-07-11 20:06:59,290 : PDF compression complete. Final file saved as 'redacted_output.pdf'.
INFO - 2025-07-11 20:06:59,313 : PDF redaction completed successfully
```

## Notes
- Redacted areas will have a white background with replacement text overlay
- Ensure you use proper file paths while providing arguments
- This redaction method only works for redacting text content in PDFs, not embedded images
- **Pattern validation** automatically checks regex syntax before processing
- **Configuration files** support both YAML and JSON formats
- **Predefined patterns** are optimized and tested for common redaction scenarios
- Use `--pattern-info` to see details about loaded patterns before processing
- **Pattern caching** improves performance for large documents with multiple patterns

## Dependencies
This package depends on the following Python libraries for PDF Manipulation:

- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/) - Handles PDF reading, text searching, and redaction.
- [PikePDF](https://pikepdf.readthedocs.io/en/latest/) - Used for compressing the pdf output.

## Testing
`pdf_redacter` includes comprehensive test coverage using pytest to ensure reliability and correctness of PDF redaction functionality.

### Test Structure
The testing suite covers:

- **Core functionality**: PDF redaction, pattern matching, and file handling
- **CLI interface**: Command-line argument parsing and execution
- **Configuration system**: YAML/JSON config file loading and validation
- **Enhanced features**: Predefined patterns, pattern validation, and statistics tracking
- **Error handling**: Invalid inputs, file permissions, and edge cases

### Running Tests
Install the package with test dependencies:

```bash
# Install with test dependencies  
pip install -e ".[test]"  
  
# Run all tests  
pytest  
  
# Run with coverage report  
pytest --cov=pdf_redacter  
  
# Run specific test categories  
pytest tests/test_core.py -v          # Core PDF processing tests  
pytest tests/test_cli.py -v           # CLI interface tests  
pytest tests/test_config.py -v        # Configuration system tests  
  
# Run tests with verbose output  
pytest -v --tb=short
```

### Test Dependencies
The testing framework requires additional dependencies that are automatically installed with the `[test]` extra:

- `pytest>=6.0` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities

### Test Coverage
The test suite includes:

- **Unit tests** for individual components and methods
- **Integration tests** for end-to-end workflows
- **Parametrized tests** for multiple pattern combinations
- **Fixture-based testing** for PDF file creation and cleanup
- **Mock testing** for CLI interface without actual file processing

### Writing New Tests
When contributing new features:

1. Add corresponding test cases in the appropriate test_*.py file
2. Use the provided fixtures for PDF creation and temporary directories
3. Follow the existing parametrized testing patterns for multiple scenarios
4. Ensure both positive and negative test cases are covered

This testing infrastructure ensures the reliability of the PDF redaction functionality across different use cases and environments.

## Notes
This testing documentation reflects the comprehensive pytest implementation discussed in the conversation history, including the test structure with conftest.py fixtures, parametrized testing for pattern matching, CLI mocking, and the resolution of PyMuPDF SWIG warnings. The section emphasizes the practical aspects users need to know for running and contributing to the tests.

### Wiki pages you might want to explore:
[Deepwiki User Guide (79man/redact_pdf)](https://deepwiki.com/79man/redact_pdf/2-user-guide)
