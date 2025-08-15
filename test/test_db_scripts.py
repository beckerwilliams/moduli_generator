"""
Tests for the db.scripts module.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from config import DEFAULT_MARIADB_DB_NAME, ModuliConfig
from db import Error, MariaDBConnector
from db.scripts import create_moduli_generator_user, initialize_moduli_generator, install_schema, moduli_stats, \
    verify_schema
from db.scripts.db_schema_for_named_db import get_moduli_generator_schema_statements


class TestVerifySchema:
    """Tests for the verify_schema module."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config object."""
        config = MagicMock(spec=ModuliConfig)
        config.get_logger.return_value = MagicMock()
        config.key_lengths = [4096, 8192]
        return config

    @patch("db.scripts.verify_schema.MariaDBConnector")
    def test_verify_schema_success(self, mock_connector, mock_config):
        """Test successful schema verification."""
        # Setup
        mock_connector.return_value = MagicMock()

        # Execute
        result = verify_schema.main(mock_config)

        # Verify
        assert result == 0
        mock_connector.assert_called_once_with(mock_config)
        mock_config.get_logger.return_value.info.assert_called()

    @patch("db.scripts.verify_schema.MariaDBConnector")
    def test_verify_schema_runtime_error(self, mock_connector, mock_config):
        """Test schema verification with RuntimeError."""
        # Setup
        mock_connector.side_effect = RuntimeError("Connection failed")

        # Execute
        result = verify_schema.main(mock_config)

        # Verify
        assert result == 1
        mock_connector.assert_called_once_with(mock_config)
        mock_config.get_logger.return_value.error.assert_called()

    @patch("db.scripts.verify_schema.MariaDBConnector")
    def test_verify_schema_value_error(self, mock_connector, mock_config):
        """Test schema verification with ValueError."""
        # Setup
        mock_connector.side_effect = ValueError("Invalid configuration")

        # Execute
        result = verify_schema.main(mock_config)

        # Verify
        assert result == 1
        mock_connector.assert_called_once_with(mock_config)
        mock_config.get_logger.return_value.error.assert_called()

    @patch("db.scripts.verify_schema.MariaDBConnector")
    def test_verify_schema_exception(self, mock_connector, mock_config):
        """Test schema verification with general Exception."""
        # Setup
        mock_connector.side_effect = Exception("Unexpected error")

        # Execute
        result = verify_schema.main(mock_config)

        # Verify
        assert result == 2
        mock_connector.assert_called_once_with(mock_config)
        mock_config.get_logger.return_value.error.assert_called()

    @patch("db.scripts.verify_schema.argparser_moduli_generator")
    @patch("db.scripts.verify_schema.MariaDBConnector")
    def test_verify_schema_no_config(
            self, mock_connector, mock_argparser_moduli_generator, mock_config
    ):
        """Test schema verification without passing a config."""
        # Setup
        mock_connector.return_value = MagicMock()
        mock_argparser_moduli_generator.local_config.return_value = mock_config

        # Execute
        result = verify_schema.main()

        # Verify
        assert result == 0
        mock_argparser_moduli_generator.local_config.assert_called_once()
        mock_connector.assert_called_once_with(mock_config)


