###  Qt framework for building graphql driven QML applications
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/qtgql?style=for-the-badge)](https://pypi.org/project/qtgql/)
[![PyPI](https://img.shields.io/pypi/v/qtgql?style=for-the-badge)](https://pypi.org/project/qtgql/)
[![GitHub Workflow Status (with branch)](https://img.shields.io/github/actions/workflow/status/nrbnlulu/qtgql/tests.yml?branch=main&style=for-the-badge)
](https://github.com/nrbnlulu/qtgql/actions/workflows/tests.yml)
[![Codecov](https://img.shields.io/codecov/c/github/nrbnlulu/qtgql?style=for-the-badge)](https://app.codecov.io/gh/nrbnlulu/qtgql)
[![Discord](https://img.shields.io/discord/1067870318301032558?label=discord&style=for-the-badge)](https://discord.gg/5vmRRJp9fu)


### Disclaimer
This project is currently under development, and **it is not** production ready,
You can play-around and tell us what is wrong / missing / awesome :smile:.




### Features
#### Codegen (introspection compiler)
- [x] object types, for each field there is a corresponding `Property`
- [x] enums
- [x] custom scalars
#### Runtime
- [x] "Qt-native" graphql-transport-ws network manager (supports subscriptions).
#### Helpers
- [x] generic models that get created from dictionaries (with update, pop, insert implemented by default)
- [x] `Property` classes that are accessible from QML, with dataclasses  syntax (using attrs)
- [x] `@slot` - decorator to be replaced with `QtCore.Slot()` that get types from type hints.

### Future vision
- Code generation from schema inspection
Ideally every graphql type would be a `QObject` with `Property` for each field.
- possibly generate C++ bindings from schema inspection
- Query only what defined by the user (similar to how relay does this)
- Auto mutations
- Subscriptions

### "Just build a web based UI"
Qt-QML IMO is a big game changer
- you get native performance
- UI code is very clear and declarative
- Easy to customize
- Easy to learn

One of the big disadvantages in Qt-QML is that Qt-C++ API is very repetitive and hard to maintain
for data-driven applications.

although it is tempting to just use `relay` or other `JS` graphql lib
there is a point where you would suffer from performance issues (react-native).

[Visit the docs for more info](https://nrbnlulu.github.io/qtgql/)
