import datetime
import os
import re
import subprocess
import textwrap
from dataclasses import dataclass
from pathlib import Path

import httpx
import tomllib

from . import githubref
from .releasefile import ReleasePreview, parse_release_file
from .utils import PATHS

REPO_SLUG = "qtgql/qtgql"


def git(*args: str):
    return subprocess.run(["git", *args]).check_returncode()


@dataclass
class PRContributor:
    pr_number: int
    pr_author_username: str
    pr_author_fullname: str


def get_last_commit_contributor(token: str) -> PRContributor:
    org, repo = REPO_SLUG.split("/")
    current_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()
    response = httpx.post(
        "https://api.github.com/graphql",
        json={
            "query": """query Contributor(
                $owner: String!
                $name: String!
                $commit: GitObjectID!
            ) {
                repository(owner: $owner, name: $name) {
                    object(oid: $commit) {
                        __typename
                        ... on Commit {
                            associatedPullRequests(first: 1) {
                                nodes {
                                    number
                                    author {
                                        __typename
                                        login
                                        ... on User {
                                            name
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }""",
            "variables": {"owner": org, "name": repo, "commit": current_commit},
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )

    payload = response.json()
    commit = payload["data"]["repository"]["object"]

    if not commit:
        raise Exception("No commit found")

    prs = commit["associatedPullRequests"]["nodes"]

    if not prs:
        raise Exception("No PR was created for the last commit")

    pr = prs[0]
    pr_number = pr["number"]
    pr_author_username = pr["author"]["login"]
    pr_author_fullname = pr["author"].get("name", "")
    return PRContributor(
        pr_number=pr_number,
        pr_author_fullname=pr_author_fullname,
        pr_author_username=pr_author_username,
    )


def update_cmake_version(version: str) -> None:
    assert PATHS.ROOT_CMAKE.exists()
    cmake_ver_pattern = r"set\(QTGQL_VERSION\s+([\d.]+)\)"

    def ver_repl(match: re.Match) -> str:
        return match.group(0).replace(match.group(1), version)

    replaced = re.sub(cmake_ver_pattern, ver_repl, PATHS.ROOT_CMAKE.read_text(), count=1)
    PATHS.ROOT_CMAKE.write_text(replaced, "UTF-8")


INIT_FILE = PATHS.QTGQLCODEGEN_ROOT / "__init__.py"
CONANFILE = PATHS.PROJECT_ROOT / "conanfile.py"


def update_python_versions(version: str) -> None:
    assert INIT_FILE.exists()
    assert CONANFILE.exists()
    pattern = r'__version__: str = "([\d.]+)"'

    def replace__version__(file: Path) -> None:
        def ver_repl(match: re.Match) -> str:
            return match.group(0).replace(match.group(1), version)

        replaced = re.sub(pattern, ver_repl, file.read_text(), count=1)
        file.write_text(replaced, "UTF-8")
        git(["add", str(file)])

    replace__version__(INIT_FILE)
    replace__version__(CONANFILE)


def get_contributor_details(conributor: PRContributor) -> str:
    return (
        f"Contributed by [{conributor.pr_author_fullname or conributor.pr_author_username}]"
        f"(https://github.com/{conributor.pr_author_username}) via [PR #{conributor.pr_number}]"
        f"(https://github.com/{REPO_SLUG}/pull/{conributor.pr_number}/)"
    )


def get_current_version() -> str:
    pyproject = tomllib.loads(PATHS.PYPROJECT_TOML.read_text(encoding="utf-8"))
    return pyproject["tool"]["poetry"]["version"]


def bump_version(bump_string: str) -> None:
    subprocess.run(["poetry", "version", bump_string])


def pprint_release_change_log(release_preview: ReleasePreview, contrib_details: str) -> str:
    current_changes = "".join(release_preview.changelog.splitlines()[1:])  # remove release type

    def is_first_or_last_line_empty(s: str) -> bool:
        return s.startswith("\n") or s.endswith("\n")

    while is_first_or_last_line_empty(current_changes):
        current_changes = current_changes.strip("\n")
    return f"{current_changes}\n\n{contrib_details}"


def update_change_log(current_changes: str, version: str) -> None:
    main_header = "CHANGELOG\n=========\n"

    this_header = textwrap.dedent(
        f"""{version} - {datetime.datetime.now(tz=datetime.timezone.utc).date().isoformat()}\n--------------------\n""",
    )
    previous = PATHS.CHANGELOG.read_text(encoding="utf-8").strip(main_header)
    PATHS.CHANGELOG.write_text(
        textwrap.dedent(
            f"{main_header}" f"{this_header}" f"{current_changes}\n\n" f"{previous}",
        ),
        encoding="utf-8",
    )


def main() -> None:
    os.chdir(PATHS.PROJECT_ROOT)
    release_file = parse_release_file(PATHS.RELEASE_FILE.read_text(encoding="utf-8"))
    bump_version(release_file.type.value)
    cur_ver = get_current_version()
    current_contributor = get_last_commit_contributor(os.getenv("BOT_TOKEN"))
    contributor_details = get_contributor_details(current_contributor)
    pretty_changes = pprint_release_change_log(release_file, contributor_details)
    update_change_log(pretty_changes, cur_ver)
    update_cmake_version(cur_ver)
    update_python_versions(cur_ver)
    git(
        "git",
        "add",
        str(PATHS.ROOT_CMAKE),
        str(INIT_FILE),
        str(CONANFILE),
        str(PATHS.PYPROJECT_TOML.resolve(True)),
        str(PATHS.CHANGELOG.resolve(True)),
    )
    # remove release file
    git("rm", str(PATHS.RELEASE_FILE))
    # GitHub release
    repo = githubref.get_repo(githubref.get_github_session())
    release = repo.create_git_release(
        name=f"qtgql {cur_ver}",
        tag=cur_ver,
        generate_release_notes=False,
        message=pretty_changes,
    )
    # publish python to GitHub
    subprocess.run(["poetry", "build"])
    for file in PATHS.PROJECT_ROOT.glob("dist/*"):
        release.upload_asset(path=str(file))


if __name__ == "__main__":
    main()