class TestModuliStats:
    """Tests for the moduli_stats module."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config object."""
        config = MagicMock(spec=ModuliConfig)
        config.log_file = "test.log"
        return config

    @patch("db.scripts.moduli_stats.argparse.ArgumentParser.parse_args")
    @patch("db.scripts.moduli_stats.dump")
    @patch("db.scripts.moduli_stats.MariaDBConnector")
    @patch("db.scripts.moduli_stats.Path")
    def test_moduli_stats_with_output_file(
            self,
            mock_path_class,
            mock_connector,
            mock_dump,
            mock_parse_args,
            mock_config,
            tmp_path,
    ):
        """Test moduli_stats with a specific output file."""
        # Setup
        # Mock arguments object with the specified output file path
        output_file = str(tmp_path / "stats.json")

        mock_args = MagicMock()
        mock_args.output_file = output_file
        mock_parse_args.return_value = mock_args

        # Create a mock Path instance that will be returned by Path(output_file)
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.open.return_value.__enter__.return_value = MagicMock()

        mock_db = MagicMock()
        mock_db.stats.return_value = {"4096": 10, "8192": 20}
        mock_connector.return_value = mock_db

        # Execute
        moduli_stats.main(mock_config)

        # Verify
        mock_connector.assert_called_once_with(mock_config)
        mock_db.stats.assert_called_once()
        mock_dump.assert_called_once()

    @patch("db.scripts.moduli_stats.argparse.ArgumentParser.parse_args")
    @patch("db.scripts.moduli_stats.Path.open")
    @patch("db.scripts.moduli_stats.MariaDBConnector")
    def test_moduli_stats_default_output_file(
            self, mock_connector, mock_open, mock_parse_args, mock_config
    ):
        """Test moduli_stats with default output file."""
        # Setup
        # Mock arguments object with empty output_file
        mock_args = MagicMock()
        mock_args.output_file = None
        mock_parse_args.return_value = mock_args

        mock_db = MagicMock()
        mock_db.stats.return_value = {"4096": 10, "8192": 20}
        mock_connector.return_value = mock_db

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Execute
        with patch(
                "db.scripts.moduli_stats.Path.home", return_value=Path("/mock_home")
        ):
            moduli_stats.main(mock_config)

        # Verify
        mock_connector.assert_called_once_with(mock_config)
        mock_db.stats.assert_called_once()
        mock_open.assert_called_once()

    @patch("db.scripts.moduli_stats.argparse.ArgumentParser.parse_args")
    @patch("db.scripts.moduli_stats.Path.open")
    @patch("db.scripts.moduli_stats.MariaDBConnector")
    def test_moduli_stats_with_args(
            self, mock_connector, mock_open, mock_parse_args, mock_config
    ):
        """Test moduli_stats with command line arguments."""
        # Setup
        mock_db = MagicMock()
        mock_db.stats.return_value = {"4096": 10, "8192": 20}
        mock_connector.return_value = mock_db

        mock_args = MagicMock()
        mock_args.output_file = "test_output.json"
        mock_parse_args.return_value = mock_args

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Execute
        moduli_stats.main(mock_config)

        # Verify
        mock_connector.assert_called_once_with(mock_config)
        mock_db.stats.assert_called_once()
        mock_open.assert_called_once()

    @patch("db.scripts.moduli_stats.argparse.ArgumentParser.parse_args")
    @patch("db.scripts.moduli_stats.dump")
    @patch("db.scripts.moduli_stats.MariaDBConnector")
    @patch("db.scripts.moduli_stats.Path")
    def test_moduli_stats_empty_result(
            self,
            mock_path_class,
            mock_connector,
            mock_dump,
            mock_parse_args,
            mock_config,
            tmp_path,
    ):
        """Test moduli_stats with empty result from stats()."""
        # Setup
        # Mock arguments object with the specified output file path
        output_file = str(tmp_path / "empty_stats.json")

        mock_args = MagicMock()
        mock_args.output_file = output_file
        mock_parse_args.return_value = mock_args

        # Create a mock Path instance that will be returned by Path(output_file)
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.open.return_value.__enter__.return_value = MagicMock()

        mock_db = MagicMock()
        mock_db.stats.return_value = {}
        mock_connector.return_value = mock_db

        # Execute
        moduli_stats.main(mock_config)

        # Verify
        mock_connector.assert_called_once_with(mock_config)
        mock_db.stats.assert_called_once()
        mock_dump.assert_called_once_with({}, mock_dump.call_args[0][1], indent=4)


