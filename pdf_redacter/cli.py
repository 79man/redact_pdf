import logging
import sys
import argparse
from typing import Final, Optional, Dict, Any
from pdf_redacter.core import PDFRedactor
from pdf_redacter.pattern_matcher import PatternType
from pdf_redacter.config import ConfigLoader
from pdf_redacter.args_processor import ArgsProcessor


class PdfRedacterCLI:

    @staticmethod
    def main():
        """
        Entry point for the PDF Redacter CLI.
        """

        parser = ArgsProcessor.generate_argument_parser()
        # Parse arguments
        args: argparse.Namespace = parser.parse_args()

        if args.verbose:
            print("Setting log levels to DEBUG")
            # Increase log levels
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(levelname)s - %(asctime)s : %(message)s"
            )

        final_config = ArgsProcessor.load_configuration(args)

        if not args.verbose and final_config.get('verbose', False):
            print("Setting log levels to DEBUG")
            # Increase log levels
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(levelname)s - %(asctime)s : %(message)s"
            )
        else:
            # print("Setting log levels to INFO")
            logging.basicConfig(
                level=logging.INFO,  # Set logging level to INFO
                format="%(levelname)s - %(asctime)s : %(message)s"
            )

        # Create a logger
        logger = logging.getLogger(__name__)
        # logger.debug(args)

        logger.info(f"final_config in cli: {final_config}")

        if final_config:
            # Handle config generation            
            if final_config.get('generate_sample_config'):                
                ConfigLoader.generate_sample_config(
                    str(final_config.get('generate_sample_config'))
                )
                logger.info(f"Saved config to {final_config.get('generate_sample_config')}")
                sys.exit(0)

            # Run redaction with merged config
            if not final_config.get('dry_run', False):
                # Perfomr redaction if not dry_run mode
                PdfRedacterCLI.run_redaction(final_config)
            else:
                logger.info("Dry Run successful")
                logger.debug(final_config)

            # Save configuration to specified file
            if final_config.get('save_config', None):
                ConfigLoader.save_config(
                    final_config,
                    str(final_config.get('save_config'))
                )
        else:
            logger.error("Invalid configuartion. Exiting...")

    @staticmethod
    def run_redaction(
        final_config: Dict[str, Any]
    ) -> None:
        """  
        Execute PDF redaction using the merged configuration.  

        Args:  
            final_config: Dictionary containing all configuration parameters  
        """
        logger = logging.getLogger(__name__)

        try:
            # Create PDFRedactor instance
            pdf_redactor_engine = PDFRedactor(
                src_file=str(final_config.get('src_file', None)),
                dest_file=str(final_config.get('output_file', None)),
                overwrite=final_config.get('overwrite', False)
            )

            # Prepare arguments for redact_pdf method
            redaction_args = {
                'needles': final_config.get('searches', None),
                'replacement': final_config.get('replacement', '***REDACTED***'),
                'ignore_case': final_config.get('ignore_case', False)
            }

            # Add enhanced pattern matching arguments if available
            if 'predefined_patterns' in final_config \
                    and final_config['predefined_patterns']:
                # Convert string patterns to PatternType enum values
                predefined_types = [PatternType(
                    pattern_name) for pattern_name in final_config['predefined_patterns']]
                redaction_args['predefined_patterns'] = predefined_types

            # Execute redaction
            result = pdf_redactor_engine.redact_pdf(**redaction_args)

            if not result:
                logger.error(f"Redaction Failed")
                sys.exit(1)

            # Handle result based on enhanced vs original implementation
            if final_config.get('print_stats', False) and isinstance(result, dict):
                # Enhanced implementation returns statistics
                logger.info(f"Redaction completed successfully:")
                logger.info(f"  - Total matches: {result['total_matches']}")
                logger.info(
                    f"  - Pages processed: {result['pages_processed']}")
                logger.info(f"  - Pages modified: {result['pages_modified']}")
                logger.info(f"  - Patterns used: {result['patterns_used']}")

                if result['matches_by_pattern']:
                    logger.info("  - Matches by pattern:")
                    for pattern, count in result['matches_by_pattern'].items():
                        logger.info(f"    * {pattern}: {count} matches")
            else:
                # Original implementation returns None on success
                logger.info("PDF redaction completed successfully")

        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            sys.exit(1)
        except FileExistsError as e:
            logger.error(f"File already exists: {e}")
            sys.exit(1)
        except ValueError as e:
            logger.error(f"Invalid configuration: {e}")
            sys.exit(1)
        except Exception as e:
            logger.exception(f"An error occurred during redaction: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    PdfRedacterCLI.main()
