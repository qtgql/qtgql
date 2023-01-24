import importlib
import inspect
import sys
import uuid

from qtgql.codegen.py.config import QtGqlConfig


def test_fetch_schema(mini_server, tmp_path):
    file = tmp_path / "generate.py"
    assert not file.exists()
    config = QtGqlConfig(url=mini_server.address.replace("ws", "http"), output=file)
    config.fetch()
    with open(file) as f:
        assert f.read(), "module was empty"
    mod_id = uuid.uuid4().hex
    spec = importlib.util.spec_from_file_location(mod_id, file)
    foo = importlib.util.module_from_spec(spec)
    sys.modules[mod_id] = foo

    spec.loader.exec_module(foo)
    assert inspect.isclass(
        importlib.import_module(mod_id).Query
    )  # Query should always be generated