class TestInstallSchema:
    """Tests for the install_schema module and InstallSchema class."""

    @pytest.fixture
    def mock_connector(self):
        """Create a mock MariaDBConnector."""
        connector = MagicMock(spec=MariaDBConnector)
        return connector

    @pytest.fixture
    def install_schema_instance(self, mock_connector):
        """Create an InstallSchema instance with mock connector."""
        instance = install_schema.InstallSchema(mock_connector, "test_db")
        # Mock the schema_statements attribute to avoid calling get_moduli_generator_schema_statements
        instance.schema_statements = []
        return instance

    def test_install_schema_init(self, mock_connector):
        """Test InstallSchema initialization."""
        # Execute
        installer = install_schema.InstallSchema(mock_connector, "test_db")

        # Verify
        assert installer.db_conn == mock_connector
        assert installer.db_name == "test_db"

    def test_install_schema_success(self, install_schema_instance):
        """Test successful schema installation."""
        # Setup
        install_schema_instance.schema_statements = [
            {"query": "CREATE DATABASE test_db", "params": None, "fetch": False},
            {"query": "CREATE TABLE test_table", "params": None, "fetch": False},
        ]

        # Execute
        result = install_schema_instance.install_schema()

        # Verify
        assert result is True
        install_schema_instance.db_conn.sql.assert_called()

    def test_install_schema_error(self, install_schema_instance):
        """Test schema installation with error."""
        # Setup
        install_schema_instance.schema_statements = [
            {"query": "CREATE DATABASE test_db", "params": None, "fetch": False},
            {"query": "CREATE TABLE test_table", "params": None, "fetch": False},
        ]
        install_schema_instance.db_conn.sql.side_effect = RuntimeError("SQL error")

        # Execute
        result = install_schema_instance.install_schema()

        # Verify
        assert result is False

    def test_install_schema_batch_success(self, install_schema_instance):
        """Test successful batch schema installation."""
        # Setup
        install_schema_instance.schema_statements = [
            {"query": "CREATE DATABASE test_db", "params": None, "fetch": False},
            {"query": "CREATE TABLE test_table", "params": None, "fetch": False},
        ]
        install_schema_instance.db_conn.execute_batch.return_value = True

        # Execute
        result = install_schema_instance.install_schema_batch()

        # Verify
        assert result is True
        install_schema_instance.db_conn.execute_batch.assert_called_once()

    def test_install_schema_batch_error(self, install_schema_instance):
        """Test batch schema installation with error."""
        # Setup
        install_schema_instance.schema_statements = [
            {"query": "CREATE DATABASE test_db", "params": None, "fetch": False},
            {"query": "CREATE TABLE test_table", "params": None, "fetch": False},
        ]
        install_schema_instance.db_conn.execute_batch.side_effect = RuntimeError(
            "SQL error"
        )

        # Execute
        result = install_schema_instance.install_schema_batch()

        # Verify
        assert result is False

    @patch("pathlib.Path.exists")
    def test_install_schema_file_no_file(self, mock_exists, install_schema_instance):
        """Test schema file installation with no file provided."""
        # Setup
        mock_exists.return_value = False

        # Execute
        result = install_schema_instance.install_schema_file()

        # Verify
        assert result is False

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=MagicMock)
    def test_install_schema_file_success(
            self, mock_open, mock_exists, install_schema_instance, tmp_path
    ):
        """Test successful schema file installation."""
        # Setup
        schema_file = tmp_path / "schema.sql"
        schema_content = "CREATE DATABASE test_db;"

        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = schema_content
        mock_open.return_value = mock_file

        # Execute
        result = install_schema_instance.install_schema_file(schema_file)

        # Verify
        assert result is True
        install_schema_instance.db_conn.sql.assert_called()

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=MagicMock)
    def test_install_schema_file_error(
            self, mock_open, mock_exists, install_schema_instance, tmp_path
    ):
        """Test schema file installation with SQL error."""
        # Setup
        schema_file = tmp_path / "schema.sql"
        schema_content = "CREATE DATABASE test_db;"

        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = schema_content
        mock_open.return_value = mock_file

        install_schema_instance.db_conn.sql.side_effect = Error("SQL error")

        # Execute
        result = install_schema_instance.install_schema_file(schema_file)

        # Verify
        assert result is False
        install_schema_instance.db_conn.sql.assert_called()

    @patch("db.scripts.install_schema.print")
    def test_main_with_batch(self, mock_print):
        """Test main function with batch argument."""
        # Mock the necessary components
        with patch("db.scripts.install_schema.ArgumentParser") as mock_argparse, patch(
                "db.scripts.install_schema.default_config"
        ) as mock_config, patch("db.scripts.install_schema.Path") as mock_path, patch(
            "db.scripts.install_schema.MariaDBConnector"
        ) as mock_connector, patch(
            "db.scripts.install_schema.InstallSchema"
        ) as mock_installer_class, patch(
            "db.scripts.install_schema.parse_mysql_config"
        ) as mock_parse_mysql_config:
            # Setup mock arguments
            mock_args = MagicMock()
            mock_args.mariadb_cnf = "/path/to/mariadb.cnf"
            mock_args.batch = True
            mock_args.moduli_db_name = "test_db"
            mock_argparse.return_value.parse_args.return_value = mock_args

            # Setup mock objects
            mock_path_instance = MagicMock()
            mock_path.return_value = mock_path_instance

            mock_connector_instance = MagicMock()
            mock_connector.return_value = mock_connector_instance

            mock_installer = MagicMock()
            mock_installer.install_schema_batch.return_value = True
            mock_installer_class.return_value = mock_installer

            # Setup mock for parse_mysql_config
            mock_parse_mysql_config.return_value = {
                "client": {
                    "host": "localhost",
                    "user": "root",
                    "password": "password"
                }
            }

            # Execute
            install_schema.main()

            # Verify
            mock_installer.install_schema_batch.assert_called_once()
            # Check that success message was printed
            mock_print.assert_any_call("Database schema installed successfully")

    @patch("db.scripts.install_schema.print")
    def test_main_default(self, mock_print):
        """Test main function with default arguments."""
        # Mock the necessary components
        with patch("db.scripts.install_schema.ArgumentParser") as mock_argparse, patch(
                "db.scripts.install_schema.default_config"
        ) as mock_config, patch("db.scripts.install_schema.Path") as mock_path, patch(
            "db.scripts.install_schema.MariaDBConnector"
        ) as mock_connector, patch(
            "db.scripts.install_schema.InstallSchema"
        ) as mock_installer_class, patch(
            "db.scripts.install_schema.parse_mysql_config"
        ) as mock_parse_mysql_config:
            # Setup mock arguments
            mock_args = MagicMock()
            mock_args.mariadb_cnf = "/path/to/mariadb.cnf"
            mock_args.batch = False
            mock_args.moduli_db_name = "test_db"
            mock_argparse.return_value.parse_args.return_value = mock_args

            # Setup mock objects
            mock_path_instance = MagicMock()
            mock_path.return_value = mock_path_instance

            mock_connector_instance = MagicMock()
            mock_connector.return_value = mock_connector_instance

            mock_installer = MagicMock()
            mock_installer.install_schema.return_value = True
            mock_installer_class.return_value = mock_installer

            # Setup mock for parse_mysql_config
            mock_parse_mysql_config.return_value = {
                "client": {
                    "host": "localhost",
                    "user": "root",
                    "password": "password"
                }
            }

            # Execute
            install_schema.main()

            # Verify
            mock_installer.install_schema.assert_called_once()
            # Check that success message was printed
            mock_print.assert_any_call("Database schema installed successfully")

    @patch("db.scripts.install_schema.print")
    def test_main_failure(self, mock_print):
        """Test main function with installation failure."""
        # Mock the necessary components
        with patch("db.scripts.install_schema.ArgumentParser") as mock_argparse, patch(
                "db.scripts.install_schema.default_config"
        ) as mock_config, patch("db.scripts.install_schema.Path") as mock_path, patch(
            "db.scripts.install_schema.MariaDBConnector"
        ) as mock_connector, patch(
            "db.scripts.install_schema.InstallSchema"
        ) as mock_installer_class:
            # Setup mock arguments
            mock_args = MagicMock()
            mock_args.mariadb_cnf = "/path/to/mariadb.cnf"
            mock_args.batch = False
            mock_args.moduli_db_name = "test_db"
            mock_argparse.return_value.parse_args.return_value = mock_args

            # Setup mock objects
            mock_path_instance = MagicMock()
            mock_path.return_value = mock_path_instance

            mock_connector_instance = MagicMock()
            mock_connector.return_value = mock_connector_instance

            mock_installer = MagicMock()
            mock_installer.install_schema.return_value = False
            mock_installer_class.return_value = mock_installer

            # Execute
            install_schema.main()

            # Verify
            mock_installer.install_schema.assert_called_once()
            # Check that failure message was printed
            mock_print.assert_any_call("Failed to install database schema")

    def test_main_connector_error(self):
        """Test main function with MariaDBConnector error."""
        # Mock the necessary components
        with patch("db.scripts.install_schema.ArgumentParser") as mock_argparse, patch(
                "db.scripts.install_schema.default_config"
        ) as mock_config, patch("db.scripts.install_schema.Path") as mock_path, patch(
            "db.scripts.install_schema.MariaDBConnector"
        ) as mock_connector:
            # Setup mock arguments
            mock_args = MagicMock()
            mock_args.mariadb_cnf = "/path/to/mariadb.cnf"
            mock_args.moduli_db_name = "test_db"
            mock_argparse.return_value.parse_args.return_value = mock_args

            # Simulate error during connector creation
            mock_connector.side_effect = Error("Connection error")

            # Execute with exception expectation
            with pytest.raises(Error):
                install_schema.main()


