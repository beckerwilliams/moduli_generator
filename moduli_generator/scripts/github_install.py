from subprocess import run

from _github_installer_sh import installer_script


def installer():
    """
    Executes a bash script to perform installation using a predefined path.

    This function locates a script within a specified directory structure and
    invokes it using the `bash` command.

    :return: None
    :rtype: None
    """
    print(f'Installer Script: {installer_script()}\n')
    script = installer_script()
    run(['bash', '-c', script])


if __name__ == "__main__":
    installer()
