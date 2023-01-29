import uuid
from types import ModuleType
from typing import Optional

import pytest
from attr import define
from qtgql.codegen.introspection import SchemaEvaluator, introspection_query
from qtgql.codegen.py.bases import BaseModel, _BaseQGraphQLObject
from qtgql.codegen.py.config import QtGqlConfig
from qtgql.codegen.py.objecttype import GqlType
from qtgql.codegen.py.scalars import DateTimeScalar
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


class ObjectTestCaseMixin:
    def test_has_correct_annotations(self):
        compiled = self.compiled()
        klass = getattr(compiled.mod, compiled.tested_type.name)
        for field in compiled.tested_type.fields:
            annotation = field.annotation
            assert klass.__init__.__annotations__[field.name] == annotation
            assert getattr(klass, field.setter_name).__annotations__["v"] == annotation
            assert getattr(klass, field.name).fget.__annotations__["return"] == field.property_type

    def test_init(self):
        compiled = self.compiled()
        klass = getattr(compiled.mod, compiled.tested_type.name)
        klass()

    def test_property_getter(self):
        compiled = self.compiled()

        klass = getattr(compiled.mod, compiled.tested_type.name)
        inst = klass.from_dict(None, self.initialize_dict)
        for field in compiled.tested_type.fields:
            v = getattr(inst, field.name)
            if scalar := field.is_custom_scalar:
                assert scalar.from_graphql(self.initialize_dict[field.name]).to_qt() == v
            else:
                assert v == self.initialize_dict[field.name]

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

all_test_cases = [
    ScalarsTestCase,
    DateTimeTestCase,
    OptionalScalarTestCase,
    NestedObjectTestCase,
    OptionalNestedObjectTestCase,
    ObjectWithListOfObjectTestCase,
    InterfaceTestCase,
    UnionTestCase,
    ListOfUnionTestCase,
]


@pytest.mark.parametrize("testcase", all_test_cases, ids=lambda x: x.test_name)
def test_init_no_arguments(testcase: QGQLObjectTestCase):
    testcase.compile()
    assert isinstance(testcase.gql_type(None), _BaseQGraphQLObject)


class TestObjectWithDateTimeScalar(ObjectTestCaseMixin):
    schema = schemas.object_with_datetime.schema
    initialize_dict = schema.execute_sync(
        query="""
        {
          user {
            name
            age
            birth
          }
        }
        """
    ).data["user"]

    def test_from_dict(self, qtbot):
        compiled = self.compiled()
        klass = getattr(compiled.mod, compiled.tested_type.name)
        inst = klass.from_dict(None, self.initialize_dict)
        assert inst.birth == DateTimeScalar.from_graphql(self.initialize_dict["birth"]).to_qt()


class TestObjectWithObject(ObjectTestCaseMixin):
    schema = schemas.object_with_object.schema
    initialize_dict = schema.execute_sync(
        query="""
        query {
            user{
                person{
                    name
                    age
                }
            }
        }
        """
    ).data["user"]

    def test_from_dict(self, qtbot):
        compiled = self.compiled()
        klass = getattr(compiled.mod, compiled.tested_type.name)
        inst = klass.from_dict(None, self.initialize_dict)
        assert inst.person.name == "Patrick"
        assert inst.person.age == 100


class TestObjectWithOptionalObjectField(ObjectTestCaseMixin):
    schema = schemas.object_with_optional_object.schema
    initialize_dict = schema.execute_sync(
        query="""
        query {
            user{
                person{
                    name
                    age
                }
            }
        }
        """
    ).data["user"]

    def test_from_dict(self, qtbot):
        compiled = self.compiled()
        klass = getattr(compiled.mod, compiled.tested_type.name)
        inst = klass.from_dict(None, self.initialize_dict)
        assert inst.person is None


# TODO: TestObjectWithListOfScalar
class TestObjectWithListOfObject(ObjectTestCaseMixin):
    schema = schemas.object_with_list_of_object.schema
    initialize_dict = schema.execute_sync(
        query="""
        query {
            user{
                persons{
                    name
                    age
                }
            }
        }
        """
    ).data["user"]

    def test_from_dict(self, qtbot):
        compiled = self.compiled()
        klass = getattr(compiled.mod, compiled.tested_type.name)
        inst: _BaseQGraphQLObject = klass.from_dict(None, self.initialize_dict)
        assert isinstance(inst.persons, BaseModel)


# TODO: test for optional list.


class TestObjectWithInterface(ObjectTestCaseMixin):
    schema = schemas.object_with_interface.schema
    initialize_dict = schema.execute_sync(
        query="""
        query {
            user{
                name
                age
            }
        }
        """
    ).data["user"]
