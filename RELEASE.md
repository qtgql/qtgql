Release type: patch

This release fixes a bug that inner model class would get overridden
by ItemBase metaclass.
```python
class StatusIndicator(ItemBaseType):
    class Model(GenericModel):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
```
