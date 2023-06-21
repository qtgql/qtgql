from __future__ import annotations

import os
import re
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

import attrs
import graphql
import jinja2
from attr import define
from qtgqlcodegen.cli import app
from qtgqlcodegen.config import QtGqlConfig
from qtgqlcodegen.generator import SchemaGenerator
from qtgqlcodegen.types import CustomScalarDefinition, DateTimeScalarDefinition
from tests.conftest import hash_schema
from tests.test_codegen import schemas
from typer.testing import CliRunner

if TYPE_CHECKING:
    from strawberry import Schema

GENERATED_TESTS_DIR = Path(__file__).parent / "generated_test_projects"
if not GENERATED_TESTS_DIR.exists:
    GENERATED_TESTS_DIR.mkdir()
template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates_for_tests"),
    autoescape=jinja2.select_autoescape(),
    variable_start_string="👉",  # jinja uses {{ variable }}, using 👉 variable 👈 because C++ uses curly brackets.
    variable_end_string="👈",
)

TST_CMAKE_TEMPLATE = template_env.get_template("CMakeLists.jinja.txt")  # only build what you test.
TST_CONFIG_TEMPLATE = template_env.get_template("configtemplate.jinja.py")
TST_CATCH2_TEMPLATE = template_env.get_template("testcase.jinja.cpp")
CLI_RUNNER = CliRunner()


@define
class TstTemplateContext:
    config: QtGqlConfig
    url_suffix: str
    test_name: str


@define
class BoolWithReason:
    v: bool
    reason: str

    @classmethod
    def false(cls, reason: str) -> BoolWithReason:
        return cls(False, reason)

    @classmethod
    def true(cls, reason: str) -> BoolWithReason:
        return cls(True, reason)

    def __bool__(self):
        return self.v


class TestCaseMetadata(NamedTuple):
    should_test_updates: BoolWithReason = BoolWithReason.true("")
    should_test_garbage_collection: BoolWithReason = BoolWithReason.true("")


@define(slots=False, kw_only=True)
class QtGqlTestCase:
    operations: str
    schema: Schema
    test_name: str
    custom_scalars: dict = {}
    qml_file: str = ""
    needs_debug: bool = False
    metadata: TestCaseMetadata = attrs.Factory(TestCaseMetadata)

    @cached_property
    def evaluator(self) -> SchemaGenerator:
        return SchemaGenerator(
            config=self.config,
            schema=graphql.build_schema(
                (self.graphql_dir / "schema.graphql").resolve(True).read_text(),
            ),
        )

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

    @property
    def generated_dir(self):
        return self.config.generated_dir

    @cached_property
    def config_file(self) -> Path:
        return self.test_dir / "qtgqlconfig.py"

    @cached_property
    def schema_file(self) -> Path:
        return self.graphql_dir / "schema.graphql"

    @cached_property
    def operations_file(self) -> Path:
        return self.graphql_dir / "operations.graphql"

    @cached_property
    def testcase_file(self) -> Path:
        return self.test_dir / f"test_{self.test_name.lower()}.cpp"

    @cached_property
    def config(self) -> QtGqlConfig:
        return QtGqlConfig(
            graphql_dir=self.graphql_dir,
            env_name="default_env",
            custom_scalars=self.custom_scalars,
            debug=self.needs_debug,
        )

    @cached_property
    def url_suffix(self):
        return str(hash_schema(self.schema))

    def generate(self) -> None:
        self.config.env_name = self.test_name
        template_context = TstTemplateContext(
            config=self.config,
            url_suffix=self.url_suffix,
            test_name=self.test_name,
        )
        self.schema_file.write_text(self.schema.as_str())
        self.operations_file.write_text(self.operations)
        self.config_file.write_text(TST_CONFIG_TEMPLATE.render(context=template_context))
        if not self.testcase_file.exists():
            self.testcase_file.write_text(TST_CATCH2_TEMPLATE.render(context=template_context))
        else:
            updated = re.sub(
                'get_server_address\\("([0-9])*"\\)',
                f'get_server_address("{self.url_suffix}")',
                self.testcase_file.read_text(),
            )
            self.testcase_file.write_text(updated)

        cwd = Path.cwd()
        os.chdir(self.config_file.parent)
        CLI_RUNNER.invoke(app, "gen", catch_exceptions=False)
        os.chdir(cwd)


