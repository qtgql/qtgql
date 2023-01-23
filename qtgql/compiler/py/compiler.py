from jinja2 import Environment, PackageLoader, select_autoescape

from qtgql.compiler.objecttype import GqlType

env = Environment(loader=PackageLoader("qtgql.compiler.py"), autoescape=select_autoescape())

SchemaTemplate = env.get_template("schema.jinja.py")


def py_template(types: list[GqlType]) -> str:
    return SchemaTemplate.render(types=types)
