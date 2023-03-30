import contextlib
import importlib
import sys
import tempfile
from functools import cached_property
from pathlib import Path
from textwrap import dedent
from types import ModuleType
from typing import TYPE_CHECKING, Optional, Type

import attrs
import strawberry.utils
from attr import define
from PySide6.QtCore import QObject
from qtgql.codegen.introspection import SchemaEvaluator
from qtgql.codegen.py.compiler.config import QtGqlConfig
from qtgql.codegen.py.objecttype import QtGqlObjectTypeDefinition
from qtgql.codegen.py.runtime.custom_scalars import (
    BaseCustomScalar,
    DateScalar,
    DateTimeScalar,
    DecimalScalar,
    TimeScalar,
)
from qtgql.codegen.py.runtime.environment import _ENV_MAP, QtGqlEnvironment, set_gql_env
from qtgql.codegen.py.runtime.queryhandler import BaseMutationHandler, BaseQueryHandler
from qtgql.gqltransport.client import GqlWsTransportClient
from strawberry import Schema

from tests.conftest import QmlBot, fake, hash_schema
from tests.test_codegen import schemas

if TYPE_CHECKING:
    from PySide6 import QtCore
    from qtgql.codegen.py.runtime.bases import _BaseQGraphQLObject


@define(slots=False, kw_only=True)
class QGQLObjectTestCase:
    query: str
    schema: Schema
    test_name: str
    type_name: str = "User"
    qmlbot: Optional[QmlBot] = None
    config: QtGqlConfig = attrs.field(
        factory=lambda: QtGqlConfig(graphql_dir=Path(__file__).parent, env_name="TestEnv"),
    )
    query_operationName: str = "MainQuery"
    first_field: str = "user"
    qml_file: str = ""

    @cached_property
    def evaluator(self) -> SchemaEvaluator:
        return SchemaEvaluator(config=self.config)

    @property
    def initialize_dict(self) -> dict:
        res = self.schema.execute_sync(
            self.evaluator._query_handlers[self.query_operationName].query,
        )
        if res.errors:
            raise Exception("graphql operations failed", res.errors)
        else:
            return res.data

    @contextlib.contextmanager
    def compile(self, url: Optional[str] = "") -> "CompiledTestCase":
        url = url.replace("graphql", f"{hash_schema(self.schema)}")
        client = GqlWsTransportClient(url=url)
        self.config.env_name = env_name = fake.pystr()
        env = QtGqlEnvironment(client=client, name=env_name)
        set_gql_env(env)

        with tempfile.TemporaryDirectory() as raw_tmp_dir:
            tmp_dir = Path(raw_tmp_dir).resolve()
            self.config.graphql_dir = tmp_dir
            (tmp_dir / "__init__.py").resolve().write_text("import os")
            (tmp_dir / "operations.graphql").resolve().write_text(self.query)
            (tmp_dir / "schema.graphql").resolve().write_text(str(self.schema))
            gen_module_name = fake.pystr()
            generated_dir = tmp_dir / gen_module_name
            generated_dir.mkdir()
            generated = self.evaluator.dumps()
            (generated_dir / "__init__.py").resolve().write_text("import os")
            schema_dir = (generated_dir / "objecttypes.py").resolve()
            schema_dir.write_text(generated["objecttypes"])
            handlers_dir = (generated_dir / "handlers.py").resolve()
            handlers_dir.write_text(generated["handlers"])
            sys.path.append(str(tmp_dir))
            try:
                schema_mod = importlib.import_module(f"{gen_module_name}.objecttypes")
            except BaseException as e:
                raise RuntimeError(generated["objecttypes"]) from e

            try:
                handler_mod = importlib.import_module(f"{gen_module_name}.handlers")
            except BaseException as e:
                raise RuntimeError(generated["handlers"]) from e
        testcase = CompiledTestCase(
            evaluator=self.evaluator,
            objecttypes_mod=schema_mod,
            handlers_mod=handler_mod,
            config=self.config,
            query=self.query,
            schema=self.schema,
            qml_file=self.qml_file,
            query_operationName=self.query_operationName,
            first_field=self.first_field,
            test_name=self.test_name,
            tested_type=self.evaluator._objecttypes_def_map.get(self.type_name, None),
        )
        yield testcase
        testcase.cleanup()
        client.deleteLater()
        _ENV_MAP.pop(env_name)


