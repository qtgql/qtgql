![qt-graphql.png](assets%2Fqt-graphql.png)
###  Qt framework for building graphql driven QML applications
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/qtgql?style=for-the-badge)
![PyPI](https://img.shields.io/pypi/v/qtgql?style=for-the-badge)
![GitHub Workflow Status (with branch)](https://img.shields.io/github/actions/workflow/status/nrbnlulu/qtgql/tests.yml?branch=main&style=for-the-badge)
![Codecov](https://img.shields.io/codecov/c/github/nrbnlulu/qtgql?style=for-the-badge)
[![forthebadge](https://forthebadge.com/images/badges/gluten-free.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/contains-cat-gifs.svg)](https://forthebadge.com)

### Disclaimer
This project is currently under development and **it is not** production ready,
You can play-around and tell us what is wrong / missing / awesome :smile:.

### Intro
Qt-QML IMO is a big game changer
- you get native performance
- UI code is very clear and declarative
- Easy to customize
- Easy to learn

One of the big disadvantages in Qt-QML is that Qt-C++ API is very repititive and hard to maintain
for data-driven applications.

although it is tempting to just use `relay` or other `JS` graphql lib
there is a point where you would suffer from performance issues (:roll_eyes:  react-native).


### GraphQL support
As I have proggresed with the codebase I realized that I can do better and possibly mimic some
features of graphql relay at the cost of making this project more opinionated.
So I decided to rename it to `qtgql` (previouslly cuter :cat: ).
Some of the current features:
 - Qt-native graphql-transport-ws network manager (supports subscriptions).
 - generic models that get created from dictionaries (with update, pop, insert implemeanted by default)
 - property classes that are accessible from QML, with dataclasses  syntax (using attrs)

### Future vision
- Code generation from schema inspection
Ideally every graphql type would be a `QObject` with `Property` for each field.
- possibly generate C++ bindings from schema inspection
- Query only what defined by the user (similar to how relay does this)
- Auto mutations
- Subscriptions

[Visit the docs for more info](https://nrbnlulu.github.io/qtgql/)
