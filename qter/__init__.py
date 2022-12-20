import os

from .slot import slot

if not os.environ.get("QT_API", None):  # pragma: no cover
    os.environ["QT_API"] = "pyside6"


__all__ = ["itemsystem", "slot", "autoproperty"]
