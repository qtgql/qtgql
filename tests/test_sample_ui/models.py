from qtgql.itemsystem import BaseType, role


class Worm(BaseType):
    name: str = role()
    family: str = role()
    size: int = role()


class Apple(BaseType):
    size: int = role()
    owner: str = role()
    color: str = role()
    worms: Worm = role(default=None)
