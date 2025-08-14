import importlib.util

import sys


def is_import_resource(name: str):
    if name in sys.modules:
        print(f"{name!r} already in sys.modules")
        return True
    elif (spec := importlib.util.find_spec(name)) is not None:
        # If you chose to perform the actual import ...
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        print(f"{name!r} has been imported")
        return True
    else:
        print(f"can't find the {name!r} module")

    return False


if __name__ == "__main__":
    if is_import_resource("data"):
        print(f"sys.modules: {sys.modules}")
        print(f'data: {importlib.util.find_spec("data")!r}')
