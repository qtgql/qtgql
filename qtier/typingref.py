from typing import Union, get_args, get_origin


def is_optional(field) -> bool:
    return get_origin(field) is Union and type(None) in get_args(field)
