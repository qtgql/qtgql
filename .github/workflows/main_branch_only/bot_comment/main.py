import os

try:
    from . import githubref, releasefile, template

except ImportError:
    import githubref
    import releasefile
    import template

if __name__ == "__main__":
    session = githubref.get_github_session(os.getenv("BOT_TOKEN"))
    pr = githubref.get_pr(session, int(os.getenv("BOT_TOKEN")))
    try:
        preview = releasefile.get_release_preview(pr)
    except releasefile.InvalidReleaseFileError as exc:
        raise exc
    content = template.render(
        template.BotCommentContext(preview),
    )
    githubref.create_or_update_bot_comment(pr, content)
