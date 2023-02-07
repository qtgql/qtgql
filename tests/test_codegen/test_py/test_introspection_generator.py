import typing
import uuid
from types import ModuleType
from typing import Optional

import attrs
import pytest
import strawberry.utils.str_converters
from attrs import define
from qtgql.codegen.introspection import SchemaEvaluator, introspection_query
from qtgql.codegen.py.bases import BaseModel, _BaseQGraphQLObject
from qtgql.codegen.py.config import QtGqlConfig
from qtgql.codegen.py.custom_scalars import DateScalar, DateTimeScalar, DecimalScalar, TimeScalar
from qtgql.codegen.py.objecttype import GqlTypeDefinition
from qtgql.codegen.py.scalars import BaseCustomScalar, BuiltinScalar, BuiltinScalars
from qtgql.typingref import TypeHinter
from strawberry import Schema

from tests.mini_gql_server import schema
from tests.test_codegen import schemas
from tests.test_codegen.conftest import get_introspection_for


@pytest.fixture
def introspected():
    return schema.execute_sync(introspection_query)


@define
class QGQLObjectTestCase:
    query: str
    schema: Schema
    test_name: str
    type_name: str = "User"
    mod: Optional[ModuleType] = None
    tested_type: Optional[GqlTypeDefinition] = None
    config: QtGqlConfig = attrs.field(factory=lambda: QtGqlConfig(url=None, output=None))

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

    def compile(self) -> "QGQLObjectTestCase":
        tmp_mod = ModuleType(uuid.uuid4().hex)
        type_name = self.type_name
        introspection = get_introspection_for(self.schema)
        res = SchemaEvaluator(introspection, config=self.config)
        generated = res.generate()
        compiled = compile(generated, "schema", "exec")
        exec(compiled, tmp_mod.__dict__)
        self.mod = tmp_mod
        self.tested_type = res._generated_types[type_name]
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


# custom scalars
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
]

custom_scalar_testcases = [
    (DateTimeTestCase, DateTimeScalar, "birth"),
    (DateTestCase, DateScalar, "birth"),
    (DecimalTestCase, DecimalScalar, "balance"),
    (TimeTestCase, TimeScalar, "whatTimeIsIt"),
    (CustomUserScalarTestCase, CountryScalar, "country"),
]


@pytest.mark.parametrize("testcase", all_test_cases, ids=lambda x: x.test_name)
def test_init_no_arguments(testcase: QGQLObjectTestCase):
    testcase.compile()
    assert isinstance(testcase.gql_type(None), _BaseQGraphQLObject)


class TestAnnotations:
    @pytest.mark.parametrize("scalar", BuiltinScalars.scalars, ids=lambda v: v.graphql_name)
    def test_scalars(self, scalar: BuiltinScalar):
        ScalarsTestCase.compile()
        field = ScalarsTestCase.get_field_by_type(scalar)
        assert field, f"field not found for {scalar.graphql_name}: {scalar}"
        klass = ScalarsTestCase.gql_type
        assert (
            scalar.tp
            == TypeHinter.from_string(
                getattr(klass, field.setter_name).__annotations__["v"], ns=field.type_map
            ).as_annotation()
        )
        assert (
            scalar.tp
            == TypeHinter.from_string(
                getattr(klass, field.name).fget.__annotations__["return"], ns=field.type_map
            ).as_annotation()
        )

    @pytest.mark.parametrize("testcase, scalar, fname", custom_scalar_testcases)
    def test_custom_scalars(
        self, testcase: QGQLObjectTestCase, scalar: typing.Type[BaseCustomScalar], fname
    ):
        testcase.compile()
        field = testcase.get_field_by_type(scalar)
        assert field, f"field {field} not found"
        klass = testcase.gql_type
        assert field.annotation == f"SCALARS.{scalar.__name__}"
        assert getattr(klass, field.setter_name).__annotations__["v"] == field.annotation
        assert getattr(klass, field.name).fget.__annotations__["return"] == field.fget_annotation
        assert (
            TypeHinter.from_string(
                field.fget_annotation, ns={"Optional": typing.Optional}
            ).as_annotation()
            == scalar.to_qt.__annotations__["return"]
        )

    def test_list_of(self):
        testcase = ObjectWithListOfObjectTestCase
        testcase.compile()
        field = testcase.get_field_by_name("persons")
        assert field.annotation == field.type.is_model.model_name
        assert field.fget_annotation == field.type.is_model.model_name

    def test_custom_scalar_property_type_is_to_qt_return_annotation(self):
        testcase = DateTimeTestCase
        testcase.compile()
        to_qt = TypeHinter.from_annotations(DateTimeScalar.to_qt.__annotations__["return"])
        assert testcase.get_field_by_name("birth").property_type == to_qt.stringify()

    def test_enums(self):
        testcase = EnumTestCase.compile()
        enum_field = testcase.get_field_by_name("status")
        assert enum_field.property_type == "int"
        assert enum_field.fget_annotation == "int"
        assert enum_field.annotation == "Status"


