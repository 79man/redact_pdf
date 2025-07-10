import sys
import os
import re

import fitz  # PyMuPDF
import pikepdf

from tqdm import tqdm
import argparse
import tempfile
from typing import Final

DEFAULT_REPLACEMENT: Final = "***REDACTED***"
DEFAULT_IGN_CASE: Final = False
DEFAULT_VERBOSE: Final = False
DEFAULT_OVERWRITE: Final = False

def redact_pdf(
    src_file: str,
    dest_file: str,
    needles: list,
    replacement: str,
    ignore_case: bool,
    verbose: bool = False,
    overwrite:bool = False
) -> None:
    """
    Redact text in a PDF file and save the compressed output.

    This function extracts text from a PDF, searches for patterns using regex, and redacts 
    matching text. The redacted PDF is saved in a compressed format.

    Args:
        src_file (str): The input PDF file to process.
        dest_file (str): The output PDF file path for the redacted version.
        needles (list): List of strings or regex patterns to match text for redaction.
        replacement (str): The string to replace matched text (defaults to an empty string).
        ignore_case (bool): Whether the search for patterns should be case-insensitive.
    """

    # Check if src_file and dest_file are valid file paths
    if not os.path.isfile(src_file):
        raise FileNotFoundError(f"Source file '{src_file}' not found")

    if not overwrite:
        if os.path.exists(dest_file):
            raise FileExistsError(f"Destination file '{dest_file}' already exists")

    # Check if needles list is not empty
    if not needles:
        raise ValueError("Needles list cannot be empty")
    try:
        # Open the PDF
        doc: fitz.Document = fitz.open(src_file)
        total_pages = len(doc)  # Get the total number of pages in the PDF

        # Compile regex patterns if ignore_case is enabled
        if ignore_case:
            needles = [re.compile(needle, re.IGNORECASE) for needle in needles]
        else:
            needles = [re.compile(needle) for needle in needles]

        if verbose:
            print(f"Regex patterns: {needles}")

        # Iterate through pages and search for the text
        for page_num, page in tqdm(
            enumerate(doc.pages()),
            total=total_pages,
            desc="Redacting",
            unit="page"
        ):
            # Convert the page text to a string using page.get_text()
            page_text = page.get_text()

            for pattern in needles:
                for match in pattern.finditer(page_text):
                    start_idx, end_idx = match.span()

                    # Locate quads (bounding boxes) for the matched text
                    text_instances = page.search_for(
                        page_text[start_idx:end_idx])  # Find the exact string
                    for inst in text_instances:
                        # Apply redaction over the found pattern
                        page.add_redact_annot(
                            inst,
                            replacement,
                            fill=(1, 1, 1)
                        )

            # Apply the redactions
            page.apply_redactions()

        # Save the modified PDF to a temporary file
        temp_file = f"{dest_file}_temp.pdf"
        doc.save(temp_file)
        print(f"PDF Redaction Completed.")

        # Open the temporary file with PikePDF and compress it
        with pikepdf.open(temp_file) as pdf:
            pdf.save(dest_file, compress_streams=True)
            print(
                f"PDF compression complete. Final file saved as '{dest_file}'.")

        # Remove the temporary file
        os.remove(temp_file)

    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    Main function to parse arguments and run the redaction process.
    """
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="A tool to redact text in PDFs with support for case-insensitive and regex searches."
    )

    # Input and output file arguments
    parser.add_argument(
        "-i", "--src_file",
        required=True,
        type=str,
        help="Path to the source PDF file."
    )
    parser.add_argument(
        "-o", "--output_file",
        required=True,
        type=str,
        help="Path to save the output PDF."
    )

    # Text to search and replace
    parser.add_argument(
        "-s", "--searches",
        nargs="+",
        required=True,
        type=str,
        help="Text to redact (multiple values allowed). Regex format is also allowed"
    )    

    # Flag for case-insensitive search
    parser.add_argument(
        "-c", "--ignore-case",
        action="store_true",
        default=DEFAULT_IGN_CASE,
        help=f"Enable case-insensitive search for redaction, default=[{DEFAULT_IGN_CASE}]"
    )

    parser.add_argument(
        "-r", "--replacement",
        type=str,
        action="store",
        default=DEFAULT_REPLACEMENT,
        help="Replacement text for redacted content. Leave empty for no replacement."
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=DEFAULT_VERBOSE,
        help=f"Increase output Verbosity, default=[{DEFAULT_VERBOSE}]"
    )

    parser.add_argument(
        "-f", "--overwrite",
        action="store_true",
        default=DEFAULT_OVERWRITE,
        help=f"Overwrite destination PDF if it alreday exists, default=[{DEFAULT_OVERWRITE}]"
    )

    # Parse arguments
    args = parser.parse_args()

    if args.verbose:
        print(args)

    if args.replacement is None:
        print("Error: Replacement value for -r/--replacement is missing!", file=sys.stderr)
        sys.exit(1)

    # Run the redaction process
    try:
        redact_pdf(
            src_file=args.src_file,
            dest_file=args.output_file,
            needles=args.searches,
            replacement=args.replacement,
            ignore_case=args.ignore_case,
            verbose=args.verbose,
            overwrite=args.overwrite
        )
    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
