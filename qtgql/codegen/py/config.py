from attrs import define

from qtgql.codegen.introspection import SchemaEvaluator


@define
class QtGQLApp:
    url: str

    def fetch(self) -> None:
        SchemaEvaluator


default_config = QtGQLApp(url="localhost:8000/graphql")
