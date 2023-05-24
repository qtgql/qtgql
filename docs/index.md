# QtGQL

![Logo](./assets/logo.svg){ align=center width=350}
*GraphQL client for Qt and QML.*
This library is an attempt to provide a high-level graphql client to the QT world.
## Similar projects
- [react-relay](https://relay.dev/)
- [apollo-client](https://www.apollographql.com/docs/react/)

## Features - TBD
!!! success "[Codegen (introspection compiler)](./codegen/tutorial.md)"
    - [x] Object types, for each field there is a corresponding `Q_PROPERTY`
    - [ ] Enums
    - [ ] Custom scalars
    - [ ] Unions
    - [ ] interfaces
    - [ ] Garbage collection
    - [ ] Type-safe operation handlers
        - [x] Query.
        - [ ] Mutations.
        - [ ] Subscriptions.
    - [ ] Query updates: fetch the same query multiple times would not instantiate everything from scratch
    - [ ] Fully typed input variables.

!!! success "Network layer"
    - [x] Native-Qt client implementation of "[graphql-transport-ws](https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md)" protocol (supports subscriptions) - You can provide your own network layer though.
