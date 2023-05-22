import os

from github import Github


def get_env(name: str) -> str:
    return os.environ[name]


g = Github(get_env("BOT_TOKEN"))
qtgql = g.get_repo("qtgql/qtgql")


def get_current_pr():
    return qtgql.get_pull(int(get_env("PR_NUMBER")))
