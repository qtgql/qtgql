from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from github.PullRequest import PullRequest

RELEASE_TYPE_REGEX = re.compile(r"(?i)Release type: (minor|major|patch)$")


class InvalidReleaseFileError(FileExistsError):
    ...


class ReleaseType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


@dataclass
class ReleasePreview:
    type: ReleaseType
    changelog: str


def get_release_preview(pr: PullRequest) -> ReleasePreview:
    for f in pr.get_files():
        if f.filename == "RELEASE.md":
            release_file = f.contents_url
            download_url = requests.get(f.contents_url, timeout=10).json()["download_url"]
            contents = requests.get(download_url, timeout=10).content.decode("utf-8")
            match = RELEASE_TYPE_REGEX.match(contents.splitlines()[0])

            if not match:
                print(release_file.read_text())  # noqa
                raise InvalidReleaseFileError("Could not find a valid release type")

            change_type_key = match.group(1)
            release_type = ReleaseType[change_type_key.upper()]
            return ReleasePreview(
                release_type,
                contents,
            )

    raise InvalidReleaseFileError(
        "Could not find `RELEASE.md`. Please provide a RELEASE.md file in the project root.",
    )
