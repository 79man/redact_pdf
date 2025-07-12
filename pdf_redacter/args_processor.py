import argparse
from typing import Final, Optional, Dict, Any

from pdf_redacter.config import RedactionConfig, ConfigLoader

import logging
logger = logging.getLogger(__name__)

DEFAULT_REPLACEMENT: Final = "***REDACTED***"
DEFAULT_IGN_CASE: Final = False
DEFAULT_VERBOSE: Final = False
DEFAULT_OVERWRITE: Final = False
DEFAULT_DRY_RUN: Final = False


class TrackingAction(argparse.Action):
    """Custom action that tracks which arguments were explicitly provided."""

    def __call__(self, parser, namespace, values, option_string=None):
        if not hasattr(namespace, '_explicitly_provided'):
            namespace._explicitly_provided = set()
        namespace._explicitly_provided.add(self.dest)
        setattr(namespace, self.dest, values)


class TrackingBooleanAction(argparse.BooleanOptionalAction):
    """Custom boolean action that tracks explicit provision."""

    def __call__(self, parser, namespace, values, option_string=None):
        if not hasattr(namespace, '_explicitly_provided'):
            namespace._explicitly_provided = set()
        namespace._explicitly_provided.add(self.dest)
        # setattr(namespace, self.dest, values)
        super().__call__(parser, namespace, values, option_string)


class ArgsProcessor:
    @staticmethod
    def generate_argument_parser() -> argparse.ArgumentParser:
        # Create argument parser
        parser = argparse.ArgumentParser(
            description="A tool to redact text in PDFs with support for case-insensitive and regex searches."
        )

        # Add config file argument
        parser.add_argument(
            "--config-file",
            type=str,
            help="Path to configuration file (YAML or JSON)"
        )

        # Add config generation argument
        parser.add_argument(
            "--generate-sample-config",
            type=str,
            help="Generate sample configuration file at specified path"
        )

        # Add config generation argument
        parser.add_argument(
            "--save-config",
            type=str,
            help="Save Working Configuration to file at specified path"
        )

        # Input and output file arguments
        parser.add_argument(
            "-i", "--src_file",
            # required=True,
            action=TrackingAction,
            type=str,
            help="Path to the source PDF file. (Required)"
        )

        parser.add_argument(
            "-o", "--output_file",
            # required=True,
            action=TrackingAction,
            type=str,
            help="Path to save the output PDF. (Required)"
        )

        # Text to search and replace
        parser.add_argument(
            "-s", "--searches",
            nargs="+",
            type=str,
            action=TrackingAction,
            help="Text to redact (multiple values allowed). Regex format is also allowed. (Optional)"
        )

        # Flag for case-insensitive search
        parser.add_argument(
            "-c", "--ignore-case",
            action=TrackingBooleanAction,  # Use custom action
            default=DEFAULT_IGN_CASE,
            help=f"Enable case-insensitive search for redaction, default=[{DEFAULT_IGN_CASE}]"
        )

        parser.add_argument(
            "-r", "--replacement",
            type=str,
            action=TrackingAction,  # Use custom action
            default=DEFAULT_REPLACEMENT,
            help=f"Replacement text for redacted content. default=[{DEFAULT_REPLACEMENT}]"
        )

        parser.add_argument(
            "-v", "--verbose",
            action=TrackingBooleanAction,  # Use custom action
            default=DEFAULT_VERBOSE,
            help=f"Increase output Verbosity, default=[{DEFAULT_VERBOSE}]"
        )

        parser.add_argument(
            "-f", "--overwrite",
            action=TrackingBooleanAction,  # Use custom action
            default=DEFAULT_OVERWRITE,
            help=f"Overwrite destination PDF if it alreday exists, default=[{DEFAULT_OVERWRITE}]"
        )

        # Add to argument parser in cli.py
        parser.add_argument(
            "-P", "--predefined-patterns",
            action=TrackingAction,
            nargs="*",
            choices=["email", "phone", "ssn", "credit_card"],
            help="Use predefined patterns for common redaction scenarios"
        )

        parser.add_argument(
            "--validate-patterns",
            action=TrackingBooleanAction,  # Use custom action
            default=True,
            help="Validate regex patterns before processing (default: True)"
        )

        parser.add_argument(
            "-d", "--print-stats",
            action=TrackingBooleanAction,  # Use custom action
            default=False,
            help="Show stats about matched patterns before exit"
        )

        parser.add_argument(
            "--dry-run",
            action=TrackingBooleanAction,  # Use custom action
            default=DEFAULT_DRY_RUN,
            help=f"Perform a dry run to validate settings, default=[{DEFAULT_DRY_RUN}]"
        )

        return parser

    @staticmethod
    def __merge_config_and_args(
        config: Optional[RedactionConfig],
        args: argparse.Namespace
    ) -> Dict[str, Any]:
        """Merge configuration file with CLI arguments (CLI takes precedence)."""

        final_config = {}

        # Start with config file values
        if config:
            final_config.update(config.to_dict())

        logger.debug(f'loaded from conf file: {final_config}')

        explicitly_provided = getattr(args, '_explicitly_provided', set())

        logger.debug(f'explicitly_provided in args: {explicitly_provided}')

        # Get all argument attributes from args namespace
        all_args = vars(args)
        all_args.pop('_explicitly_provided')
        
        for key, value in all_args.items():
            if (key in explicitly_provided or key not in final_config) and value is not None:
                final_config[key] = value
                logger.debug(f'Adding/overriding arg: {key} = {value}')

        logger.debug(f"final_config: {final_config}")

        return final_config

    @staticmethod
    def load_configuration(args: argparse.Namespace) -> Dict[str, Any]:
        # Load configuration
        config = None
        if args.config_file:
            try:
                config = ConfigLoader.load_config(args.config_file)
                logger.info(f"Loaded configuration from: {args.config_file}")
            except (FileNotFoundError, ValueError) as e:
                logger.error(f"Error in loading configuration file: {e}")

        # Merge CLI args with config (CLI args take precedence)
        final_config = ArgsProcessor.__merge_config_and_args(config, args)

        ArgsProcessor.__validate_configuration(final_config)

        return final_config

    @staticmethod
    def __validate_configuration(final_config: Dict[str, Any]) -> None:

        import sys
        # Validate required fields
        if not final_config.get('src_file') or not final_config.get('output_file'):
            logger.error("Source file (-i) and output file (-o) are required")
            sys.exit(1)

        if not final_config.get('searches') and not final_config.get('predefined_patterns'):
            logger.error(
                "Search patterns (-s) or Predefined patterns (-P) are required")
            sys.exit(1)
