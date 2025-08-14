#!/usr/bin/env python3
"""
Test script to verify connection to the MariaDB Docker container.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config import default_config
from db import MariaDBConnector


def test_connection():
    """Test the connection to the MariaDB database."""
    print("Testing connection to MariaDB Docker container...")
    print(f"Using config file: {default_config.mariadb_cnf}")

    try:
        # Create a database connector
        db_connector = MariaDBConnector(default_config)

        # Try a simple query to verify the connection
        result = db_connector.sql("SELECT 1 as test")

        if result and result[0]['test'] == 1:
            print("✅ Connection successful!")

            # Get database schema verification results
            schema_result = db_connector.verify_schema()
            if schema_result['overall_status'] == 'PASSED':
                print("✅ Database schema verification passed!")
            elif schema_result['overall_status'] == 'PASSED_WITH_WARNINGS':
                print("⚠️ Database schema verification passed with warnings:")
                for warning in schema_result['warnings']:
                    print(f"  - {warning}")
            else:
                print("❌ Database schema verification failed:")
                for error in schema_result['errors']:
                    print(f"  - {error}")

            # Print database statistics
            try:
                stats = db_connector.stats()
                print("\nDatabase Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
            except Exception as e:
                print(f"Error getting database statistics: {e}")

            return True
        else:
            print("❌ Connection test failed: Unexpected result")
            return False

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure the Docker container is running:")
        print("   docker ps | grep moduli_generator_mariadb")
        print("2. Check if MariaDB is accepting connections:")
        print("   docker-compose logs mariadb")
        print("3. Verify your configuration file (~/.moduli_generator/moduli_generator.cnf) has the correct settings:")
        print("   host = localhost")
        print("   port = 3306")
        print("   user = moduli_generator")
        print("   password = moduli_password")
        print("   database = moduli_db")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
