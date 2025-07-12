import pytest
import json
import yaml
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
from pdf_redacter.config import RedactionConfig, ConfigLoader
from pdf_redacter.pattern_matcher import PatternType


class TestRedactionConfig:
    """Test the RedactionConfig Pydantic model."""

    def test_valid_config_creation(self):
        """Test creating valid RedactionConfig with all parameters."""
        config = RedactionConfig(
            searches=["test", "email@example.com"],
            predefined_patterns=["email", "phone"],
            replacement="[REDACTED]",
            ignore_case=True,
            verbose=True,
            overwrite=False
        )

        assert config.searches == ["test", "email@example.com"]
        assert config.predefined_patterns == ["email", "phone"]
        assert config.replacement == "[REDACTED]"
        assert config.ignore_case is True
        assert config.verbose is True
        assert config.overwrite is False

    def test_config_with_defaults(self):
        """Test creating config with only required fields."""
        config = RedactionConfig(searches=["test_pattern"])

        assert config.searches == ["test_pattern"]
        assert config.predefined_patterns is None
        assert config.replacement == "***REDACTED***"
        assert config.ignore_case is False
        assert config.verbose is False
        assert config.overwrite is False

    def test_config_dict_conversion(self):
        """Test converting config to dictionary."""
        config = RedactionConfig(
            searches=["test"],
            predefined_patterns=["email"],
            replacement="[TEST]",
            ignore_case=True
        )

        config_dict = config.to_dict()

        assert config_dict["searches"] == ["test"]
        assert config_dict["predefined_patterns"] == ["email"]
        assert config_dict["replacement"] == "[TEST]"
        assert config_dict["ignore_case"] is True


class TestConfigLoader:
    """Test the ConfigLoader class for file operations."""

    def test_load_yaml_config(self, temp_dir):
        """Test loading YAML configuration file."""
        config_data = {
            'searches': ['confidential', 'secret'],
            'predefined_patterns': ['email', 'phone'],
            'replacement': '[CLASSIFIED]',
            'ignore_case': True,
            'verbose': False,
            'overwrite': True
        }

        config_file = temp_dir / "config.yml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        config = ConfigLoader.load_config(str(config_file))

        assert isinstance(config, RedactionConfig)
        assert config.searches == ['confidential', 'secret']
        assert config.predefined_patterns == ['email', 'phone']
        assert config.replacement == '[CLASSIFIED]'
        assert config.ignore_case is True
        assert config.verbose is False
        assert config.overwrite is True

    def test_load_json_config(self, temp_dir):
        """Test loading JSON configuration file."""
        config_data = {
            "searches": ["email@test.com", "confidential"],
            "predefined_patterns": ["ssn", "credit_card"],
            "replacement": "[REDACTED_JSON]",
            "ignore_case": False,
            "verbose": True
        }

        config_file = temp_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)

        config = ConfigLoader.load_config(str(config_file))

        assert isinstance(config, RedactionConfig)
        assert config.searches == ["email@test.com", "confidential"]
        assert config.predefined_patterns == ["ssn", "credit_card"]
        assert config.replacement == "[REDACTED_JSON]"
        assert config.ignore_case is False
        assert config.verbose is True

    def test_load_config_file_not_found(self):
        """Test loading non-existent configuration file."""
        with pytest.raises(FileNotFoundError, match="Config file not found"):
            ConfigLoader.load_config("nonexistent_config.yml")

    def test_load_config_unsupported_format(self, temp_dir):
        """Test loading unsupported file format."""
        config_file = temp_dir / "config.txt"
        config_file.write_text("some content")

        with pytest.raises(ValueError, match="Unsupported config format"):
            ConfigLoader.load_config(str(config_file))

    def test_load_invalid_yaml(self, temp_dir):
        """Test loading invalid YAML file."""
        config_file = temp_dir / "invalid.yml"
        config_file.write_text("invalid: yaml: content: [")

        with pytest.raises(ValueError, match="Invalid config file format"):
            ConfigLoader.load_config(str(config_file))

    def test_load_invalid_json(self, temp_dir):
        """Test loading invalid JSON file."""
        config_file = temp_dir / "invalid.json"
        config_file.write_text('{"invalid": json content}')

        with pytest.raises(ValueError, match="Invalid config file format"):
            ConfigLoader.load_config(str(config_file))

    def test_load_config_validation_failure(self, temp_dir):
        """Test loading malformed config file."""
        config_file = temp_dir / "invalid_config.yml"

        # Write malformed YAML
        with open(config_file, 'w') as f:
            f.write("invalid: yaml: content: [unclosed")

        # Should fail due to YAML parsing error
        with pytest.raises(ValueError, match="Invalid config file format"):
            ConfigLoader.load_config(str(config_file))

    def test_save_yaml_config(self, temp_dir):
        """Test saving configuration to YAML file."""
        config = RedactionConfig(
            searches=['test', 'pattern'],
            predefined_patterns=['email'],
            replacement='[SAVED]',
            ignore_case=True,
            verbose=False
        )

        config_file = temp_dir / "saved_config.yml"
        ConfigLoader.save_config(config, str(config_file))

        # Verify file was created and contains correct data
        assert config_file.exists()

        # Load and verify content
        loaded_config = ConfigLoader.load_config(str(config_file))
        assert loaded_config.searches == config.searches
        assert loaded_config.predefined_patterns == config.predefined_patterns
        assert loaded_config.replacement == config.replacement
        assert loaded_config.ignore_case == config.ignore_case

    def test_save_json_config(self, temp_dir):
        """Test saving configuration to JSON file."""
        config = RedactionConfig(
            searches=['json_test'],
            replacement='[JSON_SAVED]',
            verbose=True
        )

        config_file = temp_dir / "saved_config.json"
        ConfigLoader.save_config(config, str(config_file))

        # Verify file was created and contains correct data
        assert config_file.exists()

        # Load and verify content
        loaded_config = ConfigLoader.load_config(str(config_file))
        assert loaded_config.searches == config.searches
        assert loaded_config.replacement == config.replacement
        assert loaded_config.verbose == config.verbose

    def test_roundtrip_yaml_config(self, temp_dir):
        """Test saving and loading YAML config maintains data integrity."""
        original_config = RedactionConfig(
            searches=['roundtrip', r'\d{3}-\d{2}-\d{4}'],
            predefined_patterns=['email', 'phone'],
            replacement='[ROUNDTRIP]',
            ignore_case=True,
            verbose=True,
            overwrite=False
        )

        config_file = temp_dir / "roundtrip.yml"
        ConfigLoader.save_config(original_config, str(config_file))
        loaded_config = ConfigLoader.load_config(str(config_file))

        assert loaded_config.to_dict() == original_config.to_dict()

    def test_roundtrip_json_config(self, temp_dir):
        """Test saving and loading JSON config maintains data integrity."""
        original_config = RedactionConfig(
            searches=['json_roundtrip'],
            predefined_patterns=['ssn', 'credit_card'],
            replacement='[JSON_ROUNDTRIP]',
            ignore_case=False,
            verbose=False,
            overwrite=True
        )

        config_file = temp_dir / "roundtrip.json"
        ConfigLoader.save_config(original_config, str(config_file))
        loaded_config = ConfigLoader.load_config(str(config_file))

        assert loaded_config.to_dict() == original_config.to_dict()


