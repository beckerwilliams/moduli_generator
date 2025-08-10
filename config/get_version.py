def get_version():
    """Get package version from metadata or alternative sources."""
    try:
        from importlib.metadata import version

        return version("moduli_generator")
    except ImportError:
        # Fallback for Python < 3.8
        try:
            from importlib_metadata import version

            return version("moduli_generator")
        except ImportError:
            pass
    except Exception:
        pass

    # Try to load from pyproject.toml
    try:
        from moduli_generator.resources import get_text
        import toml

        pyproject = toml.loads(get_text("moduli_generator", "pyproject.toml"))
        return pyproject.get("tool", {}).get("poetry", {}).get("version", "0.0.0-dev")
    except Exception:
        return "0.0.0-dev"


if __name__ == "__main__":
    print(f"Version: {get_version()}")
