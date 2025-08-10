#!/usr/bin/env python3
"""
Test script for traversable_resources.py
"""
from moduli_generator.utils.traversable_resources import (
    get_data_resources,
    list_data_resources,
)


def main():
    """
    Test the traversable_resources module functionality.
    """
    print("Testing get_data_resources():")
    resources = get_data_resources()
    print(f"Found {len(resources)} resources\n")

    print("Testing list_data_resources():")
    list_data_resources()


if __name__ == "__main__":
    main()
