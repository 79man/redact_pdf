import sys

import fitz  # PyMuPDF
import pikepdf

def redact_pdf(src_file: str, dest_file: str, needle:str, replacement: str):
    # Open the PDF
    doc = fitz.open(src_file)

    # Iterate through pages and search for the text
    for page_num, page in enumerate(doc):
        text_instances = page.search_for(needle)
        for inst in text_instances:
            # Apply redaction over the found text
            page.add_redact_annot(inst, replacement, fill=(1, 1, 1))  # fill=(0, 0, 0) for black

        # Apply the redactions
        page.apply_redactions()

    # Save the modified PDF
    doc.save(dest_file)
    print(f"Redaction complete. Saved as '{dest_file}'.")

    with pikepdf.open(dest_file) as pdf:
        pdf.save(f"{dest_file}_compressed.pdf", compress_streams=True)
        print(f"PDF compression complete. Saved as '{dest_file}_compressed.pdf'.")

if __name__ == "__main__" :
    if len(sys.argv) < 5:
        print(f"Missing Arguments: \nUsage: {sys.argv[0]} src_file dest_file needle replacement")
        exit(-1)
    redact_pdf(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])