from __future__ import annotations

from pathlib import Path
from typing import NamedTuple
from typing import TYPE_CHECKING

import jinja2
from attr import define

from .ghub import get_current_pr
from tests.conftest import PATHS

if TYPE_CHECKING:
    from tests.test_codegen.testcases import QtGqlTestCase

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


class ImplementationStatus(NamedTuple):
    success: bool
    ignored: bool = False

    def __str__(self):
        if self.ignored:
            return ":heavy_minus_sign:"
        if self.success:
            return ":white_check_mark:"
        return "❌"

    def __repr__(self):
        return str(self)

    def __bool__(self):
        return self.success


@define
class TstCaseStatus:
    test: QtGqlTestCase
    implemented: ImplementationStatus
    deserialization: ImplementationStatus
    update: ImplementationStatus
    # TODO: replace with "test in operation variable"?
    # since https://github.com/qtgql/qtgql/pull/253 this is redundant I think.
    garbage_collection: ImplementationStatus


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
    test_cases: list[TstCaseStatus] = []
    for tc in all_test_cases:
        implemented = ImplementationStatus(tc in implemented_testcases)
        tst_content = tc.testcase_file.read_text() if implemented else ""
        test_cases.append(
            TstCaseStatus(
                test=tc,
                implemented=implemented,
                deserialization=ImplementationStatus("test deserialize" in tst_content),
                update=ImplementationStatus(
                    "test update" in tst_content,
                    ignored=not tc.metadata.should_test_updates,
                ),
                garbage_collection=ImplementationStatus(
                    "test in operation variable" in tst_content,
                    ignored=not tc.metadata.should_test_garbage_collection,
                ),
            ),
        )

    return TstCaseImplementationStatusTemplateContext(
        testcases=test_cases,
    )


release_file = PATHS.PROJECT_ROOT / "RELEASE.md"


def get_release_file_context() -> ReleaseContext:
    if not release_file.exists():
        return ReleaseContext(success=False, content="")
    else:
        return ReleaseContext(success=True, content=release_file.read_text())


def render(context: BotCommentContext) -> str:
    return BOT_COMMENT_TEMPLATE.render(context=context)


def create_or_update_bot_comment(content: str) -> None:
    pr = get_current_pr()
    for cm in pr.get_issue_comments():
        if "878ae1db-766f-49c7-a1a8-59f7be1fee8f" in cm.body:
            cm.edit(content)
            return

    pr.create_issue_comment(content)


def comment() -> None:
    context = BotCommentContext(
        release_context=get_release_file_context(),
        testcases_context=get_testcases_context(),
    )
    create_or_update_bot_comment(render(context))
    # fail workflow release file is not valid.
    if not context.release_context.success:
        raise FileNotFoundError("Could not find RELEASE.md or it is in bad format.")


if __name__ == "__main__":
    comment()
