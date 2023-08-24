from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import jinja2

if TYPE_CHECKING:
    from .releasefile import ReleasePreview


template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=jinja2.select_autoescape(),
)

BOT_COMMENT_TEMPLATE = template_env.get_template("bot_comment.jinja.md")


@dataclass
class BotCommentContext:
    release_preview: ReleasePreview


def render(context: BotCommentContext) -> str:
    return BOT_COMMENT_TEMPLATE.render(context=context)
