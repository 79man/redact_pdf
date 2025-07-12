import pytest
import sys
from unittest.mock import patch, MagicMock
from pdf_redacter.cli import PdfRedacterCLI
from pdf_redacter.core import PDFRedactor


class TestCLI:

    @patch('pdf_redacter.cli.PDFRedactor')
    def test_main_basic_args(self, mock_redactor, sample_pdf, temp_dir):
        """Test CLI with basic arguments."""
        output_path = temp_dir / "output.pdf"

        test_args = [
            'pdf_redacter',
            '-i', str(sample_pdf),
            '-o', str(output_path),
            '-s', 'test@example.com'
        ]

        with patch.object(sys, 'argv', test_args):
            PdfRedacterCLI.main()

        # Verify PDFRedactor was called correctly
        mock_redactor.assert_called_once()
        mock_instance = mock_redactor.return_value
        mock_instance.redact_pdf.assert_called_once()

    @patch('pdf_redacter.cli.PDFRedactor')
    def test_main_with_flags(self, mock_redactor, sample_pdf, temp_dir):
        """Test CLI with optional flags."""
        output_path = temp_dir / "output.pdf"

        test_args = [
            'pdf_redacter',
            '-i', str(sample_pdf),
            '-o', str(output_path),
            '-s', 'confidential',
            '-c',  # ignore-case
            '-v',  # verbose
            '-f',  # overwrite
            '-r', '[CLASSIFIED]'  # replacement
        ]

        with patch.object(sys, 'argv', test_args):
            PdfRedacterCLI.main()

        mock_instance = mock_redactor.return_value
        call_args = mock_instance.redact_pdf.call_args

        assert call_args[1]['ignore_case'] is True
        assert call_args[1]['replacement'] == '[CLASSIFIED]'

    def test_main_missing_required_args(self):
        """Test CLI with missing required arguments."""
        test_args = ['pdf_redacter', '-i', 'input.pdf']  # Missing -o and -s

        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                PdfRedacterCLI.main()