class TestCreateModuliGeneratorUser:
    """Tests for the create_moduli_generator_user module."""

    def test_create_moduli_generator_user_default(self):
        """Test create_moduli_generator_user with default password."""
        # Setup
        mock_db_conn = MagicMock()
        
        # Execute
        result = create_moduli_generator_user.create_moduli_generator_user(mock_db_conn, "test_db")

        # Verify
        assert isinstance(result, str)  # Should return a password string
        assert len(result) > 0  # Password should not be empty
        mock_db_conn.sql.assert_called()  # SQL execution should be called

    def test_create_moduli_generator_user_custom_password(self):
        """Test create_moduli_generator_user with custom password."""
        # Setup
        mock_db_conn = MagicMock()
        custom_password = "test_password"
        
        # Execute
        result = create_moduli_generator_user.create_moduli_generator_user(
            mock_db_conn, "test_db", custom_password
        )

        # Verify
        assert result == custom_password  # Should return the same password that was passed in
        mock_db_conn.sql.assert_called()  # SQL execution should be called

    @patch("db.scripts.create_moduli_generator_user.argparse")
    @patch("db.scripts.create_moduli_generator_user.MariaDBConnector")
    @patch("db.scripts.create_moduli_generator_user.create_moduli_generator_user")
    def test_main_success(self, mock_create_user, mock_connector, mock_argparse):
        """Test main function success."""
        # Setup
        mock_args = MagicMock()
        mock_args.mariadb_cnf = "/path/to/config.cnf"
        mock_args.batch = True
        mock_argparse.return_value = mock_args

        mock_db = MagicMock()
        mock_connector.return_value = mock_db

        mock_create_user.return_value = "generated_password"

        # Execute
        create_moduli_generator_user.main()

        # Verify
        mock_connector.assert_called_once()
        mock_create_user.assert_called_once_with(mock_db, DEFAULT_MARIADB_DB_NAME)
        assert mock_db.mariadb_cnf == Path("/path/to/config.cnf")

    @patch("db.scripts.create_moduli_generator_user.argparse")
    @patch("db.scripts.create_moduli_generator_user.MariaDBConnector")
    @patch("db.scripts.create_moduli_generator_user.create_moduli_generator_user")
    @patch("db.scripts.create_moduli_generator_user.print")
    def test_main_prints_statements(self, mock_print, mock_create_user, mock_connector, mock_argparse):
        """Test that main function prints password."""
        # Setup
        mock_args = MagicMock()
        mock_args.mariadb_cnf = "/path/to/config.cnf"
        mock_args.batch = True
        mock_argparse.return_value = mock_args

        mock_db = MagicMock()
        mock_connector.return_value = mock_db

        # Mock the create_moduli_generator_user function to return a password
        test_password = "generated_password"
        mock_create_user.return_value = test_password

        # Execute
        create_moduli_generator_user.main()

        # Verify
        mock_print.assert_called()
        # The argument to print should include the generated password
        mock_print.assert_any_call(f"Generated password: {test_password}")

    @patch("db.scripts.create_moduli_generator_user.argparse")
    @patch("db.scripts.create_moduli_generator_user.MariaDBConnector")
    @patch("db.scripts.create_moduli_generator_user.create_moduli_generator_user")
    def test_main_db_error(self, mock_create_user, mock_connector, mock_argparse):
        """Test main function with database error."""
        # Setup
        mock_args = MagicMock()
        mock_args.mariadb_cnf = "/path/to/config.cnf"
        mock_args.batch = True
        mock_argparse.return_value = mock_args

        mock_db = MagicMock()
        mock_connector.return_value = mock_db

        # Make the create_moduli_generator_user function raise an error
        mock_create_user.side_effect = RuntimeError("Database error")

        # Execute with exception expectation
        with pytest.raises(RuntimeError):
            create_moduli_generator_user.main()


