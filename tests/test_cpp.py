from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from tests.ctest_finder import CtestTestCommand, collect_tests

if TYPE_CHECKING:
    from tests.conftest import MiniServer


@pytest.mark.parametrize("ctest_command", collect_tests(), ids=lambda v: v.test_name)
def test_generated_tests(ctest_command: CtestTestCommand, schemas_server: MiniServer):
    os.environ.setdefault("SCHEMAS_SERVER_ADDR", schemas_server.address.replace("graphql", ""))
    ctest_command.run()
    if log_file := ctest_command.failed_log:
        if "All tests passed" not in log_file:
            pytest.fail(  # noqa: PT016
                reason=f"\n {'-'*8} Test {ctest_command.test_name} Failed {'-'*8} \n {log_file}",
            )