ScalarsTestCase = QtGqlTestCase(
    schema=schemas.object_with_scalar.schema,
    operations="""
        query MainQuery {
          constUser {
            id
            name
            age
            agePoint
            male
            id
            uuid
            voidField
          }
        }
        query UserWithSameIDAndDifferentFieldsQuery {
          constUserWithModifiedFields {
            age
            agePoint
            id
            male
            name
            uuid
          }
        }
        """,
    test_name="ScalarsTestCase",
)

OptionalScalarsTestCase = QtGqlTestCase(
    schema=schemas.object_with_optional_scalar.schema,
    operations="""
    query MainQuery($returnNone: Boolean! = false) {
      user(retNone: $returnNone) {
        name
        age
        agePoint
        uuid
        birth
      }
    }

    mutation ChangeName($userId: ID!, $newName: String!){
      modifyName(userId: $userId, newName: $newName) {
        uuid
        name
        id
        birth
        agePoint
        age
      }
    }
    """,
    test_name="OptionalScalarsTestCase",
)
NoIdOnQueryTestCase = QtGqlTestCase(
    # should append id to types that implements Node automatically.
    schema=schemas.object_with_scalar.schema,
    operations="""
    query MainQuery {
          user {
            name
            age
            agePoint
            male
          }
        }""",
    test_name="NoIdOnQueryTestCase",
    metadata=TestCaseMetadata(
        BoolWithReason.false("nothing special here in that context"),
        BoolWithReason.false("nothing special here in that context"),
    ),
)

CUSTOM_SCALARS_DOESNT_CACHE = BoolWithReason.false("custom scalars doesnt use cache")
DateTimeTestCase = QtGqlTestCase(
    schema=schemas.object_with_datetime.schema,
    operations="""
       query MainQuery {
          user {
            name
            age
            birth
          }
        }
mutation ChangeUserBirth($new_birth: DateTime!, $nodeId: ID!) {
  changeBirth(newBirth: $new_birth, nodeId: $nodeId) {
    age
    id
    birth
    name
  }
}
        """,
    test_name="DateTimeTestCase",
    metadata=TestCaseMetadata(
        should_test_garbage_collection=CUSTOM_SCALARS_DOESNT_CACHE,
    ),
)

DecimalTestCase = QtGqlTestCase(
    schema=schemas.object_with_decimal.schema,
    operations="""
       query MainQuery {
          user {
            name
            age
            balance
          }
        }
        mutation UpdateBalance ($newBalance: Decimal!, $id: ID!){
          changeBalance(newBalance: $newBalance, nodeId: $id) {
            balance
          }
        }
    """,
    test_name="DecimalTestCase",
    metadata=TestCaseMetadata(
        should_test_garbage_collection=CUSTOM_SCALARS_DOESNT_CACHE,
    ),
)
DateTestCase = QtGqlTestCase(
    schema=schemas.object_with_date.schema,
    operations="""
       query MainQuery {
          user {
            name
            age
            birth
          }
        }
        mutation ChangeUserBirth($new_birth: Date!, $nodeId: ID!) {
          changeBirth(newBirth: $new_birth, nodeId: $nodeId) {
            birth
          }
        }
        """,
    test_name="DateTestCase",
    metadata=TestCaseMetadata(
        should_test_garbage_collection=CUSTOM_SCALARS_DOESNT_CACHE,
    ),
)
TimeScalarTestCase = QtGqlTestCase(
    schema=schemas.object_with_time_scalar.schema,
    operations="""
      query MainQuery {
          user {
            name
            age
            lunchTime
          }
        }
        mutation UpdateLunchTime ($newTime: Time!, $id: ID!) {
          changeLunchTime(newTime: $newTime, nodeId: $id) {
            lunchTime
          }
        }
        """,
    test_name="TimeScalarTestCase",
    metadata=TestCaseMetadata(
        should_test_garbage_collection=CUSTOM_SCALARS_DOESNT_CACHE,
    ),
)

