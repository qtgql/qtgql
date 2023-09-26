import datetime
import os
import re
import subprocess
import textwrap
from dataclasses import dataclass
from pathlib import Path

import httpx
import tomlkit
from autopub import autopub
from releasefile import get_release_preview, parse_release_file


class PATHS:
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
    ROOT_CMAKE = PROJECT_ROOT / "CMakeLists.txt"
    QTGQLCODEGEN_ROOT = PROJECT_ROOT / "qtgqlcodegen"
    PYPROJECT_TOML = PROJECT_ROOT / "pyproject.toml"
    CHANGELOG = PROJECT_ROOT / "CHANGELOG.md"
    RELEASE_FILE = PROJECT_ROOT / "RELEASE.md"


REPO_SLUG = "qtgql/qtgql"

def git(*args: str):
    # Do not decode ASCII for commit messages so emoji are preserved
    return subprocess.check_output(["git", *args])

@dataclass
class PRContributor:
    pr_number: int
    pr_author_username: str
    pr_author_fullname: str


def get_last_commit_contributor(token: str) -> PRContributor:
    org, repo = REPO_SLUG.split('/')
    current_commit = (
        subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()
    )
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
        pr_author_username=pr_author_username
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
    return (f"Contributed by [{conributor.pr_author_fullname or conributor.pr_author_username}]"
            f"(https://github.com/{conributor.pr_author_username}) via [PR #{conributor.pr_number}]"
            f"(https://github.com/{REPO_SLUG}/pull/{conributor.pr_number}/)")

def get_current_version() -> str:
    pyproject = tomlkit.parse(PATHS.PYPROJECT_TOML.read_text(encoding='utf-8'))
    return pyproject['tool']['poetry']['version']
def bump_version(bump_string: str) -> None:
    subprocess.run(['poetry', 'version', bump_string])

def update_change_log(current_changes: str, version: str) -> None:
    main_header = textwrap.dedent("""
    CHANGELOG
    =========
    
    """)
    current_changes = current_changes[1:-1]  # remove release type
    def is_first_or_last_line_empty(s: str) -> bool:
        return s.startswith('\n') or s.endswith('\n')

    while is_first_or_last_line_empty(current_changes):
        current_changes = current_changes.strip('\n')
    this_header = textwrap.dedent(f"""
    {version} - {datetime.date.today().strftime()}
    --------------------
    
    """)
    previous = PATHS.CHANGELOG.read_text(encoding='utf-8').strip(main_header)
    textwrap.dedent(f"{main_header}"
                    f"{this_header}"
                    f"{current_changes}\n"
                    f"{previous}"
                    )


if __name__ == "__main__":
    os.chdir(PATHS.PROJECT_ROOT)
    release_file = parse_release_file(PATHS.RELEASE_FILE.read_text(encoding='utf-8'))
    bump_version(release_file.type.value)
    cur_ver = get_current_version()
    update_change_log(release_file.changelog)
    update_cmake_version(cur_ver)
    update_python_versions(cur_ver)
    subprocess.run(
        ["git", "add",
         str(PATHS.ROOT_CMAKE),
         str(INIT_FILE),
         str(CONANFILE),
         str(PATHS.PYPROJECT_TOML.resolve(True)),
         str(PATHS.CHANGELOG.resolve(True))
         ],
        cwd=PATHS.PROJECT_ROOT,
    ).check_returncode()
    autopub.build(args)
    autopub.commit(args)
    autopub.githubrelease(args)
