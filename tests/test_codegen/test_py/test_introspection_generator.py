import typing
import uuid
from datetime import datetime
from types import ModuleType
from typing import Optional

import pytest
import strawberry.utils.str_converters
from attr import define
from qtgql.codegen.introspection import SchemaEvaluator, introspection_query
from qtgql.codegen.py.bases import BaseModel, _BaseQGraphQLObject
from qtgql.codegen.py.config import QtGqlConfig
from qtgql.codegen.py.objecttype import GqlType
from qtgql.codegen.py.scalars import (
    BaseCustomScalar,
    BuiltinScalars,
    DateScalar,
    DateTimeScalar,
    DecimalScalar,
)
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
    tested_type: Optional[GqlType] = None

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

    def compile(self) -> None:
        tmp_mod = ModuleType(uuid.uuid4().hex)
        type_name = self.type_name
        introspection = get_introspection_for(self.schema)
        res = SchemaEvaluator(introspection, config=QtGqlConfig(url=None, output=None))
        generated = res.generate()
        compiled = compile(generated, "schema", "exec")
        exec(compiled, tmp_mod.__dict__)
        self.mod = tmp_mod
        self.tested_type = res._generated_types[type_name]

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

    def __enter__(self):
        self.compile()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...


class ObjectTestCaseMixin:
    def test_property_setter_emits(self, qtbot):
        compiled = self.compiled()
        klass = getattr(compiled.mod, compiled.tested_type.name)
        inst = klass.from_dict(None, self.initialize_dict)
        for field in compiled.tested_type.fields:
            signal = getattr(inst, field.signal_name)
            v = self.initialize_dict[field.name]
            with qtbot.wait_signal(signal):
                if scalar := field.is_custom_scalar:
                    setattr(inst, field.private_name, scalar.from_graphql(None))
                else:
                    setattr(inst, field.private_name, None)
                assert not getattr(inst, field.name)
                if scalar := field.is_custom_scalar:
                    v = scalar.from_graphql(v)
                getattr(inst, field.setter_name)(v)
                if field.is_custom_scalar:
                    assert getattr(inst, field.name) == v.to_qt()
                else:
                    assert getattr(inst, field.name) == v

    def test_from_dict(self, qtbot):
        compiled = self.compiled()
        klass = getattr(compiled.mod, compiled.tested_type.name)
        klass.from_dict(None, self.initialize_dict)


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
]

custom_scalar_testcases = [
    (DateTimeTestCase, DateTimeScalar, "birth"),
    (DateTestCase, DateScalar, "birth"),
    (DecimalTestCase, DecimalScalar, "balance"),
]


@pytest.mark.parametrize("testcase", all_test_cases, ids=lambda x: x.test_name)
def test_init_no_arguments(testcase: QGQLObjectTestCase):
    testcase.compile()
    assert isinstance(testcase.gql_type(None), _BaseQGraphQLObject)


class TestAnnotations:
    @pytest.mark.parametrize("name, scalar", BuiltinScalars.items())
    def test_scalars(self, name, scalar):
        ScalarsTestCase.compile()
        field = ScalarsTestCase.get_field_by_type(scalar)
        assert field, f"field not found for {name}: {scalar}"
        klass = ScalarsTestCase.gql_type
        sf = ScalarsTestCase.strawberry_field_by_name(field.name)
        assert sf
        assert (
            sf.type
            == TypeHinter.from_string(
                getattr(klass, field.setter_name).__annotations__["v"], ns=field.type_map
            ).as_annotation()
        )
        assert (
            sf.type
            == TypeHinter.from_string(
                getattr(klass, field.name).fget.__annotations__["return"], ns=field.type_map
            ).as_annotation()
        )

    def test_custom_scalar(self):
        DateTimeTestCase.compile()
        field = DateTimeTestCase.get_field_by_type(DateTimeScalar)
        assert field, f"field {field} not found"
        klass = DateTimeTestCase.gql_type
        sf = DateTimeTestCase.strawberry_field_by_name(field.name)
        assert sf
        assert sf.type == datetime
        assert field.annotation == f"SCALARS.{DateTimeScalar.__name__}"
        assert getattr(klass, field.setter_name).__annotations__["v"] == field.annotation
        assert getattr(klass, field.name).fget.__annotations__["return"] == field.fget_annotation
        assert (
            TypeHinter.from_string(
                field.fget_annotation, ns={"Optional": typing.Optional}
            ).as_annotation()
            == DateTimeScalar.to_qt.__annotations__["return"]
        )

    def test_list_of(self):
        testcase = ObjectWithListOfObjectTestCase
        testcase.compile()
        field = testcase.get_field_by_name("persons")
        sf = testcase.strawberry_field_by_name(field.name)
        assert field.annotation == sf.type_annotation.annotation
        assert field.fget_annotation == "PersonModel"

    def test_custom_scalar_property_type_is_to_qt_return_annotation(self):
        testcase = DateTimeTestCase
        testcase.compile()
        to_qt = TypeHinter.from_annotations(DateTimeScalar.to_qt.__annotations__["return"])
        assert testcase.get_field_by_name("birth").property_type == to_qt.stringify()


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


class TestDeserializers:
    def test_from_dict_scalars(self, qtbot):
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
        # TODO: remove this when implementing *placeholders*
        with OptionalNestedObjectTestCase as testcase:
            inst = testcase.gql_type.from_dict(None, testcase.initialize_dict)
            assert inst.person is None

    def test_object_with_list_of_object(self):
        with ObjectWithListOfObjectTestCase as testcase:
            inst = testcase.gql_type.from_dict(None, testcase.initialize_dict)
            assert isinstance(inst.persons, BaseModel)
            assert inst.persons._data[0].name

    def test_object_with_interface(self):
        with InterfaceTestCase as testcase:
            inst = testcase.gql_type.from_dict(None, testcase.initialize_dict)
            assert inst.name

    @pytest.mark.parametrize("testcase, scalar, fname", custom_scalar_testcases)
    def test_custom_scalars(
        self, testcase: QGQLObjectTestCase, scalar: BaseCustomScalar, fname: str
    ):
        testcase.compile()
        klass = testcase.gql_type
        initialize_dict = testcase.initialize_dict
        inst = klass.from_dict(None, initialize_dict)
        field = testcase.get_field_by_name(fname)
        assert inst.property(field.name) == scalar.from_graphql(initialize_dict[field.name]).to_qt()


# TODO: TestObjectWithListOfScalar
