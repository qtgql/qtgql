from github import Github
from github.PullRequest import PullRequest



def get_github_session(token: str) -> Github:
    return Github(token)


def get_pr(g: Github, num: int) -> PullRequest:
    qtgql = g.get_repo("qtgql/qtgql")
    return qtgql.get_pull(num)


def create_or_update_bot_comment(pr: PullRequest, content: str) -> None:
    for cm in pr.get_issue_comments():
        if "878ae1db-766f-49c7-a1a8-59f7be1fee8f" in cm.body:
            cm.edit(content)
            return

    pr.create_issue_comment(content)

