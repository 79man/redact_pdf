import os
# import re
from pdf_redacter.pattern_matcher import EnhancedPatternMatcher, PatternType
import fitz  # PyMuPDF
import pikepdf
import tempfile
from pathlib import Path

from tqdm import tqdm
from typing import List, Optional

import logging

# Create a logger
logger = logging.getLogger(__name__)


class PDFRedactor:
    def __init__(
            self,
            src_file: str,
            dest_file: str,
            overwrite: bool = False
    ):
        """
        Initialize the PDFRedactor class with file paths and settings.

        Args:
                src_file (str): The input PDF file to process.
                dest_file (str): The output PDF file path for the redacted version.
                overwrite (bool): Whether to overwrite the destination file if it already exists.
        """
        self.src_file = src_file
        self.dest_file = dest_file
        self.overwrite = overwrite

        # Validate input and output paths
        self._validate_paths()

    def _validate_paths(self):
        """Check the validity of input and output file paths."""
        if not self.src_file or not os.path.isfile(self.src_file):
            logger.error(f"Source file '{self.src_file}' not found")
            raise FileNotFoundError(f"Source file '{self.src_file}' not found")

        if not self.dest_file:
            logger.error(f"Valid Destination file not specified")
            raise FileNotFoundError(f"Valid Destination file not specified")

        if not self.overwrite and os.path.exists(self.dest_file):
            logger.error(f"Destination file '{self.dest_file}' already exists")
            raise FileExistsError(
                f"Destination file '{self.dest_file}' already exists")

    def redact_pdf(
            self,
            needles: List[str],
            replacement: str,
            ignore_case: bool,
            predefined_patterns: Optional[List[PatternType]] = None,
            validate_patterns: bool = True
    ) -> dict | None:
        """
        Redact text in the PDF file and save the compressed output.

        This function extracts text from a PDF, searches for patterns using regex, and redacts
        matching text. The redacted PDF is saved in a compressed format.

        Args:
                needles (list): List of strings or regex patterns to match text for redaction.
                replacement (str): The string to replace matched text (defaults to an empty string).
                ignore_case (bool): Whether the search for patterns should be case-insensitive.
                predefined_patterns Optional[List[PatternType]]: Support for Pattern Templates for commonly used patterns
                validate_patterns (bool): Enforce pattern validation.
        """

        # Initialize enhanced pattern matcher
        pattern_matcher = EnhancedPatternMatcher()

        # Validate patterns if requested
        if needles and validate_patterns:
            validation_errors = pattern_matcher.validate_patterns(needles)
            if validation_errors:
                for error in validation_errors:
                    logger.error(error)
                return None

        # Add predefined patterns (if specified)
        if predefined_patterns:
            for pattern_type in predefined_patterns:
                try:
                    pattern_matcher.add_predefined_pattern(
                        pattern_type,
                        ignore_case
                    )
                    logger.debug(
                        f"Added predefined pattern: {pattern_type.value}")
                except ValueError as e:
                    logger.error(f"Failed to add predefined pattern: {e}")
                    return None

        # Add custom patterns
        if needles:
            for needle in needles:
                try:
                    pattern_matcher.add_pattern(needle, ignore_case)
                except ValueError as e:
                    logger.error(f"Failed to compile pattern '{needle}': {e}")
                    return None

        # Log pattern information
        pattern_info = pattern_matcher.get_pattern_info()
        logger.debug(f"Loaded {len(pattern_info)} patterns:")
        for info in pattern_info:
            logger.debug(f"  - {info['name']}: {info['pattern']}")

        # Check if custom patterns list and predefined patterns list both are empty
        if len(pattern_info) <= 0:
            logger.error("No valid Search patterns specified")
            # raise ValueError("Search pattern cannot be empty")
            return

        # Statistics tracking
        stats = {
            "total_matches": 0,
            "pages_processed": 0,
            "pages_modified": 0,
            "patterns_used": len(pattern_info),
            "matches_by_pattern": {}
        }

        try:
            # Open the PDF
            doc: fitz.Document = fitz.open(self.src_file)
            total_pages = len(doc)  # Get the total number of pages in the PDF

            # Iterate through pages and search for the text
            for page_num, page in tqdm(
                    enumerate(doc.pages()),
                    total=total_pages,
                    desc="Redacting",
                    unit="page"
            ):
                # Convert the page text to a string using page.get_text()
                page_text = page.get_text()
                page_matches = 0

                # Find all matches using enhanced matcher
                matches = pattern_matcher.find_matches(page_text)

                for start_idx, end_idx, matched_text, pattern in matches:
                    # Track statistics
                    stats["total_matches"] += 1
                    page_matches += 1

                    if pattern not in stats["matches_by_pattern"]:
                        stats["matches_by_pattern"][pattern] = 0
                    stats["matches_by_pattern"][pattern] += 1

                    # Apply redaction (existing logic)
                    text_instances = page.search_for(matched_text)
                    for inst in text_instances:
                        page.add_redact_annot(
                            inst, replacement, fill=(1, 1, 1))

                # Only apply redactions if there were matches on this page
                if page_matches > 0:
                    page.apply_redactions()
                    stats["pages_modified"] += 1
                    # logger.debug(f"Page {page_num + 1}: Applied {page_matches} redactions")

                stats["pages_processed"] += 1

                # if page_matches > 0:
                #     logger.debug(
                #         f"Page {page_num + 1}: {page_matches} matches found")

            # Save the modified PDF to a temporary file
            # with tempfile.TemporaryDirectory() as tmpdir:
            #     temp_file = Path(tmpdir) / f"{Path(self.dest_file).stem}_temp.pdf"

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                temp_file = tmp.name

            # temp_file = f"{self.dest_file}_temp.pdf"
            doc.save(temp_file)
            logger.debug(
                f"PDF Redaction Completed. Total matches: {stats['total_matches']}")

            # Open the temporary file with PikePDF and compress it
            with pikepdf.open(temp_file) as pdf:
                pdf.save(self.dest_file, compress_streams=True)
                logger.info(
                    f"PDF compression complete. Final file saved as '{self.dest_file}'.")

            # Remove the temporary file
            os.unlink(temp_file)
            return stats

        except Exception as e:
            logger.exception(f"An error occurred: {str(e)}")
            return None
