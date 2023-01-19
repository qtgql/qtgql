from typing import Generic, Optional, Type, TypeVar

from attrs import define, field
from jinja2 import Environment, PackageLoader, select_autoescape

T = TypeVar("T")


@define
class PropertyImpl(Generic[T]):
    name: str
    type: Type[T] = field(converter=lambda v: v.__name__)
    default: T = None

    @property
    def setter_name(self) -> str:
        return self.name + "_setter"

    @property
    def signal_name(self) -> str:
        return self.name + "Changed"

    @property
    def private_name(self) -> str:
        return "_" + self.name


@define
class GqlType:
    name: str
    properties: list[PropertyImpl]
    docstring: Optional[str] = ""


env = Environment(loader=PackageLoader("qtgql.compiler.py"), autoescape=select_autoescape())

SchemaTemplate = env.get_template("schema.jinja.py")
if __name__ == "__main__":  # pragma: no cover

    class A:
        """Adoc."""

        def a(self):
            ...

    p = SchemaTemplate.render(
        types=[
            GqlType(
                docstring="awesome explanation", name="MyType", properties=[PropertyImpl("a", int)]
            )
        ]
    )
    print(p)
