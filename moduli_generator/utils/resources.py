# resources.py - Place this in your project's main package

"""
Resources module for moduli_generator.

Provides consistent access to package resources (data files, SQL scripts, config files, etc.)
across different environments (development, installed package, wheel distribution).
"""

import importlib.resources as pkg_resources
from importlib.resources import abc
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, TextIO, Union


class ResourceManager:
    """
    Resource manager for accessing package resources reliably in any environment.

    This class provides methods to access resources included in the moduli_generator package,
    whether running from source code, installed via pip, or packaged in a wheel.
    It handles resources like SQL scripts, shell scripts, configuration files, etc.
    """

    @staticmethod
    def get_resource(
            package: str, resource_path: Optional[str] = None
    ) -> Union[abc.Traversable, List[abc.Traversable]]:
        """
        Access a package resource or list resources in a package.

        Args:
            package: The package name containing resources (e.g., 'moduli_generator.data')
            resource_path: Optional path to a specific resource within the package

        Returns:
            Either a specific resource or list of all resources in the package/directory
        """
        try:
            package_resources = pkg_resources.files(package)

            if resource_path:
                return package_resources.joinpath(resource_path)

            return list(package_resources.iterdir())
        except (ImportError, ModuleNotFoundError, ValueError) as e:
            raise ResourceError(
                f"Failed to access resource in package '{package}': {e}"
            )

    @staticmethod
    def get_text(package: str, resource_path: str) -> str:
        """
        Get the text content of a resource file.

        Args:
            package: The package name containing the resource
            resource_path: Path to the specific resource within the package

        Returns:
            The text content of the specified resource
        """
        resource = ResourceManager.get_resource(package, resource_path)
        try:
            with resource.open("r") as f:
                return f.read()
        except Exception as e:
            raise ResourceError(f"Failed to read text from '{resource_path}': {e}")

    @staticmethod
    def get_binary(package: str, resource_path: str) -> bytes:
        """
        Get the binary content of a resource file.

        Args:
            package: The package name containing the resource
            resource_path: Path to the specific resource within the package

        Returns:
            The binary content of the specified resource
        """
        resource = ResourceManager.get_resource(package, resource_path)
        try:
            with resource.open("rb") as f:
                return f.read()
        except Exception as e:
            raise ResourceError(
                f"Failed to read binary data from '{resource_path}': {e}"
            )

    @staticmethod
    def get_path(package: str, resource_path: str) -> Path:
        """
        Get a filesystem path to a resource for operations requiring real paths.

        Args:
            package: The package name containing the resource
            resource_path: Path to the specific resource within the package

        Returns:
            A Path object pointing to the resource in the filesystem
        """
        resource = ResourceManager.get_resource(package, resource_path)
        try:
            # Use as_file to get a filesystem path (works in wheels too)
            with pkg_resources.as_file(resource) as path:
                # Return a copy of the path as the context manager will invalidate it
                return Path(str(path))
        except Exception as e:
            raise ResourceError(
                f"Failed to get filesystem path for '{resource_path}': {e}"
            )

    @staticmethod
    def open_text(package: str, resource_path: str, mode: str = "r") -> TextIO:
        """
        Open a text resource file and return a file handle.

        Args:
            package: The package name containing the resource
            resource_path: Path to the specific resource within the package
            mode: File opening mode (must be a text mode)

        Returns:
            An open file handle to the resource
        """
        if "b" in mode:
            raise ValueError("Binary mode not allowed for open_text")

        resource = ResourceManager.get_resource(package, resource_path)
        try:
            return resource.open(mode)
        except Exception as e:
            raise ResourceError(f"Failed to open text resource '{resource_path}': {e}")

    @staticmethod
    def open_binary(package: str, resource_path: str, mode: str = "rb") -> BinaryIO:
        """
        Open a binary resource file and return a file handle.

        Args:
            package: The package name containing the resource
            resource_path: Path to the specific resource within the package
            mode: File opening mode (must be a binary mode)

        Returns:
            An open file handle to the resource
        """
        if "b" not in mode:
            raise ValueError("Binary mode required for open_binary")

        resource = ResourceManager.get_resource(package, resource_path)
        try:
            return resource.open(mode)
        except Exception as e:
            raise ResourceError(
                f"Failed to open binary resource '{resource_path}': {e}"
            )

    @staticmethod
    def list_resources(
            package: str, resource_type: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        List all resources in a package, optionally filtered by type.

        Args:
            package: The package name containing resources
            resource_type: Optional filter for resource types (e.g., 'sql', 'sh', 'py')

        Returns:
            A list of dictionaries with resource information (path, type, name)
        """
        resources_list = []
        try:
            # Get all resources in the package
            resources = ResourceManager.get_resource(package)

            if not isinstance(resources, list):
                resources = [resources]

            for resource in resources:
                # Skip if not a file or doesn't match the type filter
                if not resource.is_file():
                    continue

                name = resource.name
                ext = Path(name).suffix.lstrip(".")

                if resource_type and ext != resource_type:
                    continue

                # Add resource info to the list
                resources_list.append(
                    {
                        "name": name,
                        "type": ext,
                        "path": str(resource).replace(
                            "\\", "/"
                        ),  # Normalize path separators
                    }
                )

            return resources_list
        except Exception as e:
            raise ResourceError(f"Failed to list resources in package '{package}': {e}")


class ResourceError(Exception):
    """Exception raised for errors in the resource module."""

    pass


# Convenience functions to use directly without instantiating ResourceManager
def get_resource(
        package: str, resource_path: Optional[str] = None
) -> Union[abc.Traversable, List[abc.Traversable]]:
    """Get a resource or list resources in a package."""
    return ResourceManager.get_resource(package, resource_path)


def get_text(package: str, resource_path: str) -> str:
    """Get the text content of a resource file."""
    return ResourceManager.get_text(package, resource_path)


def get_binary(package: str, resource_path: str) -> bytes:
    """Get the binary content of a resource file."""
    return ResourceManager.get_binary(package, resource_path)


def get_path(package: str, resource_path: str) -> Path:
    """Get a filesystem path to a resource."""
    return ResourceManager.get_path(package, resource_path)


def open_text(package: str, resource_path: str, mode: str = "r") -> TextIO:
    """Open a text resource file."""
    return ResourceManager.open_text(package, resource_path, mode)


def open_binary(package: str, resource_path: str, mode: str = "rb") -> BinaryIO:
    """Open a binary resource file."""
    return ResourceManager.open_binary(package, resource_path, mode)


def list_resources(
        package: str, resource_type: Optional[str] = None
) -> List[Dict[str, str]]:
    """List all resources in a package, optionally filtered by type."""
    return ResourceManager.list_resources(package, resource_type)
