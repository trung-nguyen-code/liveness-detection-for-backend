from typing import Union


def safe_to_int(value: Union[str, int], default=0) -> int:
    try:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value)
        if value is None:
            return default
    except ValueError:
        return default
