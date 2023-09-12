#
#
# deps = 'libxcb-xfixes0-dev libxcb-icccm4-dev libxcb-randr0-dev libxcb-keysyms1-dev libxcb-image0 libxcb-cursor-dev libxcb-shm0 libpulse-dev libxcb-icccm4 libxkbcommon-x11-0  libsm-dev  libxau-dev libgl1-mesa-dev libx11-dev libxcb-util1 libxcb-render-util0  libice-dev   libxau-dev  libxcb-randr0 libxkbcommon-dev libfontenc-dev libxcb-sync1  libx11-xcb-dev  libxcb1 build-essential libxaw7-dev libxcb-xfixes0 libxcb-render0 libx11-dev  libx11-xcb-dev  libxaw7-dev  libxcb-glx0 libgstreamer-gl1.0-0 libxcb-keysyms1 libxcb-xinerama0 libice-dev libxcb-xkb-dev libxcb-shape0  libfontenc-dev  libsm-dev'
#
# add = 'libxcomposite-dev, libxcursor-dev, libxdamage-dev, libxfixes-dev, libxi-dev, libxinerama-dev, libxmuu-dev, libxrandr-dev, libxres-dev, libxss-dev, libxtst-dev, libxv-dev, libxvmc-dev, libxxf86vm-dev, libxcb-icccm4-dev, libxcb-keysyms1-dev, libxcb-randr0-dev, libxcb-shape0-dev, libxcb-sync-dev, libxcb-xfixes0-dev, libxcb-xinerama0-dev, libxcb-dri3-dev'
# l = [r.replace('"', " ") for r in add.split(", ")]
# res = set(l).union(set(deps.split(" ")))
# print(" ".join(res))

# TODO: don't commit this.

import re
from pathlib import Path

TESTS_DIR = Path(__file__).parent / "tests"

tests = TESTS_DIR.glob("**/test_*.cpp")

for test in tests:
    regex = ",\s*\"\[.*?\]\""
    original = test.read_text(encoding="utf-8")
    result = re.sub(regex, "", original)
    test.write_text(result, encoding="utf-8")
