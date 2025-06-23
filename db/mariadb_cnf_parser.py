import configparser
import os
from typing import Dict, Optional


def parse_mysql_config(config_path: str) -> Dict[str, Dict[str, str]]:
    """
    Parse a MySQL configuration file and return a dictionary of sections and their key-value pairs.

    Args:
        config_path (str): Path to the MySQL configuration file

    Returns:
        Dict[str, Dict[str, str]]: Dictionary with sections as keys and
                                  dictionaries of key-value pairs as values

    Raises:
        FileNotFoundError: If the configuration file doesn't exist,
        ValueError: If there's an issue parsing the file
    """
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    cnf = configparser.ConfigParser(allow_no_value=True)
    try:
        cnf.read(config_path)
        result = {local_section: dict(cnf[local_section]) for local_section in cnf.sections()}
        return result
    except configparser.Error as error:
        raise ValueError(f"Error parsing configuration file: {error}")


def get_mysql_config_value(cnf: Dict[str, Dict[str, str]],
                           local_section: str,
                           local_key: str,
                           default: Optional[str] = None) -> Optional[str]:
    """
    Get a specific value from a parsed MySQL configuration.

    Args:
        cnf (Dict[str, Dict[str, str]]): Parsed configuration dictionary
        local_section (str): Section name
        local_key (str): Key name
        default (Optional[str]): Default value if section or key doesn't exist

    Returns:
        Optional[str]: Value from the configuration or default
    """
    if local_section in cnf and local_key in cnf[local_section]:
        return cnf[local_section][local_key]
    else:
        return None
