import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

@dataclass
class RedactionConfig:
    """Configuration structure for PDF redaction."""
    searches: List[str]
    predefined_patterns: Optional[List[str]] = None
    replacement: str = "***REDACTED***"
    ignore_case: bool = False
    verbose: bool = False
    overwrite: bool = False
    validate_patterns: bool = True
    print_stats: bool = True
    dry_run: bool = False

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'RedactionConfig':
        """Create config from dictionary."""
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__annotations__})

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)


class ConfigLoader:
    """Load and validate configuration files."""

    @staticmethod
    def load_config(config_path: str) -> RedactionConfig:
        """Load configuration from file."""
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        try:
            with open(path, 'r') as f:
                if path.suffix.lower() in ['.yml', '.yaml']:
                    config_data = yaml.safe_load(f)
                elif path.suffix.lower() == '.json':
                    config_data = json.load(f)
                else:
                    raise ValueError(
                        f"Unsupported config format: {path.suffix}")

            return RedactionConfig.from_dict(config_data)

        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid config file format: {e}")

    @staticmethod
    def __save_redaction_config(
        config: RedactionConfig,
        config_path: str
    ) -> None:
        """Save configuration to file."""
        path = Path(config_path)

        with open(path, 'w') as f:
            if path.suffix.lower() in ['.yml', '.yaml']:
                yaml.dump(config.to_dict(), f, default_flow_style=False)
            elif path.suffix.lower() == '.json':
                json.dump(config.to_dict(), f, indent=2)

    @staticmethod
    def __save_dict_config(
        config_to_save: Dict[str, Any],
        save_path: str
    ) -> None:
        """  
        Save configuration after successful processing.  

        Args:  
            final_config: The merged configuration used for processing  
            save_path: Path to save the configuration  
        """
        # logger = logging.getLogger(__name__)

        # Convert final_config back to RedactionConfig format
        final_config = RedactionConfig.from_dict(config_to_save)

        try:
            ConfigLoader.save_config(final_config, save_path)
        except Exception as e:
            raise e

    @staticmethod
    def save_config(
            config_to_save: Union[Dict[str, Any], RedactionConfig],
            save_path: str) -> None:
        if isinstance(config_to_save, RedactionConfig):
            ConfigLoader.__save_redaction_config(config_to_save, save_path)
        elif isinstance(config_to_save, dict):
            ConfigLoader.__save_dict_config(config_to_save, save_path)
        else:
            raise TypeError("Unsupported config type")

    @staticmethod
    def generate_sample_config(config_path: str) -> None:
        """Generate a sample configuration file."""
        sample_config = RedactionConfig(
            searches=["email@example.com", r"\b\d{3}-\d{2}-\d{4}\b"],
            predefined_patterns=["email", "phone"],
            replacement="[REDACTED]",
            ignore_case=True,
            verbose=False,
            overwrite=False,
            validate_patterns=True,
            print_stats=False,
            dry_run=True
        )

        return ConfigLoader.save_config(
            config_to_save=sample_config.to_dict(),
            save_path=config_path
        )
    
    
