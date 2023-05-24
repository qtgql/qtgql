from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
QTGQL = ROOT_DIR / "qtgql"


def main(name: str):
    submod = QTGQL / name
    submod.mkdir(exist_ok=True)
    inc_dir = submod / "inc" / "qtgql" / name
    inc_dir.mkdir(parents=True, exist_ok=True)
    (inc_dir / f"{name}.hpp").write_text("# pragma once")


if __name__ == "__main__":
    main(input("enter component name"))
