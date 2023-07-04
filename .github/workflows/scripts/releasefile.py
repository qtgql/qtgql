from __future__ import annotations

import re
from enum import Enum

from attrs import define
from tests.conftest import PATHS

release_file = PATHS.PROJECT_ROOT / "RELEASE.md"

# Shamelessly copied from strawberry
# https://github.com/strawberry-graphql/strawberry/blob/main/.github/release-check-action/release.py

RELEASE_TYPE_REGEX = re.compile(r"^[Rr]release [Tt]ype: (major|minor|patch)$")


class InvalidReleaseFileError(Exception):
    pass


class ReleaseType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


@define
class ReleaseFile:
    type: ReleaseType | None
    changelog: str | None = None

    @classmethod
    def from_file(cls) -> ReleaseFile:
        if not release_file.exists():
            raise InvalidReleaseFileError(
                "Could not find `RELEASE.md`. Please provide a RELEASE.md file in the project root.",
            )

        changelog = release_file.read_text()
        match = RELEASE_TYPE_REGEX.match(changelog.splitlines()[0])

        if not match:
            print(release_file.read_text())  # noqa
            raise InvalidReleaseFileError("Could not find a valid release type")

        change_type_key = match.group(1)
        release_type = ReleaseType[change_type_key.upper()]
        return cls(
            release_type,
            changelog,
        )


@define
class ReleasePreview:
    changelog: str | None = None
    error: str | None = None


def get_release_preview() -> ReleasePreview:
    try:
        return ReleasePreview(changelog=ReleaseFile.from_file().changelog)
    except InvalidReleaseFileError as exc:
        return ReleasePreview(error=exc.args[0])


if __name__ == "__main__":
    get_release_preview()
