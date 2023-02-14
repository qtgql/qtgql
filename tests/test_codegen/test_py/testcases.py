import tempfile
import uuid
from contextlib import contextmanager
from functools import cached_property
from pathlib import Path
from textwrap import dedent
from types import ModuleType
from typing import Optional

import attrs
import strawberry.utils
from attr import define
from qtgql.codegen.introspection import SchemaEvaluator
from qtgql.codegen.py.compiler.config import QtGqlConfig
from qtgql.codegen.py.objecttype import GqlTypeDefinition
from qtgql.codegen.py.runtime.bases import _BaseQGraphQLObject
from qtgql.codegen.py.runtime.custom_scalars import (
    BaseCustomScalar,
    DateScalar,
    DateTimeScalar,
    DecimalScalar,
    TimeScalar,
)
from qtgql.codegen.py.runtime.environment import ENV_MAP, QtGqlEnvironment
from qtgql.codegen.py.runtime.queryhandler import BaseQueryHandler
from strawberry import Schema

from tests.conftest import QmlBot, hash_schema
from tests.test_codegen import schemas
from tests.test_codegen.conftest import get_introspection_for


@define(slots=False)
class QGQLObjectTestCase:
    query: str
    schema: Schema
    test_name: str
    type_name: str = "User"
    mod: Optional[ModuleType] = None
    tested_type: Optional[GqlTypeDefinition] = None
    qmlbot: Optional[QmlBot] = None
    config: QtGqlConfig = attrs.field(
        factory=lambda: QtGqlConfig(url=None, output=None, qml_dir=Path(__file__).parent)
    )
    qml_files: dict[str, str] = {}

    def __attrs_post_init__(self):
        if not self.qml_files:
            self.qml_files = {
                "main.qml": dedent(
                    """
            import QtQuick
            import QtGql 1.0 as Gql
            Item{

             Gql.MainQuery{id: backend
              graphql: `query MainQuery %s`
             }
             Text{
                text: backend.data
             }
            }
        """
                    % self.query.replace("query", "")
                )
            }

    @cached_property
    def evaluator(self) -> SchemaEvaluator:
        introspection = get_introspection_for(self.schema)
        return SchemaEvaluator(introspection, config=self.config)

    def get_environment(self) -> QtGqlEnvironment:
        return ENV_MAP[self.config.env_name]

    def load_qml(self, qmlbot: QmlBot):
        self.qmlbot = qmlbot
        qmlbot.loads_many(self.qml_files)
        return self

    @property
    def qml_queryhandler(self) -> BaseQueryHandler:
        return self.qmlbot.find("MainQuery", BaseQueryHandler)

    @property
    def module(self) -> ModuleType:
        assert self.mod
        return self.mod

    @property
    def gql_type(self) -> _BaseQGraphQLObject:
        assert self.tested_type
        return getattr(self.module, self.tested_type.name)

    @property
    def initialize_dict(self) -> dict:
        return self.schema.execute_sync(self.query).data["user"]

    @contextmanager
    def tmp_qml_dir(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            for fname, content in self.qml_files.items():
                with open(tmp_dir / fname, "w") as f:
                    f.write(content)
            yield tmp_dir

    def compile(self, url: Optional[str] = None) -> "QGQLObjectTestCase":
        if url:
            self.config.url = url.replace("graphql", f"{hash_schema(self.schema)}")
        tmp_mod = ModuleType(uuid.uuid4().hex)
        type_name = self.type_name
        with self.tmp_qml_dir() as tmp_dir:
            self.config.qml_dir = tmp_dir
            generated = self.evaluator.dumps()
        compiled = compile(generated, "schema", "exec")
        exec(compiled, tmp_mod.__dict__)
        self.mod = tmp_mod
        self.tested_type = self.evaluator._generated_types[type_name]
        return self

    def get_field_by_type(self, t):
        for field in self.tested_type.fields:
            if field.type.type == t:
                return field

    def get_field_by_name(self, name: str):
        for field in self.tested_type.fields:
            if field.name == name:
                return field

        raise Exception(f"field {name} not found in {self.tested_type}")

    def strawberry_field_by_name(self, field_name: str, klass_name: Optional[str] = None):
        if not klass_name:
            klass_name = self.gql_type.__name__

        stawberry_definition = self.schema.get_type_by_name(klass_name)
        for sf in stawberry_definition.fields:
            if field_name == strawberry.utils.str_converters.to_camel_case(sf.name):
                return sf


ScalarsTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_scalar.schema,
    query="""
        {
          user {
            name
            age
            agePoint
            male
            id
            uuid
          }
        }
        """,
    test_name="ScalarsTestCase",
)
OptionalScalarTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_optional_scalar.schema,
    query="""
    query {
        user{
            name
            age
        }
    }
    """,
    test_name="OptionalScalarTestCase",
)
NestedObjectTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_object.schema,
    query="""
    query {
        user{
            person{
                name
                age
            }
        }
    }
    """,
    test_name="NestedObjectTestCase",
)
OptionalNestedObjectTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_optional_object.schema,
    query="""
    query {
        user{
            person{
                name
                age
            }
        }
    }
    """,
    test_name="OptionalNestedObjectTestCase",
)
ObjectWithListOfObjectTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_list_of_object.schema,
    query="""
    query {
        user{
            persons{
                name
                age
            }
        }
    }
    """,
    test_name="ObjectWithListOfObjectTestCase",
)
InterfaceTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_interface.schema,
    query="""
    query {
        user{
            name
            age
        }
    }
    """,
    test_name="InterfaceTestCase",
)
UnionTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_union.schema,
    query="""
        {
          user {
            whoAmI {
              ... on Frog {
                __typename
                name
                color
              }
              ... on Person {
                __typename
                name
                age
              }
            }
          }
        }
    """,
    test_name="UnionTestCase",
)
ListOfUnionTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_list_of_type_with_union.schema,
    query="""
        {
          userManager {
            users {
              whoAmI {
                ... on Frog {
                  __typename
                  name
                  color
                }
                ... on Person {
                  __typename
                  name
                  age
                }
              }
            }
          }
        }

    """,
    test_name="ListOfUnionTestCase",
)
EnumTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_enum.schema,
    query="""
        {
          user {
            name
            age
            status
          }
        }
        """,
    test_name="EnumTestCase",
)
DateTimeTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_datetime.schema,
    query="""
        {
          user {
            name
            age
            birth
          }
        }
        """,
    test_name="DateTimeTestCase",
)
DecimalTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_decimal.schema,
    query="""
        {
          user {
            name
            age
            balance
          }
        }
    """,
    test_name="DecimalTestCase",
)
DateTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_date.schema,
    query="""
        {
          user {
            name
            age
            birth
          }
        }
        """,
    test_name="DateTestCase",
)
TimeTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_time_scalar.schema,
    query="""
        {
          user {
            name
            age
            whatTimeIsIt
          }
        }
        """,
    test_name="TimeTestCase",
)
ObjectsThatReferenceEachOtherTestCase = QGQLObjectTestCase(
    schema=schemas.object_reference_each_other.schema,
    test_name="ObjectsThatReferenceEachOtherTestCase",
    query="""
    {
      user {
        password
        person {
          name
          age
          user
        }
      }
    }
""",
)


