import sys
import os

import fitz  # PyMuPDF
import pikepdf

from tqdm import tqdm

def redact_pdf(src_file: str, dest_file: str, needle: str, replacement: str):
    # Open the PDF
    doc = fitz.open(src_file)
    total_pages = len(doc)  # Get the total number of pages in the PDF


    # Iterate through pages and search for the text
    for page_num, page in tqdm(enumerate(doc), total=total_pages, desc="Redacting", unit="page"):
        text_instances = page.search_for(needle)
        for inst in text_instances:
            # Apply redaction over the found text
            page.add_redact_annot(inst, replacement, fill=(1, 1, 1))  # fill=(0, 0, 0) for black

        # Apply the redactions
        page.apply_redactions()

    # Save the modified PDF to a temporary file
    temp_file = f"{dest_file}_temp.pdf"
    doc.save(temp_file)
    print(f"PDF Redaction Completed.")

    # Open the temporary file with PikePDF and compress it
    with pikepdf.open(temp_file) as pdf:
        pdf.save(dest_file, compress_streams=True)
        print(f"PDF compression complete. Final file saved as '{dest_file}'.")

    # Remove the temporary file
    os.remove(temp_file)
    # print(f"Temporary file '{temp_file}' has been removed.")

if __name__ == "__main__" :
    if len(sys.argv) < 5:
        print(f"Missing Arguments: \nUsage: {sys.argv[0]} src_file dest_file needle replacement")
        exit(-1)
    redact_pdf(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])