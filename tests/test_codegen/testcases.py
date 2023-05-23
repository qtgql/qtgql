from __future__ import annotations

import os
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

import jinja2
from attr import define
from typer.testing import CliRunner

from qtgqlcodegen.cli import app
from qtgqlcodegen.config import QtGqlConfig
from qtgqlcodegen.introspection import SchemaEvaluator
from qtgqlcodegen.runtime.custom_scalars import CustomScalarDefinition
from qtgqlcodegen.runtime.custom_scalars import DateTimeScalarDefinition
from tests.conftest import hash_schema
from tests.test_codegen import schemas

if TYPE_CHECKING:
    from strawberry import Schema


BaseQueryHandler = None  # TODO: remove this when done migrating, this is just for readability.

GENERATED_TESTS_DIR = Path(__file__).parent / "generated_test_projects"
if not GENERATED_TESTS_DIR.exists:
    GENERATED_TESTS_DIR.mkdir()
template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates_for_tests"),
    autoescape=jinja2.select_autoescape(),
    variable_start_string="👉",  # jinja uses {{ variable }}, using 👉 variable 👈 because C++ uses curly brackets.
    variable_end_string="👈",
)

TST_CONFIG_TEMPLATE = template_env.get_template("configtemplate.jinja.py")
TST_CATCH2_TEMPLATE = template_env.get_template("testcase.jinja.cpp")
CLI_RUNNER = CliRunner()
TST_CMAKE = (Path(__file__).parent / "CMakeLists.txt").resolve(True)


@define
class TstTemplateContext:
    config: QtGqlConfig
    url_suffix: str
    test_name: str


@define(slots=False, kw_only=True)
class QGQLObjectTestCase:
    query: str
    schema: Schema
    test_name: str
    type_name: str = "User"
    custom_scalars: dict = {}
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

    @cached_property
    def test_dir(self) -> Path:
        ret = GENERATED_TESTS_DIR / self.test_name
        if not ret.exists():
            ret.mkdir()
        return ret

    @cached_property
    def graphql_dir(self) -> Path:
        ret = self.test_dir / "graphql"
        if not ret.exists():
            ret.mkdir()
        return ret

    @cached_property
    def config_dir(self) -> Path:
        return self.test_dir / "qtgqlconfig.py"

    @cached_property
    def schema_dir(self) -> Path:
        return self.graphql_dir / "schema.graphql"

    @cached_property
    def operations_dir(self) -> Path:
        return self.graphql_dir / "operations.graphql"

    @cached_property
    def config(self) -> QtGqlConfig:
        return QtGqlConfig(
            graphql_dir=self.graphql_dir,
            env_name="default_env",
            custom_scalars=self.custom_scalars,
        )

    def generate(self) -> None:
        self.config.env_name = self.test_name
        template_context = TstTemplateContext(
            config=self.config,
            url_suffix=str(hash_schema(self.schema)),
            test_name=self.test_name,
        )
        self.schema_dir.write_text(self.schema.as_str())
        self.operations_dir.write_text(self.query)
        self.config_dir.write_text(TST_CONFIG_TEMPLATE.render(context=template_context))
        generated_test_case = self.test_dir / f"test_{self.test_name.lower()}.cpp"
        if not generated_test_case.exists():
            generated_test_case.write_text(TST_CATCH2_TEMPLATE.render(context=template_context))

        cwd = Path.cwd()
        os.chdir(self.config_dir.parent)
        CLI_RUNNER.invoke(app, "gen", catch_exceptions=False)
        os.chdir(cwd)
        prev = TST_CMAKE.read_text()
        link_line = "target_link_libraries(${TESTS_TARGET} PRIVATE generated::%s)" % (
            self.config.env_name
        )
        if link_line not in prev:
            TST_CMAKE.write_text(prev + f"\n {link_line}")


ScalarsTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_scalar.schema,
    query="""
        query MainQuery {
          constUser {
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
NoIdOnQueryTestCase = QGQLObjectTestCase(  # should append id automatically.
    schema=schemas.object_with_scalar.schema,
    query="""
    query MainQuery {
          user {
            name
            age
            agePoint
            male
          }
        }""",
    test_name="NoIdOnQueryTestCase",
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
TimeScalarTestCase = QGQLObjectTestCase(
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
    test_name="TimeScalarTestCase",
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


CountryScalar = CustomScalarDefinition(
    type_name="CountryScalar",
    graphql_name="Country",
    property_type="QString",
    deserialized_type="QString",
    include_path="NOT IMPLEMENTED",
)


CustomUserScalarTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_user_defined_scalar.schema,
    custom_scalars={CountryScalar.graphql_name: CountryScalar},
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
    query MainQuery ($ret: TypesEnum! = Dog) {
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

ListOfInterfaceTestcase = QGQLObjectTestCase(
    schema=schemas.list_of_interface.schema,
    query=InterfaceFieldTestCase.query,
    test_name="ListOfInterfaceTestcase",
)
all_test_cases = [
    ScalarsTestCase,
    NoIdOnQueryTestCase,
    DateTimeTestCase,
    DateTestCase,
    TimeScalarTestCase,
    DecimalTestCase,
    OptionalScalarTestCase,
    NestedObjectTestCase,
    OptionalNestedObjectTestCase,
    ObjectWithListOfObjectTestCase,
    InterfaceTestCase,
    UnionTestCase,
    ListOfObjectWithUnionTestCase,
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
    (DateTimeTestCase, DateTimeScalarDefinition, "birth"),
    (CustomUserScalarTestCase, CountryScalar, "country"),
]

implemented_testcases = [
    ScalarsTestCase,
    NoIdOnQueryTestCase,
    DateTimeTestCase,
    DecimalTestCase,
    DateTestCase,
    TimeScalarTestCase,
]


def generate_testcases() -> None:
    for testcase in implemented_testcases:
        testcase.generate()


if __name__ == "__main__":
    generate_testcases()
