from qtgql.codegen.py.runtime.queryhandler import BaseQueryHandler, UseQueryABC

from tests.test_codegen.test_py.testcases import ScalarsTestCase


def test_is_singleton(pseudo_environment):
    class Foo(BaseQueryHandler):
        ENV_NAME = pseudo_environment.name
        ...

    assert Foo() is Foo()

    class Bar(BaseQueryHandler):
        ENV_NAME = pseudo_environment.name
        ...

    assert Bar() is not Foo()


def test_fetched_when_first_use_query_consumes_the_operation(qtbot, schemas_server):
    testcase = ScalarsTestCase.compile()
    handler: BaseQueryHandler = getattr(testcase.handlers_mod, testcase.query_operationName)()
    assert not handler._operation_on_the_fly
    use_query: UseQueryABC = testcase.handlers_mod.UseQuery()
    use_query.set_operationName(testcase.query_operationName)
    assert handler._operation_on_the_fly
