import importlib.resources


__all__ = ['installer']


def installer():
    """
    Executes a bash script to perform installation using a predefined path.

        This function locates a script within a specified directory structure and
        invokes it using the `bash` command.

    Returns:
        None: None
    """
    try:
        # Access the module from the installers directory
        files = importlib.resources.files('data.bash_scripts')
        module = files / 'install_gm.sh'

        if module.is_file():
            print(f'Installer Script: {module}\n')
            print(module.read_text())
        else:
            print("Error: get_github_installer.py not found in package installers")

    except Exception as err:
        print(f"Error importing installer script: {err}")


if __name__ == "__main__":
    installer()
