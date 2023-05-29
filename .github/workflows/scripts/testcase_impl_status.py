from __future__ import annotations

from pathlib import Path
from typing import Literal
from typing import TYPE_CHECKING

import jinja2
from attr import define

from .ghub import get_current_pr
from tests.conftest import PATHS

if TYPE_CHECKING:
    from tests.test_codegen.testcases import QGQLObjectTestCase

from tests.test_codegen.testcases import all_test_cases, implemented_testcases

template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=jinja2.select_autoescape(),
)

BOT_COMMENT_TEMPLATE = template_env.get_template("bot_comment.jinja.md")


@define
class BotCommentContext:
    testcases_context: TstCaseImplementationStatusTemplateContext
    release_context: ReleaseContext


@define
class TstCaseStatus:
    test: QGQLObjectTestCase
    implemented: bool
    status: Literal[":heavy_check_mark:"] | Literal["❌"] = "❌"

    def __attrs_post_init__(self):
        if self.implemented:
            self.status = ":heavy_check_mark:"


@define
class ReleaseContext:
    success: bool
    content: str


@define
class TstCaseImplementationStatusTemplateContext:
    testcases: list[TstCaseStatus]

    @property
    def summery(self) -> str:
        implemented_count = len(list(filter(lambda tc: tc.implemented, self.testcases)))
        return f"{implemented_count}/{len(self.testcases)} testcases implemented."


def get_testcases_context() -> TstCaseImplementationStatusTemplateContext:
    return TstCaseImplementationStatusTemplateContext(
        testcases=[
            TstCaseStatus(
                test=tc,
                implemented=tc in implemented_testcases,
            )
            for tc in all_test_cases
        ],
    )


release_file = PATHS.PROJECT_ROOT / "RELEASE.md"


def get_release_file_context() -> ReleaseContext:
    if not release_file.exists():
        return ReleaseContext(success=False, content="")
    else:
        return ReleaseContext(success=True, content=release_file.read_text())


def render(context: BotCommentContext) -> str:
    return BOT_COMMENT_TEMPLATE.render(context=context)


def create_or_update_bot_comment() -> None:
    context = BotCommentContext(
        release_context=get_release_file_context(),
        testcases_context=get_testcases_context(),
    )
    content = render(context)
    pr = get_current_pr()
    for comment in pr.get_issue_comments():
        if "878ae1db-766f-49c7-a1a8-59f7be1fee8f" in comment.body:
            comment.edit(content)
            return

    pr.create_issue_comment(content)

    # fail workflow release file is not valid.
    if not context.release_context.success:
        raise FileNotFoundError("Could not find RELEASE.md or it is in bad format.")


if __name__ == "__main__":
    create_or_update_bot_comment()