class TestConfigIntegration:
    """Integration tests for configuration system."""

    def test_config_with_complex_regex_patterns(self, temp_dir):
        """Test config with complex regex patterns."""
        config_data = {
            'searches': [
                r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',  # Email
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'\b(?:\d{4}[-\s]?){3}\d{4}\b'  # Credit card
            ],
            'replacement': '[COMPLEX_REDACTED]',
            'ignore_case': True
        }

        config_file = temp_dir / "complex_config.yml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        config = ConfigLoader.load_config(str(config_file))

        assert len(config.searches) == 3
        assert config.replacement == '[COMPLEX_REDACTED]'
        assert config.ignore_case is True

    def test_config_with_all_predefined_patterns(self, temp_dir):
        """Test config with all available predefined patterns."""
        config_data = {
            'searches': ['custom_pattern'],
            'predefined_patterns': ['email', 'phone', 'ssn', 'credit_card'],
            'replacement': '[ALL_PATTERNS]'
        }

        config_file = temp_dir / "all_patterns.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        config = ConfigLoader.load_config(str(config_file))

        assert config.searches == ['custom_pattern']
        assert set(config.predefined_patterns) == {
            'email', 'phone', 'ssn', 'credit_card'}
        assert config.replacement == '[ALL_PATTERNS]'

    def test_minimal_valid_config(self, temp_dir):
        """Test minimal valid configuration."""
        config_data = {'searches': ['minimal']}

        config_file = temp_dir / "minimal.yml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        config = ConfigLoader.load_config(str(config_file))

        assert config.searches == ['minimal']
        assert config.predefined_patterns is None
        assert config.replacement == "***REDACTED***"  # Default value
        assert config.ignore_case is False  # Default value

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