class TestDbSchemaForNamedDb:
    """Tests for the db_schema_for_named_db module."""

    def test_get_moduli_generator_schema_statements_default(self):
        """Test get_moduli_generator_schema_statements with default database name."""
        # Execute
        result = get_moduli_generator_schema_statements()

        # Verify
        assert isinstance(result, list)
        assert len(result) == 10  # Check that all expected statements are present

        # Check each statement type exists
        assert "CREATE DATABASE" in result[0]["query"]
        assert "test_moduli_db" in result[0]["query"]

        assert "CREATE TABLE" in result[1]["query"]
        assert "mod_fl_consts" in result[1]["query"]

        assert "CREATE TABLE" in result[2]["query"]
        assert "moduli" in result[2]["query"]

        assert "CREATE VIEW" in result[3]["query"]
        assert "moduli_view" in result[3]["query"]

        assert "CREATE TABLE" in result[4]["query"]
        assert "moduli_archive" in result[4]["query"]

        assert "CREATE INDEX idx_size" in result[5]["query"]
        assert "test_moduli_db.moduli" in result[5]["query"]
        assert "CREATE INDEX idx_timestamp" in result[6]["query"]
        assert "test_moduli_db.moduli" in result[6]["query"]
        assert "CREATE INDEX idx_size" in result[7]["query"]
        assert "test_moduli_db.moduli_archive" in result[7]["query"]
        assert "CREATE INDEX idx_timestamp" in result[8]["query"]
        assert "test_moduli_db.moduli_archive" in result[8]["query"]

        # Check INSERT statement has parameters
        assert "INSERT INTO" in result[9]["query"]
        assert "mod_fl_consts" in result[9]["query"]
        assert result[9]["params"] is not None
        assert len(result[9]["params"]) == 6

    def test_get_moduli_generator_schema_statements_custom_db(self):
        """Test get_moduli_generator_schema_statements with custom database name."""
        # Execute
        result = get_moduli_generator_schema_statements("custom_db")

        # Verify
        assert isinstance(result, list)
        assert len(result) == 10  # Check that all expected statements are present

        # Verify custom database name is used
        for statement in result:
            assert "custom_db" in statement["query"]

        # Check specific statement types
        assert "CREATE DATABASE IF NOT EXISTS custom_db" in result[0]["query"]
        assert "mod_fl_consts" in result[1]["query"]
        assert "moduli" in result[2]["query"]
        assert "moduli_view" in result[3]["query"]
        assert "moduli_archive" in result[4]["query"]

    def test_get_moduli_generator_schema_statements_invalid_db_name(self):
        """Test get_moduli_generator_schema_statements with invalid database name."""
        # Execute and verify
        with pytest.raises(ValueError, match="Invalid database name"):
            get_moduli_generator_schema_statements("invalid;db")


