from importlib import resources
from pathlib import Path


def get_data_resources():
    """
    Get a list of all code and data resources available from the 'data' package resources.
    Uses importlib.resources to access resources that have been unpacked from a Python wheel.

    Returns:
        list: A list of dictionaries containing the path and type of each resource.
    """
    # Initialize an empty list to store the resources
    resources_list = []

    # Get the data resource from the package using importlib.resources
    data_resource = resources.files("data")

    # Walk through all files in the resource
    def traverse_resource(resource, parent_path=""):
        # Traverse directories recursively
        for item in resource.iterdir():
            # Create path relative to data directory
            rel_path = str(Path(parent_path) / item.name)

            if item.is_file():
                # Determine the file type based on extension
                ext = Path(item.name).suffix
                if ext == ".sh":
                    file_type = "shell script"
                elif ext == ".sql":
                    file_type = "SQL script"
                elif ext == ".py":
                    file_type = "Python script"
                elif ext == ".txt":
                    file_type = "text file"
                elif ext == ".md":
                    file_type = "markdown file"
                elif ext == ".json":
                    file_type = "JSON file"
                elif ext == ".pyc":
                    file_type = "compiled Python file"
                else:
                    file_type = "unknown"

                # Get the full path (this may be different from the filesystem path in wheel)
                with resources.as_file(item) as file_path:
                    full_path = str(file_path)

                resources_list.append(
                    {"path": rel_path, "type": file_type, "full_path": full_path}
                )
            elif item.is_dir():
                # Recursively traverse subdirectories
                traverse_resource(item, rel_path)

    # Start traversal from the root data resource
    traverse_resource(data_resource)

    return resources_list


def list_data_resources():
    """
    Print a list of all code and data resources available from the package resources.
    Uses importlib.resources to access resources that have been unpacked from a Python wheel.
    """
    resources = get_data_resources()

    print("Available resources in package data:")
    print("----------------------------------------")
    for resource in resources:
        print(f"Path: {resource['path']}")
        print(f"Type: {resource['type']}")
        print(f"Full path: {resource['full_path']}")
        print("----------------------------------------")

    return resources


if __name__ == "__main__":
    list_data_resources()