@define
class CompiledTestCase(QGQLObjectTestCase):
    objecttypes_mod: ModuleType
    handlers_mod: ModuleType
    config: QtGqlConfig
    tested_type: QtGqlObjectTypeDefinition
    evaluator: SchemaEvaluator
    parent_obj: QObject = attrs.field(factory=QObject)

    def __attrs_post_init__(self):
        self.query = dedent(self.query)
        if not self.qml_file:
            self.qml_file = dedent(
                """
                    import QtQuick
                    import generated.{} as Env

                     Env.Consume{}{{
                        objectName: "rootObject"
                        autofetch: true
                        anchors.fill: parent;
                        Text{{
                            text: `is autofetch? ${{autofetch}}`
                        }}

                    }}
                """.format(
                    self.config.env_name,
                    self.query_operationName,
                ),
            )

    def cleanup(self) -> None:
        self.parent_obj.deleteLater()

    @property
    def module(self) -> ModuleType:
        return self.objecttypes_mod

    @property
    def gql_type(self) -> Type["_BaseQGraphQLObject"]:
        assert self.tested_type
        return getattr(self.objecttypes_mod, self.tested_type.name)

    @cached_property
    def query_handler(self) -> "BaseQueryHandler":
        return getattr(self.handlers_mod, self.query_operationName)(self.parent_obj)

    def get_attr(self, attr: str):
        return getattr(self.handlers_mod, attr, None)

    def get_query_handler(self, operation_name: str) -> BaseQueryHandler:
        return self.get_attr(operation_name)(self.parent_obj)

    def get_mutation_handler(self, operation_name: str) -> BaseMutationHandler:
        return self.get_attr(operation_name)(self.parent_obj)

    def get_signals(self) -> dict[str, "QtCore.Signal"]:
        return {
            field.signal_name: getattr(self.query_handler.data, field.signal_name)
            for field in self.tested_type.fields
        }

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

    def load_qml(self, qmlbot: QmlBot):
        qmlbot.loads(self.qml_file)
        return self

    def get_qml_query_handler(self, bot: QmlBot) -> BaseQueryHandler:
        return bot.qquickiew.findChildren(BaseQueryHandler)[0]


ScalarsTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_scalar.schema,
    query="""
        query MainQuery {
          user {
            id
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
    query MainQuery {
        user{
            name
            age
        }
    }
    """,
    test_name="OptionalScalarTestCase",
)

OperationErrorTestCase = QGQLObjectTestCase(
    schema=schemas.operation_error.schema,
    query="""
    query MainQuery {
        user{
            name
            age
        }
    }
    """,
    test_name="OperationErrorTestCase",
)

NestedObjectTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_object.schema,
    query="""
    query MainQuery {
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
    query MainQuery {
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
    query MainQuery {
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

RootListOfTestCase = QGQLObjectTestCase(
    schema=schemas.root_list_of_object.schema,
    query="""
    query MainQuery {
        users{
            name
            age
        }
    }
    """,
    test_name="RootListOfTestCase",
)

InterfaceTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_interface.schema,
    query="""
    query MainQuery {
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
        query MainQuery {
          user (choice: FROG){
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
ListOfObjectWithUnionTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_list_of_type_with_union.schema,
    query="""
        query MainQuery {
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
        query MainQuery {
          user {
            name
            age
            status
          }
        }
        """,
    test_name="EnumTestCase",
)
RootEnumTestCase = QGQLObjectTestCase(
    schema=schemas.root_enum_schema.schema,
    query="""
        query MainQuery {
          status
        }
        """,
    test_name="RootEnumTestCase",
)

DateTimeTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_datetime.schema,
    query="""
       query MainQuery {
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
       query MainQuery {
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
       query MainQuery {
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
      query MainQuery {
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
  query MainQuery {
      user {
        password
        person {
          name
          age
        }
      }
    }
""",
)


class CountryScalar(BaseCustomScalar[Optional[str], str]):
    countrymap = schemas.object_with_user_defined_scalar.countrymap
    GRAPHQL_NAME = "Country"
    DEFAULT_VALUE = "isr"

    @classmethod
    def deserialize(cls, v=None) -> "BaseCustomScalar":
        if v:
            return cls(cls.countrymap[v])
        return cls()

    def to_qt(self) -> str:
        return self._value


CustomUserScalarTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_user_defined_scalar.schema,
    config=QtGqlConfig(
        graphql_dir=None,
        custom_scalars={CountryScalar.GRAPHQL_NAME: CountryScalar},
    ),
    test_name="CustomUserScalarTestCase",
    query="""
     query MainQuery {
          user {
            name
            age
            country
          }
        }
    """,
)

TypeWithNoIDTestCase = QGQLObjectTestCase(
    schema=schemas.type_with_no_id.schema,
    query="""query MainQuery {users{name}}""",
    test_name="TypeWithNoIDTestCase",
)

