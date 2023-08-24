import argparse

from github import Github
from github.PullRequest import PullRequest


def create_or_update_bot_comment(pr: PullRequest, content: str) -> None:
    for cm in pr.get_issue_comments():
        if "878ae1db-766f-49c7-a1a8-59f7be1fee8f" in cm.body:
            cm.edit(content)
            return

    pr.create_issue_comment(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("BOT_TOKEN")
    parser.add_argument("PR_NUMBER")
    parser.add_argument("BOT_COMMENT_CONTENT")
    context = parser.parse_args()
    g = Github(context.BOT_TOKEN)
    qtgql = g.get_repo("qtgql/qtgql")
    create_or_update_bot_comment(qtgql.get_pull(context.PR_NUMBER), context.BOT_COMMENT_CONTENT)
