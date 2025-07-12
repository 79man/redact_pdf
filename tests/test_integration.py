import pytest
import subprocess
import sys
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import patch
from pdf_redacter.core import PDFRedactor
from pdf_redacter.cli import PdfRedacterCLI
from pdf_redacter.config import RedactionConfig, ConfigLoader
import fitz


class TestIntegration:
    """Integration tests for end-to-end PDF redaction workflows."""

    def test_full_workflow_cli_basic(self, sample_pdf, temp_dir):
        """Test complete workflow via CLI with basic arguments."""
        output_path = temp_dir / "integrated_output.pdf"

        cmd = [
            sys.executable, "-m", "pdf_redacter.cli",
            "-i", str(sample_pdf),
            "-o", str(output_path),
            "-s", "test@example.com",
            "-r", "[EMAIL_REDACTED]",
            "-v"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        assert result.returncode == 0
        assert output_path.exists()

        # Verify redaction worked
        doc = fitz.open(str(output_path))
        page_text = doc[0].get_text()
        assert "[EMAIL_REDACTED]" in page_text
        assert "test@example.com" not in page_text
        doc.close()

    def test_full_workflow_with_predefined_patterns(self, sample_pdf, temp_dir):
        """Test workflow using predefined patterns."""
        output_path = temp_dir / "predefined_output.pdf"

        cmd = [
            sys.executable, "-m", "pdf_redacter.cli",
            "-i", str(sample_pdf),
            "-o", str(output_path),
            "-s", "Confidential",
            "--predefined-patterns", "email", "phone",
            "-r", "[REDACTED]",
            "-v", "-f"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        assert result.returncode == 0
        assert output_path.exists()

        # Verify multiple pattern types were redacted
        doc = fitz.open(str(output_path))
        page_text = doc[0].get_text()
        assert "[REDACTED]" in page_text  # Default replacement
        # Email should be redacted
        assert "@" not in page_text or "[REDACTED]" in page_text
        doc.close()

    def test_config_file_workflow_yaml(self, sample_pdf, temp_dir):
        """Test complete workflow using YAML configuration file."""
        config_path = temp_dir / "test_config.yml"
        output_path = temp_dir / "config_output.pdf"

        # Create test configuration
        config_data = {
            'searches': ['Confidential', 'test@example.com'],
            'predefined_patterns': ['phone', 'ssn'],
            'replacement': '[CLASSIFIED]',
            'ignore_case': True,
            'verbose': True,
            'overwrite': True
        }

        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)

        cmd = [
            sys.executable, "-m", "pdf_redacter.cli",
            "--config", str(config_path),
            "-i", str(sample_pdf),
            "-o", str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        assert result.returncode == 0
        assert output_path.exists()

        # Verify redaction with config settings
        doc = fitz.open(str(output_path))
        page_text = doc[0].get_text()
        assert "[CLASSIFIED]" in page_text  # Custom replacement
        doc.close()

    def test_config_file_workflow_json(self, sample_pdf, temp_dir):
        """Test complete workflow using JSON configuration file."""
        config_path = temp_dir / "test_config.json"
        output_path = temp_dir / "json_config_output.pdf"

        # Create test configuration
        config_data = {
            "searches": ["confidential"],
            "predefined_patterns": ["email"],
            "replacement": "[REDACTED_JSON]",
            "ignore_case": True,
            "verbose": False,
            "overwrite": True
        }

        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)

        cmd = [
            sys.executable, "-m", "pdf_redacter.cli",
            "--config", str(config_path),
            "-i", str(sample_pdf),
            "-o", str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        assert result.returncode == 0
        assert output_path.exists()

        # Verify JSON config was applied
        doc = fitz.open(str(output_path))
        page_text = doc[0].get_text()
        assert "[REDACTED_JSON]" in page_text
        doc.close()

    def test_config_generation_and_usage(self, temp_dir):
        """Test generating config file and then using it."""
        config_path = temp_dir / "generated_config.yml"

        # Generate sample config
        cmd_generate = [
            sys.executable, "-m", "pdf_redacter.cli",
            "--generate-sample-config", str(config_path)
        ]

        result = subprocess.run(cmd_generate, capture_output=True, text=True)
        assert result.returncode == 0
        assert config_path.exists()

        # Verify generated config is valid
        config = ConfigLoader.load_config(str(config_path))
        assert isinstance(config, RedactionConfig)
        assert len(config.searches) > 0

    def test_save_config_workflow(self, sample_pdf, temp_dir):
        """Test saving current arguments to config file."""
        output_path = temp_dir / "save_test_output.pdf"
        config_path = temp_dir / "saved_config.yml"

        cmd = [
            sys.executable, "-m", "pdf_redacter.cli",
            "-i", str(sample_pdf),
            "-o", str(output_path),
            "-s", "test_pattern",
            "-r", "[SAVED_CONFIG]",
            "--save-config", str(config_path),
            "-v"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        assert result.returncode == 0
        assert output_path.exists()
        assert config_path.exists()

        # Verify saved config contains correct values
        saved_config = ConfigLoader.load_config(str(config_path))
        assert "test_pattern" in saved_config.searches
        assert saved_config.replacement == "[SAVED_CONFIG]"
        assert saved_config.verbose is True

    def test_cli_override_config_values(self, sample_pdf, temp_dir):
        """Test that CLI arguments override config file values."""
        config_path = temp_dir / "override_config.yml"
        output_path = temp_dir / "override_output.pdf"

        # Create config with specific values
        config_data = {
            'searches': ['config_pattern'],
            'replacement': '[CONFIG_REPLACEMENT]',
            'ignore_case': False,
            'verbose': False
        }

        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)

        # Use CLI args that should override config
        cmd = [
            sys.executable, "-m", "pdf_redacter.cli",
            "--config", str(config_path),
            "-i", str(sample_pdf),
            "-o", str(output_path),
            "-s", "Confidential",  # Override searches
            "-r", "[CLI_REPLACEMENT]",  # Override replacement
            "-v"  # Override verbose
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        assert result.returncode == 0
        assert output_path.exists()

        # Verify CLI overrides were applied
        doc = fitz.open(str(output_path))
        page_text = doc[0].get_text()
        assert "[CLI_REPLACEMENT]" in page_text  # CLI replacement, not config
        doc.close()

    def test_pattern_validation_integration(self, sample_pdf, temp_dir):
        """Test pattern validation in full workflow."""
        output_path = temp_dir / "validation_output.pdf"

        # Test with invalid regex pattern
        cmd_invalid = [
            sys.executable, "-m", "pdf_redacter.cli",
            "-i", str(sample_pdf),
            "-o", str(output_path),
            "-s", "[unclosed bracket",  # Invalid regex
            "--validate-patterns"
        ]

        result = subprocess.run(cmd_invalid, capture_output=True, text=True)

        # Should fail due to validation
        assert result.returncode != 0
        assert "Invalid pattern" in result.stderr or "validation" in result.stderr.lower()

    def test_error_handling_missing_files(self, temp_dir):
        """Test error handling for missing input files."""
        nonexistent_file = temp_dir / "nonexistent.pdf"
        output_path = temp_dir / "output.pdf"

        cmd = [
            sys.executable, "-m", "pdf_redacter.cli",
            "-i", str(nonexistent_file),
            "-o", str(output_path),
            "-s", "test"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()

    def test_statistics_output_integration(self, sample_pdf, temp_dir):
        """Test that statistics are properly output in verbose mode."""
        output_path = temp_dir / "stats_output.pdf"

        cmd = [
            sys.executable, "-m", "pdf_redacter.cli",
            "-i", str(sample_pdf),
            "-o", str(output_path),
            "-s", "test@example.com", "Confidential",
            "-v"  # Verbose mode should show statistics
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        assert result.returncode == 0
        assert output_path.exists()

        # Check for statistics in output
        output_text = result.stdout + result.stderr
        assert "matches" in output_text.lower() or "redaction" in output_text.lower()

    def test_multiple_file_formats_config(self, sample_pdf, temp_dir):
        """Test that both YAML and JSON configs work interchangeably."""
        yaml_config = temp_dir / "test.yml"
        json_config = temp_dir / "test.json"

        config_data = {
            'searches': ['test_pattern'],
            'replacement': '[TEST]',
            'ignore_case': True
        }

        # Save as both YAML and JSON
        with open(yaml_config, 'w') as f:
            yaml.dump(config_data, f)

        with open(json_config, 'w') as f:
            json.dump(config_data, f)

        # Test both formats produce same results
        for config_file in [yaml_config, json_config]:
            output_path = temp_dir / f"output_{config_file.suffix}.pdf"

            cmd = [
                sys.executable, "-m", "pdf_redacter.cli",
                "--config", str(config_file),
                "-i", str(sample_pdf),
                "-o", str(output_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0
            assert output_path.exists()

    @patch('pdf_redacter.cli.PDFRedactor')
    def test_cli_argument_passing_integration(self, mock_redactor, sample_pdf, temp_dir):
        """Test that CLI arguments are properly passed to PDFRedactor."""
        output_path = temp_dir / "mock_output.pdf"

        # Mock the PDFRedactor to verify argument passing
        mock_instance = mock_redactor.return_value
        mock_instance.redact_pdf.return_value = {
            'total_matches': 5,
            'pages_processed': 1,
            'patterns_used': 2,
            'matches_by_pattern': {}
        }

        # Only include the actual CLI arguments, not the module execution part
        test_args = [
            "pdf_redacter",  # Script name
            "-i", str(sample_pdf),
            "-o", str(output_path),
            "-s", "pattern1", "pattern2",
            "-r", "[CUSTOM]",
            "-c",  # ignore-case
            "-v",  # verbose
            "-f"   # overwrite
        ]

        with patch.object(sys, 'argv', test_args):
            PdfRedacterCLI.main()

        # Verify PDFRedactor was called with correct arguments
        mock_redactor.assert_called_once_with(
            src_file=str(sample_pdf),
            dest_file=str(output_path),
            overwrite=True
        )

        # Verify redact_pdf was called with correct parameters
        call_args = mock_instance.redact_pdf.call_args
        assert call_args[1]['needles'] == ['pattern1', 'pattern2']
        assert call_args[1]['replacement'] == '[CUSTOM]'
        assert call_args[1]['ignore_case'] is True