RootTypeNoIDTestCase = QGQLObjectTestCase(
    schema=schemas.root_type_no_id.schema,
    query="""
    query MainQuery {
        user{
            name
            age
        }
    }""",
    test_name="RootTypeNoIDTestCase",
)

TypeWithNullAbleIDTestCase = QGQLObjectTestCase(
    schema=schemas.type_with_nullable_id.schema,
    query="""query MainQuery {users{name}}""",
    test_name="TypeWithNullAbleIDTestCase",
)

ListOfUnionTestCase = QGQLObjectTestCase(
    schema=schemas.list_of_union.schema,
    query="""
       query MainQuery {
          usersAndFrogs {
            ... on User {
              name
              age
            }
            ... on Frog {
              name
              color
            }
          }
        }""",
    test_name="ListOfUnionTestCase",
)


OperationVariableTestCase = QGQLObjectTestCase(
    schema=schemas.variables_schema.schema,
    query="""
    query MainQuery {
      post {
        header
        comments {
          content
          commenter
        }
        createdAt
      }
    }

    mutation changePostHeaderMutation($postID: ID!, $newHeader: String!) {
      changePostHeader(newHeader: $newHeader, postId: $postID) {
        header
      }
    }

    mutation CreatePost($input: CreatePostInput!) {
      createPost(input: $input) {
        content
        header
        createdAt
        id
        comments {
          id
          commenter
          content
        }
      }
    }

    query GetPostById($id: ID!) {
      getPostById(id: $id) {
        content
        header
        createdAt
        id
        comments {
          id
          commenter
          content
        }
      }
    }
    query EnumNameQuery ($enumVar: SampleEnum! ){
      getEnumName(enumInput: $enumVar)
    }
    """,
    test_name="OperationVariableTestCase",
    type_name="Post",
)
OptionalInputTestCase = QGQLObjectTestCase(
    schema=schemas.optional_input_schema.schema,
    query="""
    query HelloOrEchoQuery($echo: String){
      echoOrHello(echo: $echo)
    }
    """,
    test_name="OptionalInputTestCase",
)

CustomScalarInputTestCase = QGQLObjectTestCase(
    schema=schemas.custom_scalar_input_schema.schema,
    query="""
        query ArgsQuery($decimal: Decimal!, $dt: DateTime!, $time: Time!, $date: Date!) {
          echoCustomScalar(decimal: $decimal, dt: $dt, time_: $time, date_: $date) {
            date_
            decimal
            dt
            time_
          }
        }

        query CustomScalarsInputObj($input: SupportedCustomScalarsInput!) {
          echoCustomScalarInputObj(input: $input) {
            dt
            decimal
            date_
            time_
          }
        }
    """,
    test_name="CustomScalarInputTestCase",
)

MutationOperationTestCase = QGQLObjectTestCase(
    schema=schemas.mutation_schema.schema,
    query="""        query MainQuery {
          user {
            id
            name
            age
            agePoint
            male
            id
            uuid
          }
        }""",
    test_name="MutationOperationTestCase",
)


SubscriptionTestCase = QGQLObjectTestCase(
    schema=schemas.subscription_schema.schema,
    query="""
    subscription CountSubscription ($target: Int = 5){
        count(target: $target)
}
    """,
    test_name="SubscriptionTestCase",
)


InterfaceFieldTestCase = QGQLObjectTestCase(
    schema=schemas.interface_field.schema,
    query="""
    query MainQuery ($ret: TypesEnum!) {
      node(ret: $ret) {
        id
        __typename
        ... on HasNameAgeInterface {
          name
          age
        }
        ... on User {
          password
        }
        ... on Dog {
          barks
        }
      }
    }
    """,
    test_name="InterfaceFieldTestCase",
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
    ListOfObjectWithUnionTestCase,
    TimeTestCase,
    EnumTestCase,
    CustomUserScalarTestCase,
    ObjectsThatReferenceEachOtherTestCase,
    RootListOfTestCase,
    TypeWithNoIDTestCase,
    TypeWithNullAbleIDTestCase,
    ListOfUnionTestCase,
    RootTypeNoIDTestCase,
]
custom_scalar_testcases = [
    (DateTimeTestCase, DateTimeScalar, "birth"),
    (DateTestCase, DateScalar, "birth"),
    (DecimalTestCase, DecimalScalar, "balance"),
    (TimeTestCase, TimeScalar, "whatTimeIsIt"),
    (CustomUserScalarTestCase, CountryScalar, "country"),
]
