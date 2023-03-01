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

[Visit the docs for more info](https://nrbnlulu.github.io/qtgql/)


### Features
- [x] object types, for each field there is a corresponding `Property`
- [x] enums
- [x] custom scalars
- [x] Unions
- [x] query handlers: queries your server when a component uses this query (or imperatively fetched).
- [x] query updates: fetch the same query multiple times would not instantiate everything from scratch
it would compare the current data with data received and emit __only__ the signals that are needed.
- [x] "Qt-native" graphql-transport-ws network manager (supports subscriptions).
#### Helpers
- [x] generic models that get created from dictionaries (with update, pop, insert implemented by default)
- [x] `Property` classes that are accessible from QML, with dataclasses  syntax (using attrs)
- [x] `@slot` - decorator to be replaced with `QtCore.Slot()` that get types from type hints.

### TODO
- Mutations
- Subscriptions
- Migrate to C++
- Fragments?
