from __future__ import annotations

from pathlib import Path
from typing import Literal
from typing import TYPE_CHECKING

import jinja2
from attr import define

from .ghub import get_current_pr

if TYPE_CHECKING:
    from tests.test_codegen.testcases import QGQLObjectTestCase

from tests.test_codegen.testcases import all_test_cases, implemented_testcases

template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=jinja2.select_autoescape(),
)

TESTCASE_IMPLEMENTATION_STATUS = template_env.get_template("implementation_status.jinja.md")


@define
class TstCaseStatus:
    test: QGQLObjectTestCase
    implemented: bool
    status: Literal["✅"] | Literal["❌"] = "❌"

    def __attrs_post_init__(self):
        if self.implemented:
            self.status = "✅"


@define
class TstCaseImplementationStatusTemplateContext:
    testcases: list[TstCaseStatus]

    @property
    def summery(self) -> str:
        implemented_count = len(list(filter(lambda tc: tc.status == "✅", self.testcases)))
        return f"{implemented_count}/{len(self.testcases)} testcases implemented."


def tst_case_implementation_status() -> str:
    context = TstCaseImplementationStatusTemplateContext(
        testcases=[
            TstCaseStatus(
                test=tc,
                implemented=tc in implemented_testcases,
            )
            for tc in all_test_cases
        ],
    )
    return template_env.get_template("implementation_status.jinja.md").render(context=context)


if __name__ == "__main__":
    pr = get_current_pr()
    pr.create_comment(
        position=0,
        body=tst_case_implementation_status(),
    )
