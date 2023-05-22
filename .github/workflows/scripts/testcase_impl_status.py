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
    status: Literal[":heavy_check_mark:"] | Literal["❌"] = "❌"

    def __attrs_post_init__(self):
        if self.implemented:
            self.status = ":heavy_check_mark:"


@define
class TstCaseImplementationStatusTemplateContext:
    testcases: list[TstCaseStatus]

    @property
    def summery(self) -> str:
        implemented_count = len(list(filter(lambda tc: tc.implemented, self.testcases)))
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


def comment_on_pr():
    pr = get_current_pr()
    for comment in pr.get_issue_comments():
        if "878ae1db-766f-49c7-a1a8-59f7be1fee8f" in comment.body:
            comment.edit(tst_case_implementation_status())
            return

    pr.create_issue_comment(tst_case_implementation_status())


if __name__ == "__main__":
    comment_on_pr()
