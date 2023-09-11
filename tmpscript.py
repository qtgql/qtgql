

s = '"libx11-dev", "libx11-xcb-dev", "libfontenc-dev", "libice-dev", "libsm-dev", "libxau-dev", "libxaw7-dev'

l = [r.replace('"', " ") for r in s.split(", ")]
print(" ".join(l))