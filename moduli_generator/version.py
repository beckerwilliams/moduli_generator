from importlib.metadata import PackageNotFoundError, version


def get_version() -> str:
    """
    Retrieves the version of the `moduli_generator` package.

    This function fetches the installed version of the `moduli_generator` package
    using the `version` function. If the package is not found, it raises a runtime
    error indicating the inability to retrieve the version.

    :raises RuntimeError: If the `moduli_generator` package version cannot be found.
    :return: The version of the `moduli_generator` package.
    :rtype: str
    """
    try:
        return version("moduli_generator")
    except PackageNotFoundError:
        raise RuntimeError("Unable to find moduli_generator package version.")


if __name__ == "__main__":
    print(get_version())
