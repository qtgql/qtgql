from .releasefile import parse_release_file
from .utils import PATHS


def main() -> None:
    assert PATHS.RELEASE_FILE.exists(), "Release file dosn't exist"
    parse_release_file(PATHS.RELEASE_FILE.read_text("utf-8"))


if __name__ == "__main__":
    main()
