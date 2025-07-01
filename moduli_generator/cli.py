#!/usr/bin/env python
import argparse
from datetime import UTC, datetime
from sys import exit

# Import the default configuration
from config import (default_config)
from moduli_generator import ModuliGenerator
from db.moduli_db_utilities import MariaDBConnector


def parse_args():
    """Parse command line arguments for moduli_generator."""
    parser = argparse.ArgumentParser(
        description="Moduli Generator - Generate and manage secure moduli for cryptographic operations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--key-lengths",
        type=int,
        nargs="+",
        default=default_config.key_lengths,
        help="Space-separated list of key lengths to generate moduli for"
    )
    parser.add_argument(
        "--moduli-home",
        type=str,
        default=str(default_config.base_dir),
        help="Base directory for moduli generation and storage"
    )
    parser.add_argument(
        "--candidates-dir",
        type=str,
        default=str(default_config.candidates_dir.relative_to(default_config.base_dir)),
        help="Directory to store candidate moduli (relative to moduli-home)"
    )
    parser.add_argument(
        "--moduli-dir",
        type=str,
        default=str(default_config.moduli_dir.relative_to(default_config.base_dir)),
        help="Directory to store generated moduli (relative to moduli-home)"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default=str(default_config.log_dir.relative_to(default_config.base_dir)),
        help="Directory to store log files (relative to moduli-home)"
    )
    parser.add_argument(
        "--mariadb-cnf",
        type=str,
        default=str(default_config.moduli_generator_config.relative_to(default_config.base_dir)),
        help="Path to MariaDB configuration file (relative to moduli-home)"
    )
    # Add a nice_value argument that might be missing
    parser.add_argument(
        "--nice-value",
        type=int,
        default=default_config.nice_value,
        help="Process nice value for CPU intensive operations"
    )

    return parser.parse_args()


def main():
    """Main function for the moduli_generator package"""
    args = parse_args()

    # Create a custom configuration based on the command line arguments
    config = default_config.with_base_dir(args.moduli_home)

    # Override with command line options if provided
    config.candidates_dir = config.base_dir / args.candidates_dir
    config.moduli_dir = config.base_dir / args.moduli_dir
    config.log_dir = config.base_dir / args.log_dir
    config.moduli_generator_config = config.base_dir / args.mariadb_cnf

    logger = config.get_logger()
    logger.name = __name__

    logger.debug(f'Using default config: {config}')
    logger.debug(f'Overriding config with command line args: {args}')

    # Ensure all directories exist
    config.ensure_directories()
    logger.debug(f'Directories created or validated: {config.base_dir}')

    # Set variables from args
    config.key_lengths = tuple(args.key_lengths)
    logger.debug(f'Key Lengths: {config.key_lengths}')

    config.nice_value = args.nice_value
    logger.debug(f'Nice Value: {config.nice_value}')

    # Generate moduli
    start_time = datetime.now(UTC).replace(tzinfo=None)
    logger.info(f'Starting Moduli Generation at {start_time}')
    generator = ModuliGenerator(config)
    generated_files = generator.generate_moduli()
    logger.debug(f'Generated Moduli: {generated_files}')

    # Save screened moduli as JSON dict
    generator.save_moduli()  # to
    logger.debug(f'Moduli saved to {config.moduli_dir}')

    # Store Screened Moduli in MariaDB
    generator.store_moduli(MariaDBConnector(config))  # To DB
    logger.info(f'Moduli stored in DB')

    # Stats and Cleanup
    duration = (datetime.now(UTC).replace(tzinfo=None) - start_time).seconds
    logger.info(f'Moduli Generation Complete. Time taken: {duration} seconds')
    print(f'Moduli Generation Complete. Time taken: {duration} seconds')

    return 0


if __name__ == "__main__":
    exit(main())