OperationVariablesTestcase = QtGqlTestCase(
    schema=schemas.operation_variables.schema,
    operations="""
  query MainQuery($connectedVar: Boolean!) {
    user {
      id
      name
      friend(connectedArg: $connectedVar) {
        id
        name
      }
    }
  }

  mutation ChangeFriendName($connected: Boolean!, $new_name: String!) {
  changeFriendName(connected: $connected, newName: $new_name) {
    friend(connectedArg: $connected) {
      name
    }
  }
}
        """,
    test_name="OperationVariablesTestcase",
)

OperationErrorTestCase = QtGqlTestCase(
    schema=schemas.operation_error.schema,
    operations="""
    query MainQuery {
        user{
            name
            age
        }
    }
    """,
    test_name="OperationErrorTestCase",
)

NestedObjectTestCase = QtGqlTestCase(
    schema=schemas.object_with_object.schema,
    operations="""
    query MainQuery {
        user{
            person{
                name
                age
            }
        }
    }

    mutation UpdateUserName($nodeId: ID!, $newName: String!) {
      changeName(newName: $newName, nodeId: $nodeId) {
        person {
          name
        }
      }
    }
    """,
    test_name="NestedObjectTestCase",
)
OptionalNestedObjectTestCase = QtGqlTestCase(
    schema=schemas.object_with_optional_object.schema,
    operations="""
    query MainQuery($return_null: Boolean!) {
      user(returnNull: $return_null) {
        person {
          name
          age
        }
      }
    }

    mutation UpdateUserName($nodeId: ID!, $newName: String!) {
      changeName(newName: $newName, nodeId: $nodeId) {
        person {
          name
        }
      }
    }
    """,
    test_name="OptionalNestedObjectTestCase",
)
ObjectWithListOfObjectTestCase = QtGqlTestCase(
    schema=schemas.object_with_list_of_object.schema,
    operations="""
    query MainQuery {
        user{
            friends{
                name
                age
            }
        }
    }
    mutation AddFriend ($userId: ID!, $name: String!) {
      addFriend(userId: $userId, name: $name)
    }
    """,
    test_name="ObjectWithListOfObjectTestCase",
    needs_debug=True,
)

RootListOfTestCase = QtGqlTestCase(
    schema=schemas.root_list_of_object.schema,
    operations="""
    query MainQuery {
        users{
            name
            age
        }
    }
    """,
    test_name="RootListOfTestCase",
)

