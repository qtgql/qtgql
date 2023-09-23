from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from tests.ctest_finder import collect_tests, CtestTestCommand
if TYPE_CHECKING:
    from tests.conftest import MiniServer


@pytest.mark.parametrize("ctest_command", collect_tests(), ids=lambda v: v.test_name)
def test_generated_tests(ctest_command: CtestTestCommand, schemas_server: MiniServer):
    os.environ.setdefault("SCHEMAS_SERVER_ADDR", schemas_server.address)
    ctest_command.run()