class TestInitializeModuliGenerator:
    """Tests for the initialize_moduli_generator module."""

    @patch("db.scripts.initialize_moduli_generator.arg_parser")
    @patch("db.scripts.initialize_moduli_generator.default_config")
    @patch("db.scripts.initialize_moduli_generator.ModuliGenerator")
    @patch("db.scripts.initialize_moduli_generator.Path")
    @patch("db.scripts.initialize_moduli_generator.InstallSchema")
    def test_create_moduli_generator_home_success(
            self, mock_installer, mock_path, mock_generator, mock_config, mock_arg_parser
    ):
        """Test successful creation of moduli generator home."""
        # Setup
        mock_args = MagicMock()
        mock_args.mariadb_cnf = "/path/to/mysql.cnf"
        mock_args.mariadb_name = "test_db"
        mock_args.moduli_home = "/path/to/moduli"
        mock_args.batch = False
        mock_arg_parser.return_value = mock_args

        # Mock Path.exists to return True for mariadb_cnf
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.read_text.return_value = "mock config content"
        mock_path.return_value = mock_path_instance

        # Mock generator and its config
        mock_generator_instance = MagicMock()
        mock_generator_instance.config.mariadb_cnf = "/path/to/moduli_generator.cnf"
        mock_generator_instance.db = MagicMock()
        mock_generator_instance.config.db_name = "test_db"
        mock_generator.return_value = mock_generator_instance

        # Mock InstallSchema
        mock_installer_instance = MagicMock()
        mock_installer.return_value = mock_installer_instance

        # Execute
        result = initialize_moduli_generator.create_moduli_generator_home()

        # Verify
        assert result == 0
        mock_generator.assert_called_once()
        mock_installer.assert_called_once_with(mock_generator_instance.db, "test_db")
        mock_installer_instance.install_schema.assert_called_once()

    @patch("db.scripts.initialize_moduli_generator.arg_parser")
    @patch("db.scripts.initialize_moduli_generator.default_config")
    @patch("db.scripts.initialize_moduli_generator.ModuliGenerator")
    @patch("db.scripts.initialize_moduli_generator.Path")
    @patch("db.scripts.initialize_moduli_generator.InstallSchema")
    def test_create_moduli_generator_home_batch_mode(
            self, mock_installer, mock_path, mock_generator, mock_config, mock_arg_parser
    ):
        """Test creation of moduli generator home in batch mode."""
        # Setup
        mock_args = MagicMock()
        mock_args.mariadb_cnf = "/path/to/mysql.cnf"
        mock_args.mariadb_name = "test_db"
        mock_args.moduli_home = "/path/to/moduli"
        mock_args.batch = True
        mock_arg_parser.return_value = mock_args

        # Mock Path.exists to return True for mariadb_cnf
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.read_text.return_value = "mock config content"
        mock_path.return_value = mock_path_instance

        # Mock generator and its config
        mock_generator_instance = MagicMock()
        mock_generator_instance.config.mariadb_cnf = "/path/to/moduli_generator.cnf"
        mock_generator_instance.db = MagicMock()
        mock_generator_instance.config.db_name = "test_db"
        mock_generator.return_value = mock_generator_instance

        # Mock InstallSchema
        mock_installer_instance = MagicMock()
        mock_installer.return_value = mock_installer_instance

        # Execute
        result = initialize_moduli_generator.create_moduli_generator_home()

        # Verify
        assert result == 0
        mock_installer_instance.install_schema_batch.assert_called_once()

    @patch("db.scripts.initialize_moduli_generator.arg_parser")
    @patch("db.scripts.initialize_moduli_generator.default_config")
    @patch("db.scripts.initialize_moduli_generator.ModuliGenerator")
    @patch("db.scripts.initialize_moduli_generator.Path")
    @patch("db.scripts.initialize_moduli_generator.print")
    def test_create_moduli_generator_home_config_not_found(
            self, mock_print, mock_path, mock_generator, mock_config, mock_arg_parser
    ):
        """Test creation of moduli generator home when config file not found."""
        # Setup
        mock_args = MagicMock()
        mock_args.mariadb_cnf = "/path/to/mysql.cnf"
        mock_arg_parser.return_value = mock_args

        # Mock Path.exists to return False for mariadb_cnf
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        # Execute
        result = initialize_moduli_generator.create_moduli_generator_home()

        # Verify
        assert result == 1
        mock_print.assert_called_once()
        assert "MariaDB config file not found" in mock_print.call_args[0][0]

    @patch("db.scripts.initialize_moduli_generator.arg_parser")
    @patch("db.scripts.initialize_moduli_generator.default_config")
    @patch("db.scripts.initialize_moduli_generator.ModuliGenerator")
    @patch("db.scripts.initialize_moduli_generator.Path")
    def test_create_moduli_generator_home_db_name_fallback(
            self, mock_path, mock_generator, mock_config, mock_arg_parser
    ):
        """Test fallback to default db_name if not in config."""
        # Setup
        mock_args = MagicMock()
        mock_args.mariadb_cnf = "/path/to/mysql.cnf"
        mock_args.mariadb_name = "test_db"
        mock_args.moduli_home = "/path/to/moduli"
        mock_args.batch = False
        mock_arg_parser.return_value = mock_args

        # Mock Path.exists to return True for mariadb_cnf
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.read_text.return_value = "mock config content"
        mock_path.return_value = mock_path_instance

        # Mock generator with config missing db_name
        mock_generator_instance = MagicMock()
        mock_generator_instance.config.mariadb_cnf = "/path/to/moduli_generator.cnf"
        mock_generator_instance.db = MagicMock()
        # Remove db_name from config to test fallback
        delattr(mock_generator_instance.config, "db_name")
        mock_generator.return_value = mock_generator_instance

        # Mock InstallSchema
        mock_installer = MagicMock()
        mock_installer_instance = MagicMock()
        mock_installer.return_value = mock_installer_instance

        # Install patch for InstallSchema
        with patch(
                "db.scripts.initialize_moduli_generator.InstallSchema", mock_installer
        ):
            # Execute
            result = initialize_moduli_generator.create_moduli_generator_home()

            # Verify
            assert result == 0
            # Should use "moduli_db" as fallback
            mock_installer.assert_called_once_with(
                mock_generator_instance.db, "moduli_db"
            )

    def test_arg_parser(self):
        """Test arg_parser function with default arguments."""
        # Mock sys.argv
        with patch("sys.argv", ["initialize_moduli_generator.py"]):
            # Execute
            args = initialize_moduli_generator.arg_parser()

            # Verify
            assert hasattr(args, "moduli_home")
            assert hasattr(args, "mariadb_cnf")
            assert hasattr(args, "mariadb_name")
            assert hasattr(args, "batch")
            assert args.batch is False
