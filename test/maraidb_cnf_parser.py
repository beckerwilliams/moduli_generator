import configparser
from pathlib import Path
from typing import Any, Union


def get_mysql_config_value(config, section: str, key: str, default: Any = None) -> Any:
    """Get a configuration value with proper type validation."""
    # Type validation - this MUST raise TypeError for invalid types INCLUDING None
    if config is None:
        raise TypeError("config cannot be None")

    if not isinstance(
        config, (configparser.ConfigParser, configparser.RawConfigParser, dict)
    ):
        raise TypeError(
            f"config must be ConfigParser, RawConfigParser, or dict, got {type(config).__name__}"
        )

    if not isinstance(section, str):
        raise TypeError(f"section must be string, got {type(section).__name__}")

    if not isinstance(key, str):
        raise TypeError(f"key must be string, got {type(key).__name__}")

    try:
        # Handle both ConfigParser objects and dicts
        if hasattr(config, "sections"):
            # It's a ConfigParser object
            if section in config and key in config[section]:
                value = config[section][key]
                return value
        else:
            # It's a dictionary
            if section in config and key in config[section]:
                value = config[section][key]
                return value
        return default
    except Exception:
        return default


def parse_mysql_config(config_path: Union[str, Path]) -> configparser.ConfigParser:
    """Parse MySQL/MariaDB configuration file with proper error handling."""

    # Handle file-like objects
    if hasattr(config_path, "read"):
        try:
            # Read the content and process inline comments manually
            content = config_path.read()
            if hasattr(config_path, "seek"):
                config_path.seek(0)  # Reset file pointer

            # Process inline comments manually - this is the key fix
            processed_lines = []
            for line in content.split("\n"):
                # Handle inline comments properly
                if "#" in line and not line.strip().startswith("#"):
                    # Find the position of # that's not at the start of the line
                    comment_pos = line.find("#")
                    # Only strip if there's actual content before the #
                    if comment_pos > 0 and line[:comment_pos].strip():
                        line = line[:comment_pos].rstrip()
                processed_lines.append(line)

            processed_content = "\n".join(processed_lines)

            config = configparser.ConfigParser(allow_no_value=True)
            config.read_string(processed_content)
            return config

        except Exception as e:
            raise ValueError(f"Error parsing configuration file: {e}")

    # Handle string/Path objects
    file_path = Path(config_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    # Check if the file is empty
    if file_path.stat().st_size == 0:
        return configparser.ConfigParser(allow_no_value=True)

    try:
        # Read and process the file content manually to handle inline comments
        content = file_path.read_text()

        # Process inline comments manually - this is the key fix
        processed_lines = []
        for line in content.split("\n"):
            # Handle inline comments properly
            if "#" in line and not line.strip().startswith("#"):
                # Find the position of # that's not at the start of the line
                comment_pos = line.find("#")
                # Only strip if there's actual content before the #
                if comment_pos > 0 and line[:comment_pos].strip():
                    line = line[:comment_pos].rstrip()
            processed_lines.append(line)

        processed_content = "\n".join(processed_lines)

        config = configparser.ConfigParser(allow_no_value=True)
        config.read_string(processed_content)
        return config

    except configparser.DuplicateSectionError:
        # Handle duplicate sections by creating a custom parser
        return _parse_config_with_duplicate_sections(file_path)
    except Exception as e:
        raise ValueError(f"Error parsing configuration file: {e}")


def _parse_config_with_duplicate_sections(file_path: Path) -> configparser.ConfigParser:
    """Handle configuration files with duplicate sections by merging them."""
    try:
        content = file_path.read_text()

        # Manually parse and merge duplicate sections
        sections = {}
        current_section = None

        for line_num, line in enumerate(content.split("\n"), 1):
            original_line = line
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Handle section headers
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1]
                if current_section not in sections:
                    sections[current_section] = {}
                continue

            # Handle key-value pairs
            if current_section and "=" in line:
                # Handle inline comments properly
                if "#" in line and not line.startswith("#"):
                    comment_pos = line.find("#")
                    if comment_pos > 0:
                        line = line[:comment_pos].rstrip()

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                sections[current_section][key] = value

            elif current_section and line:
                # Key without value
                sections[current_section][line] = None

        # Create a new ConfigParser with merged sections
        config = configparser.ConfigParser(allow_no_value=True)
        for section_name, section_items in sections.items():
            config.add_section(section_name)
            for key, value in section_items.items():
                config.set(section_name, key, value)

        return config

    except Exception as e:
        raise ValueError(f"Error parsing configuration file: {e}")