class TestPropertyGetter:
    def default_test(self, testcase: QGQLObjectTestCase, field_name: str):
        testcase.compile()
        klass = testcase.gql_type
        initialize_dict = testcase.initialize_dict
        inst = klass.from_dict(None, initialize_dict)
        field = testcase.get_field_by_name(field_name)
        assert inst.property(field.name)

    def test_scalars(self, qtbot):
        testcase = ScalarsTestCase
        testcase.compile()
        klass = testcase.gql_type
        initialize_dict = testcase.initialize_dict
        inst = klass.from_dict(None, initialize_dict)
        for field in testcase.tested_type.fields:
            v = inst.property(field.name)
            assert v == initialize_dict[field.name]

    def test_datetime_scalar(self, qtbot):
        self.default_test(DateTimeTestCase, "birth")

    def test_nested_object(self, qtbot):
        self.default_test(NestedObjectTestCase, "person")

    def test_list_of(self, qtbot):
        self.default_test(ObjectWithListOfObjectTestCase, "persons")

    def test_union(self, qtbot):
        self.default_test(UnionTestCase, "whoAmI")

    def test_enum(self):
        testcase = EnumTestCase.compile()
        inst = testcase.gql_type.from_dict(None, data=testcase.initialize_dict)
        f = testcase.get_field_by_name("status")
        assert inst.property(f.name) == testcase.module.Status.Connected.value


class TestDeserializers:
    def test_scalars(self, qtbot):
        testcase = ScalarsTestCase
        testcase.compile()
        klass = testcase.gql_type
        initialize_dict = testcase.initialize_dict
        inst = klass.from_dict(None, initialize_dict)
        for field in testcase.tested_type.fields:
            v = getattr(inst, field.private_name)
            assert v == initialize_dict[field.name]

    def test_nested_object_from_dict(self, qtbot):
        testcase = NestedObjectTestCase
        testcase.compile()
        klass = testcase.gql_type
        inst = klass.from_dict(None, testcase.initialize_dict)
        assert inst.person.name == "Patrick"
        assert inst.person.age == 100

    def test_nested_optional_object(self):
        testcase = OptionalNestedObjectTestCase.compile()
        inst = testcase.gql_type.from_dict(None, testcase.initialize_dict)
        assert inst.person

    def test_object_with_list_of_object(self):
        testcase = ObjectWithListOfObjectTestCase.compile()
        inst = testcase.gql_type.from_dict(None, testcase.initialize_dict)
        assert isinstance(inst.persons, BaseModel)
        assert inst.persons._data[0].name

    def test_object_with_interface(self):
        testcase = InterfaceTestCase.compile()
        inst = testcase.gql_type.from_dict(None, testcase.initialize_dict)
        assert inst.name

    @pytest.mark.parametrize("testcase, scalar, fname", custom_scalar_testcases)
    def test_custom_scalars(
        self, testcase: QGQLObjectTestCase, scalar: BaseCustomScalar, fname: str
    ):
        testcase.compile()
        klass = testcase.gql_type
        initialize_dict = testcase.initialize_dict
        initialize_dict["country"] = "isr"
        inst = klass.from_dict(None, initialize_dict)
        field = testcase.get_field_by_name(fname)
        assert inst.property(field.name) == scalar.from_graphql(initialize_dict[field.name]).to_qt()

    def test_enum(self):
        testcase = EnumTestCase.compile()
        inst = testcase.gql_type.from_dict(None, data=testcase.initialize_dict)
        f = testcase.get_field_by_name("status")
        assert getattr(inst, f.private_name) == testcase.module.Status.Connected


class TestDefaultConstructor:
    @pytest.mark.parametrize("scalar", BuiltinScalars.scalars, ids=lambda v: v.graphql_name)
    def test_builtin_scalars(self, scalar: BuiltinScalar):
        testcase = ScalarsTestCase
        testcase.compile()
        klass = testcase.gql_type
        inst = klass()
        f = testcase.get_field_by_type(scalar)
        assert getattr(inst, f.private_name) == scalar.default_value

    def test_nested_object_from_dict(self, qtbot):
        testcase = NestedObjectTestCase.compile()
        klass = testcase.gql_type
        inst = klass()
        assert inst.person.name == BuiltinScalars.by_python_type(str).default_value
        assert inst.person.age == BuiltinScalars.by_python_type(int).default_value

    def test_object_with_list_of_object(self):
        testcase = ObjectWithListOfObjectTestCase.compile()
        inst = testcase.gql_type()
        assert isinstance(inst.persons, BaseModel)
        # by default there is no need for initializing delegates.
        assert len(inst.persons._data) == 0

    @pytest.mark.parametrize("testcase, scalar, fname", custom_scalar_testcases)
    def test_custom_scalars(
        self, testcase: QGQLObjectTestCase, scalar: BaseCustomScalar, fname: str
    ):
        testcase.compile()
        inst = testcase.gql_type()
        field = testcase.get_field_by_name(fname)
        assert getattr(inst, field.private_name).to_qt() == scalar().to_qt()

    def test_enum(self):
        testcase = EnumTestCase.compile()
        inst = testcase.gql_type()
        f = testcase.get_field_by_name("status")
        assert (
            getattr(inst, f.private_name)
            == testcase.module.Status(1)
            == testcase.module.Status.Connected
        )

    def test_union(self):
        testcase = UnionTestCase.compile()
        testcase.gql_type()
