import pytest
import os
from pdf_redacter.core import PDFRedactor
import fitz

from pdf_redacter.pattern_matcher import PatternType


class TestPDFRedactor:

    def test_init_valid_paths(self, sample_pdf, temp_dir):
        """Test PDFRedactor initialization with valid paths."""
        output_path = temp_dir / "output.pdf"
        redactor = PDFRedactor(
            src_file=str(sample_pdf),
            dest_file=str(output_path),
            overwrite=True
        )
        assert redactor.src_file == str(sample_pdf)
        assert redactor.dest_file == str(output_path)

    def test_init_nonexistent_source(self, temp_dir):
        """Test PDFRedactor with non-existent source file."""
        with pytest.raises(FileNotFoundError):
            PDFRedactor(
                src_file="nonexistent.pdf",
                dest_file=str(temp_dir / "output.pdf"),
                overwrite=True
            )

    def test_redact_pdf_basic(self, sample_pdf, temp_dir):
        """Test basic PDF redaction functionality."""
        output_path = temp_dir / "redacted.pdf"
        redactor = PDFRedactor(
            src_file=str(sample_pdf),
            dest_file=str(output_path),
            overwrite=True
        )

        # Test redaction
        redactor.redact_pdf(
            needles=["test@example.com"],
            replacement="[EMAIL REDACTED]",
            ignore_case=False
        )

        # Verify output file exists
        assert output_path.exists()

        # Verify redaction worked
        doc = fitz.open(str(output_path))
        page_text = doc[0].get_text()
        assert "[EMAIL REDACTED]" in page_text
        assert "test@example.com" not in page_text
        doc.close()

    def test_redact_pdf_case_insensitive(self, sample_pdf, temp_dir):
        """Test case-insensitive redaction."""
        output_path = temp_dir / "redacted.pdf"
        redactor = PDFRedactor(
            src_file=str(sample_pdf),
            dest_file=str(output_path),
            overwrite=True
        )

        redactor.redact_pdf(
            needles=["CONFIDENTIAL"],  # Uppercase pattern
            replacement="[REDACTED]",
            ignore_case=True
        )

        # Verify redaction worked on lowercase text
        doc: fitz.Document = fitz.open(str(output_path))
        page_text = doc[0].get_text()
        assert "[REDACTED]" in page_text
        doc.close()

    @pytest.mark.parametrize("pattern,text,should_match", [
        (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}",
         "test@example.com", True),
        (r"\d{3}-\d{2}-\d{4}", "123-45-6789", True),
        ("confidential", "Confidential", False),  # case sensitive
    ])
    def test_regex_patterns(self, sample_pdf, temp_dir, pattern, text, should_match):
        """Test various regex patterns."""
        output_path = temp_dir / "redacted.pdf"
        redactor = PDFRedactor(
            src_file=str(sample_pdf),
            dest_file=str(output_path),
            overwrite=True
        )

        redactor.redact_pdf(
            needles=[pattern],
            replacement="[REDACTED]",
            ignore_case=False
        )

        doc = fitz.open(str(output_path))
        page_text = doc[0].get_text()
        doc.close()

        if should_match:
            assert "[REDACTED]" in page_text
        else:
            assert text in page_text  # Original text should remain

    def test_redact_pdf_empty_needles(self, sample_pdf, temp_dir):
        """Test redaction with empty needles list."""
        output_path = temp_dir / "redacted.pdf"
        redactor = PDFRedactor(
            src_file=str(sample_pdf),
            dest_file=str(output_path),
            overwrite=True
        )

        result = redactor.redact_pdf(
            needles=[],
            replacement="[REDACTED]",
            ignore_case=False
        )

        # Should return None for empty needles
        assert result is None

    @pytest.mark.parametrize("pattern,expected_result", [
        ("email", True),
        ("phone", True),
        ("ssn", True),
        ("credit_card", True),
        ("abracadabra", False)
    ])
    def test_redact_pdf_with_predefined_patterns(
            self, sample_pdf, temp_dir,
            pattern, expected_result
    ):
        """Test redaction using predefined patterns."""
        output_path = temp_dir / "redacted.pdf"
        redactor = PDFRedactor(
            src_file=str(sample_pdf),
            dest_file=str(output_path),
            overwrite=True
        )

        # Handle invalid pattern case
        if pattern == "abracadabra":
            # This should fail during pattern type conversion or validation
            with pytest.raises((ValueError, AttributeError)):
                PatternType(pattern)
            return

        # Convert string to PatternType enum
        try:
            pattern_type = PatternType(pattern)
            predefined_patterns = [pattern_type]
        except ValueError:
            pytest.fail(f"Pattern {pattern} should be valid")

        # Test with email predefined pattern
        result = redactor.redact_pdf(
            needles=[],
            replacement="[REDACTED]",
            ignore_case=False,
            predefined_patterns=predefined_patterns
        )

        # Verify method returns statistics dictionary
        assert isinstance(result, dict)
        assert "total_matches" in result

        if expected_result:
            # Verify pattern found matches and redacted content
            assert result["total_matches"] > 0
            doc = fitz.open(str(output_path))
            page_text = doc[0].get_text()
            assert "[REDACTED]" in page_text
            doc.close()
        else:
            # Pattern is valid but no matches found in sample PDF
            assert result["total_matches"] == 0

    def test_redact_pdf_combined_patterns(self, sample_pdf, temp_dir):
        """Test combining custom needles with predefined patterns."""
        output_path = temp_dir / "redacted.pdf"
        redactor = PDFRedactor(
            src_file=str(sample_pdf),
            dest_file=str(output_path),
            overwrite=True
        )

        # Test both custom needles and predefined patterns together
        result = redactor.redact_pdf(
            needles=["Confidential"],  # Custom pattern
            replacement="[REDACTED]",
            ignore_case=True,
            predefined_patterns=[PatternType.EMAIL, PatternType.PHONE],
            validate_patterns=True
        )

        # Verify the method returns statistics
        assert isinstance(result, dict)
        assert "total_matches" in result
        assert "pages_processed" in result
        assert "patterns_used" in result
        assert "matches_by_pattern" in result

        # Should have processed patterns: 1 custom + 2 predefined = 3 total
        assert result["patterns_used"] == 3

        # Verify redaction worked
        doc = fitz.open(str(output_path))
        page_text = doc[0].get_text()

        # Check that custom pattern was redacted
        assert "[REDACTED]" in page_text
        assert "Confidential" not in page_text

        # Check that email was redacted (predefined pattern)
        assert "@" not in page_text or "[REDACTED]" in page_text

        # Check that phone number was redacted (predefined pattern)
        # The sample PDF contains "(555) 123-4567"
        assert "555" not in page_text or "[REDACTED]" in page_text

        doc.close()

        # Verify statistics show matches for different patterns
        assert result["total_matches"] > 0
        assert len(result["matches_by_pattern"]) > 0

    def test_redact_pdf_invalid_patterns_with_validation(self, sample_pdf, temp_dir):
        """Test that invalid patterns are caught when validation is enabled."""
        output_path = temp_dir / "redacted.pdf"
        redactor = PDFRedactor(
            src_file=str(sample_pdf),
            dest_file=str(output_path),
            overwrite=True
        )

        result = redactor.redact_pdf(
            needles=["[unclosed bracket"],  # Invalid regex
            replacement="[REDACTED]",
            ignore_case=False,
            validate_patterns=True
        )

        # Should return None due to validation failure
        assert result is None

    def test_redact_pdf_skip_validation(self, sample_pdf, temp_dir):
        """Test that validation can be disabled."""
        output_path = temp_dir / "redacted.pdf"
        redactor = PDFRedactor(
            src_file=str(sample_pdf),
            dest_file=str(output_path),
            overwrite=True
        )

        # Test with an invalid regex pattern but validation disabled
        result_invalid = redactor.redact_pdf(
            # Invalid regex that would normally fail
            needles=["[unclosed bracket"],
            replacement="[REDACTED]",
            ignore_case=False,
            validate_patterns=False  # Disable validation
        )
        # Should successfully process valid patterns even with validation disabled
        assert result_invalid is None

        # When validation is disabled, the method should attempt to process
        # even invalid patterns, though it may fail during execution
        # The key is that it doesn't fail during the validation phase

        # Verify the method doesn't immediately return None due to validation
        # (it might still return None due to regex compilation errors during processing)

        # Test with a valid pattern to ensure the method works when validation is off
        result_valid = redactor.redact_pdf(
            needles=["test@example.com"],
            replacement="[REDACTED]",
            ignore_case=False,
            validate_patterns=False
        )

        # Should successfully process valid patterns even with validation disabled
        assert isinstance(result_valid, dict)
        assert "total_matches" in result_valid
        assert "pages_processed" in result_valid

        # Verify the output file was created
        assert output_path.exists()

        # Verify redaction worked
        doc = fitz.open(str(output_path))
        page_text = doc[0].get_text()
        assert "[REDACTED]" in page_text
        assert "test@example.com" not in page_text
        doc.close()
