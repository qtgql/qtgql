Release type: patch

This release adds support for operation errors hooks.
i.e
```python
from qtgql.codegen.py.runtime.queryhandler import BaseOperationHandler


class Foo(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        operation: BaseOperationHandler
        operation.error.connect(self.on_error)

    @slot
    def on_error(self, err: dict) -> None:
        print(err)
```
