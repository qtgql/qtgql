from typing import Optional

from PySide6.QtCore import QObject


def deserialize_optional_child(data: dict, child, field_name: str) -> Optional[QObject]:
    if found := data.get(field_name, None):
        return child.from_dict(found)
    return None
