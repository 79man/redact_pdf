import logging
import sys
import argparse
from typing import Final
from pdf_redacter.core import PDFRedactor
from pdf_redacter.pattern_matcher import PatternType

DEFAULT_REPLACEMENT: Final = "***REDACTED***"
DEFAULT_IGN_CASE: Final = False
DEFAULT_VERBOSE: Final = False
DEFAULT_OVERWRITE: Final = False


def main():
    """
    Entry point for the PDF Redacter CLI.
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
        help="Path to the source PDF file. (Required)"
    )
    parser.add_argument(
        "-o", "--output_file",
        required=True,
        type=str,
        help="Path to save the output PDF. (Required)"
    )

    # Text to search and replace
    parser.add_argument(
        "-s", "--searches",
        nargs="+",
        type=str,
        help="Text to redact (multiple values allowed). Regex format is also allowed. (Optional)"
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
        help=f"Replacement text for redacted content. default=[{DEFAULT_REPLACEMENT}]"
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

    # Add to argument parser in cli.py
    parser.add_argument(
        "-P", "--predefined-patterns",
        nargs="*",
        choices=["email", "phone", "ssn", "credit_card"],
        help="Use predefined patterns for common redaction scenarios"
    )

    parser.add_argument(
        "--validate-patterns",
        action="store_true",
        default=True,
        help="Validate regex patterns before processing (default: True)"
    )

    parser.add_argument(
        "-d", "--pattern-info",
        action="store_true",
        help="Show stats about matched patterns before exit"
    )

    # Parse arguments
    args = parser.parse_args()

    if args.verbose:
        # Increase log levels
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(levelname)s - %(asctime)s : %(message)s"
        )
    else:
        logging.basicConfig(
            level=logging.INFO,  # Set logging level to INFO
            format="%(levelname)s - %(asctime)s : %(message)s"
        )

    # Create a logger
    logger = logging.getLogger(__name__)
    logger.debug(args)

    # Run the redaction process
    try:
        pdf_redactor_engine = PDFRedactor(
            src_file=args.src_file,
            dest_file=args.output_file,
            overwrite=args.overwrite
        )
        stats = pdf_redactor_engine.redact_pdf(
            needles=args.searches,
            replacement=args.replacement,
            ignore_case=args.ignore_case,            
            use_predefined_patterns=[PatternType(p) for p in (args.predefined_patterns or [])],
            validate_patterns=args.validate_patterns
        )       

        if stats and args.pattern_info:
            logger.info(stats)

    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
