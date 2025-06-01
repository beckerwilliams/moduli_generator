import importlib.metadata as importlib_metadata
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from logging import (INFO, basicConfig, getLogger)
from pathlib import PosixPath as Path
from random import shuffle

from config_manager import (ConfigManager)

basicConfig(level=INFO)
logger = getLogger(__name__)

__version__ = importlib_metadata.version('moduli_assembly')


def ISO_UTC_TIMESTAMP() -> str:
    """ Returns Current Timestamp in ISO Format with TZ=UTC
    Returns:
        Current ISO TimeStamp, TZ=UTC
    """
    return datetime.now(tz=timezone.utc).isoformat()


def default_config() -> dict:
    """ Returns Default Configuration for Moduli_Assembly Operation

    Returns:
        Sufficient configuration for Moduli_Assembly Operation
    """
    return {
        'generator_type': 2,
        'auth_bitsizes': [3072, 4096, 6144, 7680, 8192],
        'config_dir': '.moduli_assembly',
        'config_file': '.config',
        'moduli_dir': '.moduli',
        'moduli_file': 'MODULI_FILE'
    }


class ModuliAssembly(ConfigManager):

    @property
    def version(self) -> str:
        """
        Returns:

            version
        """

        return __version__

    def __init__(self, config: dict = None, root_dir: Path = None) -> None:
        """
        Initialize the class with the provided configuration and root directory.

        This constructor function initializes the class by setting up the configuration
        and operational directories. It ensures all required configuration attributes
        are present, sets up the necessary paths for operational files, and creates missing
        directories if needed.

        Args:

            config: A dictionary of configuration settings. If not provided, the
                    default configuration will be used.

            root_dir: The directory path where root-level configuration will reside.
                      Defaults to the user's home directory if not provided.
        """
        if not root_dir:
            root_dir = Path.home()

        if not config:
            config = default_config()

        # Validate Attributes
        for attr in default_config().keys():
            if attr not in config:
                raise AttributeError(f'Config Required Attribute: {attr}: Missing')

        super().__init__(config, root_dir)

        # Operational Config has 'moduli_dir' as a full path under the selected config dir
        self.config['moduli_dir'] = self.config['config_dir'] / Path(config['moduli_dir'])

        self.config['moduli_dir'].mkdir(exist_ok=True)
        self.config['moduli_file'] = self.config['config_dir'] / Path(config['moduli_file'])

        self.config['auth_bitsizes'] = config['auth_bitsizes']
        self.config['generator_type'] = config['generator_type']

    def create_checkpoint_filename(self, path: Path) -> Path:
        """Creates a checkpoint filename based on the provided path.

        Args:
            path: The base path for the checkpoint file.

        Returns:
            The full path to the checkpoint file.
        """
        return self.config['moduli_dir'] / Path(f'.{path.name}')
        # return self.config['moduli_dir'].joinpath(f'.{path.name}')

    def create_candidate_path(self, key_length: int):
        """
        Generates a candidate file path for a given key length and timestamp in the moduli directory
        specified in the configuration. The candidate file is then created in the determined path.

        Args:

            key_length: Key length indicating the size of the keys for which the candidate file is generated.

        Returns:
            The path of the candidate file as a Path object.
        """
        candidate_path = self.config['moduli_dir'] / Path(f'{key_length}.candidate_{ISO_UTC_TIMESTAMP()}')
        candidate_path.touch()
        return candidate_path

    @staticmethod
    def get_screened_path(path: Path) -> Path:
        """
        Constructs a new file path by replacing the substring "candidate" in the
        file name with "screened". The directory of the given file path remains
        unchanged in the new path.

        Args:
            path: The original file path from which the directory and file
                  name are used to construct the new path. The file name should
                  include the substring "candidate" for meaningful replacement.

        Returns:
            A new file path with the substring "candidate" in the file name
            replaced by "screened".
        """

        return path.parent / Path(str(path.name).replace('candidate', 'screened'))

    def screen_candidates(self, candidate_path: Path) -> Path:
        """Screens candidate moduli for safe primes.

        Args:
            candidate_path: Path to the file containing generated moduli.

        Returns:
            Path to the screened moduli file.

        Raises:
            RuntimeError: If screening fails.
        """
        logger.info(f'Screening {candidate_path} for Safe Primes (generator={self.config["generator_type"]})')

        try:
            screen_command = [
                'ssh-keygen',
                '-M', 'screen',
                '-O', f'generator={self.config["generator_type"]}',
                '-O', f'checkpoint={self.create_checkpoint_filename(candidate_path)}',
                '-f', str(candidate_path),
                str(self.get_screened_path(candidate_path))
            ]
            subprocess.run(screen_command, text=True, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f'Error screening candidates for {candidate_path.name.split(".")[0]} bit length: {e}')

        if candidate_path.exists():
            candidate_path.unlink()

        return self.get_screened_path(candidate_path)

    def generate_candidates(self, key_length: int, count: int) -> Path:
        """Generates candidate moduli files for the specified key length.

        Args:
            key_length: Maximum moduli key length.
            count: Number of moduli to generate.

        Returns:
            Path to the candidate file.

        Raises:
            ValueError: If key_length or count is invalid.
            RuntimeError: If generation fails.
        """
        if key_length <= 0 or count <= 0:
            raise ValueError("key_length and count must be positive integers")

        logger.info(f'Generating candidate files for modulus size: {key_length}')
        candidate_file = self.create_candidate_path(key_length)

        for _ in range(count):
            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    gen_command = [
                        'ssh-keygen',
                        '-M', 'generate',
                        '-O', f'bits={key_length}',
                        temp_file.name
                    ]
                    subprocess.run(gen_command, check=True, text=True)

                    # Append temporary file content to candidate file
                    with open(temp_file.name, 'r') as src, candidate_file.open('a') as dst:
                        shutil.copyfileobj(src, dst)

            except subprocess.CalledProcessError as e:
                raise RuntimeError(f'Error generating {key_length}-bit prime: {e}')

            finally:
                if Path(temp_file.name).exists():
                    Path(temp_file.name).unlink()

        return candidate_file

    def create_moduli_file(self, f_path: Path = None) -> Path:
        """Creates a moduli file by combining screened moduli.

        Args:
            f_path: Path to the moduli file. Defaults to the configured moduli file.

        Returns:
            Path to the created moduli file.
        """
        if not f_path:
            f_path = self.config['config_dir'] / self.config['moduli_file']

        ts = ISO_UTC_TIMESTAMP()
        ts_name = f"{f_path.absolute()}_{ts}"
        path = Path(ts_name)
        path.touch()

        if f_path.exists():
            f_path.unlink(missing_ok=True)
        f_path.symlink_to(path)

        moduli_files = sorted(self.config['moduli_dir'].glob('????.screened*'))
        content = [f'#/etc/ssh/moduli: creation_date: moduli_assembly: {ts}']

        for modulus_file in moduli_files:
            lines = modulus_file.read_text().strip().split('\n')
            shuffle(lines)
            content.extend(lines)

        path.write_text('\n'.join(content))
        return path

    def restart_candidate_screening(self):
        """
        Restart Screening of Any Interrupted Screening of Candidate Modulus Files

        """
        for modulus_file in [moduli for moduli in self.config['moduli_dir'].glob('????.candidate*')]:
            self.screen_candidates(candidate_path=modulus_file)

    def clear_artifacts(self) -> None:
        """
        Removes all files present in the directory specified in the configuration
        under the key 'moduli_dir'. This method iterates through all files in the 
        given directory and deletes them one by one.
        """
        for file in self.config['moduli_dir'].glob('*'):
            file.unlink()
