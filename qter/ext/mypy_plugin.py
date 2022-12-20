from mypy.plugin import Plugin
from mypy.plugins.attrs import attr_define_makers

attr_define_makers.add("qter.itemsystem._core.define_roles")
attr_define_makers.add("qter.autoproperty.define_properties")


class MyPlugin(Plugin):
    # Our plugin does nothing, but it has to exist so this file gets loaded.
    pass


def plugin(version):
    return MyPlugin
