#!/usr/bin/env python3
import secrets
import string


def generate_random_password(length=32) -> str:
    """
    Generates a random password of the specified length, consisting of letters, digits,
    and MariaDB-recommended safe special characters. This method uses cryptographically
    secure random number generation to ensure unpredictability of the password.

    Args:
        length (int): The desired length of the generated password.

    Returns:
        str: A randomly generated password containing letters, digits, and safe special characters.
    """
    # Define character sets
    letters_digits = string.ascii_letters + string.digits
    # Include only MariaDB.com recommended safe special characters, excluding quotes and backslash
    safe_punctuation = '+-*/,.,:;!?#$%&@=^_~|<>()[]{}'
    alphabet = letters_digits + safe_punctuation

    # Generate the password using secrets module
    password = ''.join(secrets.choice(alphabet) for _ in range(length))

    return password


def main():
    print(generate_random_password())


if __name__ == "__main__":
    exit(main())
