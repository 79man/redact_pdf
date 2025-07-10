import os
import re

import fitz  # PyMuPDF
import pikepdf

from tqdm import tqdm
from typing import List 

import logging

# Create a logger
logger = logging.getLogger(__name__)


class PDFRedactor:
    def __init__(self, src_file: str, dest_file: str, overwrite: bool = False):
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
        if not os.path.isfile(self.src_file):
            logger.error(f"Source file '{self.src_file}' not found")
            raise FileNotFoundError(f"Source file '{self.src_file}' not found")

        if not self.overwrite and os.path.exists(self.dest_file):
            logger.error(f"Destination file '{self.dest_file}' already exists")
            raise FileExistsError(
                f"Destination file '{self.dest_file}' already exists")

    def redact_pdf(
        self,        
        needles: List[str],
        replacement: str,
        ignore_case: bool        
    ) -> None:
        """
        Redact text in the PDF file and save the compressed output.

        This function extracts text from a PDF, searches for patterns using regex, and redacts 
        matching text. The redacted PDF is saved in a compressed format.

        Args:
            needles (list): List of strings or regex patterns to match text for redaction.
            replacement (str): The string to replace matched text (defaults to an empty string).
            ignore_case (bool): Whether the search for patterns should be case-insensitive.
        """

        # Check if needles list is not empty
        if not needles:
            logger.error("Search pattern cannot be empty")
            # raise ValueError("Search pattern cannot be empty")
            return

        try:
            # Open the PDF
            doc: fitz.Document = fitz.open(self.src_file)
            total_pages = len(doc)  # Get the total number of pages in the PDF

            # Compile regex patterns if ignore_case is enabled
            if ignore_case:
                needles_to_process = [re.compile(needle, re.IGNORECASE) for needle in needles]
            else:
                needles_to_process = [re.compile(needle) for needle in needles]

            logger.info(f"Regex patterns: {needles}")

            # Iterate through pages and search for the text
            for page_num, page in tqdm(
                enumerate(doc.pages()),
                total=total_pages,
                desc="Redacting",
                unit="page"
            ):
                # Convert the page text to a string using page.get_text()
                page_text = page.get_text()

                for pattern in needles_to_process:
                    for match in pattern.finditer(page_text):
                        start_idx, end_idx = match.span()

                        # Locate quads (bounding boxes) for the matched text
                        text_instances = page.search_for(
                            # Find the exact string
                            page_text[start_idx:end_idx])
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
            temp_file = f"{self.dest_file}_temp.pdf"
            doc.save(temp_file)
            logger.info(f"PDF Redaction Completed.")

            # Open the temporary file with PikePDF and compress it
            with pikepdf.open(temp_file) as pdf:
                pdf.save(self.dest_file, compress_streams=True)
                logger.info(
                    f"PDF compression complete. Final file saved as '{self.dest_file}'.")

            # Remove the temporary file
            os.remove(temp_file)

        except Exception as e:
            logger.exception(f"An error occurred: {str(e)}")
            return None
