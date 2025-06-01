from json import (dumps, loads)
from pathlib import PosixPath as Path

# _path_parameters are those properties that become `Path` objects in runtime
# NOTE: Supply ONLY the NAMES - Not the path in which they reside.
#       The Config Directory will always be placed in User's HOME
#
# You can change either _def_dirname or _def_cfgname, Or supply your own config on __init__
_def_dirname: str = '.bw_cfg'
_def_cfgname: str = '.config'

# ________________________________________ (DO NOT MODIFY BELOW) _________________________________
_default_pre_config: tuple = (('config_dir', _def_dirname), ('config_file', _def_cfgname))


def default_config() -> dict:
    """
    Generates and returns a default configuration dictionary.

    This function creates a dictionary using data from `_default_pre_config`, where
    each value is set based on the provided `name` and `value` pairs. It is used
    to establish the default settings or configuration for the application.

    Returns:
        A dictionary representing the default configuration.
    """
    return dict((name, value) for name, value in _default_pre_config)


def _path_parameters() -> list:
    """
    Generate a list of path parameter entries from the default pre-configuration.

    This function extracts the first element of each inner list contained in the
    _default_pre_config variable, and compiles these first elements into a new list
    representing the path parameters.

    Returns:
        A list containing the first elements of each list in the default
        pre-configuration.
    """
    return [entry[0] for entry in [entry for entry in _default_pre_config]]


def _enable_path_properties(config: dict, root_dir=None) -> dict:
    """
    Enables and resolves path properties in the given configuration dictionary by
    interpreting specific keys like 'config_dir' and 'config_file' relative to a
    specified root directory. If `root_dir` is not provided, the user's home
    directory will be used as the default root directory.

    Args:
        config: Configuration dictionary containing various key-value pairs.
                  Some keys, such as 'config_dir' and 'config_file', represent
                  paths that may require resolution relative to the root directory.

        root_dir: The root directory used to resolve path properties. If not
                     provided, it defaults to the user's home directory.

    Returns:
        A new configuration dictionary with the same keys as the input
        `config`, where path-related keys have been resolved to absolute
        paths based on the given `root_dir`.
    """
    if not root_dir:
        root_dir = Path.home()

    new_config = dict()
    for prop in config:
        if prop in _path_parameters():
            if prop == 'config_dir':
                new_config[prop] = root_dir / config[prop]
            elif prop == 'config_file':
                new_config[prop] = root_dir / config['config_dir'] / config[prop]
        else:
            new_config[prop] = config[prop]

    return new_config


def _disable_path_properties(config: dict) -> dict:
    """
    Disables specific path-related properties ('config_dir' and 'config_file') in
    the given configuration dictionary by replacing their values with their
    `name` attribute. If the property is not 'config_dir' or 'config_file',
    it assigns the 'name' attribute of 'config_file' to the key 'config_file'.

    Args:
        config: Configuration dictionary containing potential path
        properties such as 'config_dir' or 'config_file'. The values for
        these keys are expected to have a `name` attribute.

    Returns:
        A modified configuration dictionary with updated values for
        'config_dir' and 'config_file' keys.
    """
    new_config = dict()
    for prop in config:
        if prop in ['config_dir', 'config_file']:
            new_config[prop] = config[prop].name
        else:
            new_config['config_file'] = config['config_file'].name

    return new_config


def _fs_delete(directory: Path = None) -> Path:
    """
    Recursively deletes all contents of a directory and the directory itself.

    This function removes all files and directories within the specified directory
    and then deletes the directory itself. If any subdirectories are found, they
    are processed recursively.

    Args:

        directory: The path to the directory to delete. Defaults to None.

    Returns:
        The path of the directory after it is deleted.
    """
    for fobject in directory.iterdir():
        if fobject.is_dir():
            _fs_delete(fobject)
            fobject.rmdir()
        else:
            fobject.unlink()


def fs_delete(directory: Path = None) -> None:
    """
    Deletes a directory and its contents if applicable. This function ensures that
    the specified directory is removed, handling nested contents if any. It is a
    wrapper around `_fs_delete` to perform necessary cleanup operations.

    Args:

        directory: The directory path to delete. Defaults to None.
    """
    _fs_delete(directory)
    if directory.is_dir():
        directory.rmdir()


class ConfigManager(object):

    @classmethod
    def __init__(cls, config: dict = None, root_dir: Path = None) -> None:
        """
        Initializes the class with the provided configuration dictionary and root directory. If no
        configuration or root directory is provided, it will use default values. Ensures the creation
        of necessary directories as defined in the configuration. Handles reading and writing
        of configuration files to the disk, effectively storing and retrieving configuration state.

        Args:
            config: Configuration dictionary containing parameters and paths for initialization.

            root_dir: Root directory where configuration directories and files will be managed.
        """

        if not root_dir:
            root_dir = Path.home()

        if not config:
            config = default_config()

        config['config_dir'] = root_dir / config['config_dir']
        if not config['config_dir'].exists():
            config['config_dir'].mkdir(parents=True, exist_ok=True)

        config_file = config['config_dir'] / config["config_file"]

        # Read Configuration File, Continue
        if config_file.exists() and config_file.is_file() and config_file.stat().st_size > 0:
            cls.config = _enable_path_properties(loads(config_file.read_text()))
        else:  # Save Current Config
            cls.config = _enable_path_properties(config)
            config_file.write_text(dumps(_disable_path_properties(cls.config)))

    # The Config Directory will be deleted when using program implements if this __del__ is implemented
    @classmethod
    def __del__(cls) -> None:
        pass

    def remove_config(self):
        """
        Removes the configuration directory if it exists.

        The method checks for the existence of the configuration directory specified
        in the `config` attribute and deletes it using the `fs_delete` function.
        """
        if self.config['config_dir'].exists():
            fs_delete(self.config['config_dir'])

    @classmethod
    def print_config(cls):
        """
        Represents a method to print the class-level configuration attribute.

        This method is a class method, and it directly accesses the `config`
        class attribute of the associated class to display its value. Primarily
        useful for debugging or informational purposes to ensure the class-level
        configuration is correctly set.

        """
        print(f'{cls.config}')