class CountryScalar(BaseCustomScalar[Optional[str]]):
    countrymap = schemas.object_with_user_defined_scalar.countrymap
    GRAPHQL_NAME = "Country"
    DEFAULT_VALUE = "isr"

    @classmethod
    def from_graphql(cls, v: Optional[str] = None) -> "BaseCustomScalar":
        if v:
            return cls(cls.countrymap[v])
        return cls()

    def to_qt(self) -> str:
        return self._value


CustomUserScalarTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_user_defined_scalar.schema,
    config=QtGqlConfig(
        url=None, output=None, custom_scalars={CountryScalar.GRAPHQL_NAME: CountryScalar}
    ),
    test_name="CustomUserScalarTestCase",
    query="""
            {
          user {
            name
            age
            country
          }
        }
    """,
)
all_test_cases = [
    ScalarsTestCase,
    DateTimeTestCase,
    DateTestCase,
    DecimalTestCase,
    OptionalScalarTestCase,
    NestedObjectTestCase,
    OptionalNestedObjectTestCase,
    ObjectWithListOfObjectTestCase,
    InterfaceTestCase,
    UnionTestCase,
    ListOfUnionTestCase,
    TimeTestCase,
    EnumTestCase,
    CustomUserScalarTestCase,
    ObjectsThatReferenceEachOtherTestCase,
]
custom_scalar_testcases = [
    (DateTimeTestCase, DateTimeScalar, "birth"),
    (DateTestCase, DateScalar, "birth"),
    (DecimalTestCase, DecimalScalar, "balance"),
    (TimeTestCase, TimeScalar, "whatTimeIsIt"),
    (CustomUserScalarTestCase, CountryScalar, "country"),
]
