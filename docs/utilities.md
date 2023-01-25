## Utilities
general helpers for ease of development.

### Auto-property

::: autoproperty.define_properties

 Example:
 ```python
 from qtgql.autoproperty import define_properties

 @define_properties
 class Apple:
    color: str
    size: int

 apple = Apple(color="red", size=92)
 apple_as_qt: Apple = apple.properties
 assert apple_as_qt.color == apple.color
 apple.color = "green"
 assert apple_as_qt.color == "green"
 ```