InterfaceTestCase = QtGqlTestCase(
    schema=schemas.object_with_interface.schema,
    operations="""
    query MainQuery {
        user{
            name
            age
        }
    }
    """,
    test_name="InterfaceTestCase",
)
UnionTestCase = QtGqlTestCase(
    schema=schemas.object_with_union.schema,
    operations="""
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
ListOfObjectWithUnionTestCase = QtGqlTestCase(
    schema=schemas.object_with_list_of_type_with_union.schema,
    operations="""
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
EnumTestCase = QtGqlTestCase(
    schema=schemas.object_with_enum.schema,
    operations="""
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
RootEnumTestCase = QtGqlTestCase(
    schema=schemas.root_enum_schema.schema,
    operations="""
        query MainQuery {
          status
        }
        """,
    test_name="RootEnumTestCase",
)

ObjectsThatReferenceEachOtherTestCase = QtGqlTestCase(
    schema=schemas.object_reference_each_other.schema,
    test_name="ObjectsThatReferenceEachOtherTestCase",
    operations="""
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
    name="CountryScalar",
    graphql_name="Country",
    to_qt_type="QString",
    deserialized_type="QString",
    include_path="NOT IMPLEMENTED",
)

CustomUserScalarTestCase = QtGqlTestCase(
    schema=schemas.object_with_user_defined_scalar.schema,
    custom_scalars={CountryScalar.graphql_name: CountryScalar},
    test_name="CustomUserScalarTestCase",
    operations="""
     query MainQuery {
          user {
            name
            age
            country
          }
        }
    """,
)

TypeWithNoIDTestCase = QtGqlTestCase(
    schema=schemas.type_with_no_id.schema,
    operations="""query MainQuery {users{name}}""",
    test_name="TypeWithNoIDTestCase",
)

RootTypeNoIDTestCase = QtGqlTestCase(
    schema=schemas.root_type_no_id.schema,
    operations="""
    query MainQuery {
        user{
            name
            age
        }
    }""",
    test_name="RootTypeNoIDTestCase",
)

TypeWithNullAbleIDTestCase = QtGqlTestCase(
    schema=schemas.type_with_nullable_id.schema,
    operations="""query MainQuery {users{name}}""",
    test_name="TypeWithNullAbleIDTestCase",
)

ListOfUnionTestCase = QtGqlTestCase(
    schema=schemas.list_of_union.schema,
    operations="""
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

InputTypeOperationVariableTestCase = QtGqlTestCase(
    schema=schemas.input_type.schema,
    operations="""
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
    test_name="InputTypeOperationVariableTestCase",
)

OptionalInputTestCase = QtGqlTestCase(
    schema=schemas.optional_input_schema.schema,
    operations="""
    query HelloOrEchoQuery($echo: String){
      echoOrHello(echo: $echo)
    }
    """,
    test_name="OptionalInputTestCase",
)

CustomScalarInputTestCase = QtGqlTestCase(
    schema=schemas.custom_scalar_input_schema.schema,
    operations="""
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

MutationOperationTestCase = QtGqlTestCase(
    schema=schemas.mutation_schema.schema,
    operations="""        query MainQuery {
          user {
            id
            name
            age
            agePoint
            male
            uuid
          }
        }""",
    test_name="MutationOperationTestCase",
)

SubscriptionTestCase = QtGqlTestCase(
    schema=schemas.subscription_schema.schema,
    operations="""
    subscription CountSubscription ($target: Int = 5){
        count(target: $target)
}
    """,
    test_name="SubscriptionTestCase",
)

InterfaceFieldTestCase = QtGqlTestCase(
    schema=schemas.interface_field.schema,
    operations="""
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

ListOfInterfaceTestcase = QtGqlTestCase(
    schema=schemas.list_of_interface.schema,
    operations=InterfaceFieldTestCase.operations,
    test_name="ListOfInterfaceTestcase",
)
all_test_cases = [
    ScalarsTestCase,
    OptionalScalarsTestCase,
    NoIdOnQueryTestCase,
    DateTimeTestCase,
    DateTestCase,
    TimeScalarTestCase,
    DecimalTestCase,
    NestedObjectTestCase,
    OptionalNestedObjectTestCase,
    ObjectWithListOfObjectTestCase,
    InputTypeOperationVariableTestCase,
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
    OptionalScalarsTestCase,
    NestedObjectTestCase,
    OptionalNestedObjectTestCase,
    ObjectWithListOfObjectTestCase,
    EnumTestCase,
    InterfaceTestCase,
]


def generate_testcases(*testcases: QtGqlTestCase) -> None:
    (GENERATED_TESTS_DIR / "CMakeLists.txt").write_text(
        TST_CMAKE_TEMPLATE.render(context={"testcases": testcases}),
    )
    for tc in testcases:
        tc.generate()


if __name__ == "__main__":
    generate_testcases(DateTestCase)
