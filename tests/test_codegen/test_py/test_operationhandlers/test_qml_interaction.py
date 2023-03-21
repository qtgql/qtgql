from qtgql.codegen.py.runtime.queryhandler import BaseOperationHandler, QmlOperationConsumerABC

from tests.test_codegen.test_py.testcases import OperationVariableTestCase, ScalarsTestCase


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


class TestQQuickOperationComp:
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
