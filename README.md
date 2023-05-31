###  Qt framework for building graphql driven QML applications
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/qtgql?style=for-the-badge)](https://pypi.org/project/qtgql/)
[![PyPI](https://img.shields.io/pypi/v/qtgql?style=for-the-badge)](https://pypi.org/project/qtgql/)
[![GitHub Workflow Status (with branch)](https://img.shields.io/github/actions/workflow/status/nrbnlulu/qtgql/tests.yml?branch=main&style=for-the-badge)
](https://github.com/nrbnlulu/qtgql/actions/workflows/tests.yml)
[![Codecov](https://img.shields.io/codecov/c/github/nrbnlulu/qtgql?style=for-the-badge)](https://app.codecov.io/gh/nrbnlulu/qtgql)
[![Discord](https://img.shields.io/discord/1067870318301032558?label=discord&style=for-the-badge)](https://discord.gg/5vmRRJp9fu)
![PyPI - Downloads](https://img.shields.io/pypi/dm/qtgql?style=for-the-badge)

### Disclaimer
This project is currently under development, and **it is not** production ready,
You can play-around and tell us what is wrong / missing / awesome :smile:.

[Visit the docs for more info](https://nrbnlulu.github.io/qtgql/) (WIP)


### Features
- [x] object types, for each field there is a corresponding `Q_PROPERTY`
- [x] enums
- [ ] custom scalars
- [ ] Unions
- [ ] interfaces
- [ ] Garbage collection
- [ ] Type-safe operation handlers
  - [x] Query.
  - [ ] Mutations.
  - [ ] Subscriptions.
- [ ] updates: fetch the same query multiple times would not instantiate everything from scratch
it would compare the current data with data received and emit __only__ the signals that are needed.
- [x] Native-Qt client implementation of "[graphql-transport-ws](https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md)" protocol (supports subscriptions) - You can provide your own network layer though.
- [ ] Fully typed input variables.
