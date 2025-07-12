import pytest
import tempfile
import os
from pathlib import Path
from pdf_redacter.core import PDFRedactor
import fitz  # pyumpdf


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_pdf(temp_dir):
    """Create a sample PDF with test content."""
    pdf_path = temp_dir / "sample.pdf"
    doc: fitz.Document = fitz.open()
    page = doc.new_page()

    # Add test content
    text_content = """  
    This is a test document.  
    Contact us at test@example.com or support@company.org  
    Phone: (555) 123-4567  
    Phone: +91-9856788765 
    SSN: 123-45-6789  
    Credit Card: 9987-6654-0098-3345
    Confidential information here.  
    """

    page.insert_text((50, 50), text_content)
    doc.save(str(pdf_path))
    doc.close()

    return pdf_path
