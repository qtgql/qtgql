from qtgql.itemsystem import define_roles, role


@define_roles
class Worm:
    name: str = role()
    family: str = role()
    size: int = role()


@define_roles
class Apple:
    size: int = role()
    owner: str = role()
    color: str = role()
    worms: Worm = role(default=None)
