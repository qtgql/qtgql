# QtGQL

![Logo](./assets/logo.svg){ align=center width=350}
*GraphQL client for Qt and QML.*
## Features
!!! success "[Codegen (introspection compiler)](./codegen/tutorial.md)"
    - [x] object types, for each field there is a corresponding `Property`
    - [x] enums
    - [x] custom scalars
!!! success "Runtime"
    - [x] "Qt-native" graphql-transport-ws network manager (supports subscriptions).
!!! success "Helpers"
    - [x] [generic models](./itemsystem/intro.md) that get created from dictionaries (with update, pop, insert implemented by default)
    - [x] [`Property` classes](./utilities.md#auto-property) that are accessible from QML, with dataclasses  syntax (using attrs)
    - [x] `@slot` - decorator to be replaced with `QtCore.Slot()` that get types from type hints.

## Installation

<div class="termy">

```console

// This would install our codegen dependencies as well...

$ pip install qtgql[codegen]

---> 100%
```

</div>
