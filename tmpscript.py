

deps = 'libgl1-mesa-dev libx11-dev  libxau-dev libxcb-keysyms1 libxcb-cursor-dev libxcb-xfixes0 libxcb-render0 libxcb1 libxcb-render-util0 libxcb-xinerama0 libxcb-util1 libxaw7-dev  libx11-xcb-dev  libxcb-glx0 libxcb-sync1  libxaw7-dev  libx11-dev build-essential  libfontenc-dev  libxcb-image0  libice-dev  libx11-xcb-dev libxcb-xkb-dev libxcb-icccm4 libxcb-shm0 libxkbcommon-dev libsm-dev  libsm-dev  libfontenc-dev libxcb-shape0  libxau-dev  libxcb-randr0 libpulse-dev libgstreamer-gl1.0-0 libxkbcommon-x11-0 libice-dev'

add = 'libx11-dev", "libx11-xcb-dev", "libfontenc-dev", "libice-dev", "libsm-dev", "libxau-dev", "libxaw7-dev"'
l = [r.replace('"', " ") for r in add.split(", ")]
res = set(l).union(set(deps.split(" ")))
print(" ".join(res))