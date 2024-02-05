import sys
from typing import Union


def get_arg(name: str, default: Union[str, int, None] = None):
    if name not in sys.argv:
        # Explicitly check against None, otherwise 0 is treated as missing argument
        if default is None:
            print(f"Argument '{name}' is required to run the script")
            exit(1)
        else:
            return default

    index = sys.argv.index(name)
    return sys.argv[index+1]