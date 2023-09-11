

deps = 'libxcb-cursor-dev libxcb-randr0 libxcb-glx0 libxcb-render-util0 libxkbcommon-dev libxcb-render0 libxcb-xkb-dev libxcb1 libx11-xcb-dev libgl1-mesa-dev libxcb-image0 libpulse-dev libice-dev libxcb-util1 libxcb-shm0 libx11-dev libxaw7-dev libxcb-sync1 libxkbcommon-x11-0 libsm-dev build-essential libxcb-icccm4 libfontenc-dev libxau-dev libgstreamer-gl1.0-0 libxcb-xinerama0 libxcb-shape0 libxcb-xfixes0 libxcb-keysyms1'
add = 'libx11-dev", "libx11-xcb-dev", "libfontenc-dev", "libice-dev", "libsm-dev", "libxau-dev", "libxaw7-dev"'

l = [r.replace('"', " ") for r in add.split(", ")]
res = set(l).union(set(deps.split(" ")))
print(" ".join(res))