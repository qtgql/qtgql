from typing import Optional

import pytest
from qtgql.codegen.py.runtime.queryhandler import BaseOperationHandler, QmlOperationConsumerABC

from tests.conftest import IS_WINDOWS
from tests.test_codegen.test_py.testcases import (
    OperationErrorTestCase,
    OperationVariableTestCase,
    ScalarsTestCase,
)


def test_data_fetched(qmlbot, schemas_server):
    with ScalarsTestCase.compile(schemas_server.address) as testcase:
        testcase.load_qml(qmlbot)
        operation_consumer = qmlbot.qquickiew.findChildren(QmlOperationConsumerABC)[0]
        with qmlbot.bot.wait_signal(operation_consumer.handlerDataChanged):
            ...
        assert isinstance(operation_consumer.property("handlerData"), testcase.gql_type)


def test_disposes_operation_when_component_is_deleted(qmlbot, schemas_server):
    with ScalarsTestCase.compile(schemas_server.address) as testcase:
        testcase.load_qml(qmlbot)
        handler = testcase.get_qml_query_handler(qmlbot)
        with qmlbot.bot.wait_signal(handler.completedChanged):
            ...
        assert handler._data
        qmlbot.cleanup()
        qmlbot.bot.wait_until(lambda: not handler._data)


def test_on_completed_emits(qmlbot, schemas_server):
    with ScalarsTestCase.compile(schemas_server.address) as testcase:
        testcase.load_qml(qmlbot)
        handler = testcase.get_qml_query_handler(qmlbot)
        with qmlbot.bot.wait_signal(handler.completedChanged):
            ...
        assert handler._data
        assert handler.completed


def test_operation_on_flight_prop(qtbot, schemas_server):
    with ScalarsTestCase.compile(schemas_server.address) as testcase:
        handler = testcase.query_handler
        assert not handler.operationOnFlight
        handler.fetch()
        assert handler.property("operationOnFlight")
        assert handler.operationOnFlight
        qtbot.wait_until(lambda: handler.property("completed"))
        assert not handler.operationOnFlight


@pytest.mark.skipif(IS_WINDOWS, reason="This would kill the server on windows for some reason.")
def test_operation_on_flight_prop_on_error(qtbot, schemas_server):
    with OperationErrorTestCase.compile(schemas_server.address) as testcase:
        handler = testcase.query_handler
        assert not handler.operationOnFlight
        handler.fetch()
        assert handler.property("operationOnFlight")
        assert handler.operationOnFlight
        qtbot.wait_until(lambda: handler.property("completed"))
        assert not handler.operationOnFlight


@pytest.mark.skipif(IS_WINDOWS, reason="This would kill the server on windows for some reason.")
def test_emits_error_on_error(qtbot, schemas_server):
    with OperationErrorTestCase.compile(schemas_server.address) as testcase:
        handler = testcase.query_handler
        error: Optional[dict] = None

        def catch_error(err):
            nonlocal error
            error = err

        handler.error.connect(catch_error)
        handler.fetch()
        qtbot.wait_until(lambda: bool(error))
        assert error


class TestQQuickOperationConsumerComp:
    def test_has_handler_prop(self, qmlbot, schemas_server):
        with ScalarsTestCase.compile(schemas_server.address) as testcase:
            testcase.load_qml(qmlbot)
            operation_wraper = qmlbot.qquickiew.findChildren(QmlOperationConsumerABC)[0]
            assert isinstance(operation_wraper.property("handler"), BaseOperationHandler)
            qmlbot.cleanup()

    def test_mutation_handler(self, qmlbot, schemas_server):
        with OperationVariableTestCase.compile(schemas_server.address) as testcase:
            qml = """
            import generated.%s as ENV
            import QtQuick

            ENV.ConsumeCreatePost{
            id: operation_consumer
            }

            """ % (
                testcase.config.env_name
            )
            testcase.qml_file = qml
            testcase.load_qml(qmlbot)
            operation_consumer = qmlbot.qquickiew.findChildren(QmlOperationConsumerABC)[0]
            input_klass = testcase.get_attr("CreatePostInput")
            inp = input_klass(testcase.parent_obj, "Nir", "Nir")
            operation_consumer.handler.setVariables(inp)
            operation_consumer.handler.commit()
            qmlbot.bot.wait_until(lambda: operation_consumer.handler.completed)
            assert operation_consumer.handlerData.header == "Nir"
