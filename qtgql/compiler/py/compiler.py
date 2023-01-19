from jinja2 import Environment, PackageLoader, select_autoescape

from qtgql.compiler.objecttype import GqlType, PropertyImpl

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
