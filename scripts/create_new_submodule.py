from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
QTGQL = ROOT_DIR / "qtgql"


def main(name: str):
    submod = QTGQL / name
    submod.mkdir(exist_ok=True)
    (submod / "inc" / "qtgql" / name).mkdir(parents=True)


main("gqlwstransport")
