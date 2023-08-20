# QtGQL

![Logo](./assets/logo.svg){ align=center width=350}
*GraphQL client for Qt and QML.*
This library is an attempt to provide a high-level graphql client to the QT world.
## Similar projects
- [react-relay](https://relay.dev/)
- [apollo-client](https://www.apollographql.com/docs/react/)

## Features - TBD
- types:
    - [x] Object Type
    - [x] Enum
    - [x] Custom scalar
    - [x] Union
    - [x] Interface
      - [x] [Node Interface](./server-requirements.md#node-interface)
    - List of:
        - [x] Object Type
        - [x] Scalar
        - [ ] custom scalar
        - [x] Interface
        - [x] Union
        - [ ] Enum
- [x] Fragments
- [x] Operation handlers (queries the server and deserialize data) for Query / Mutation / Subscription.
- [x] *Fully typed operation variables.* (partially, [see](https://github.com/qtgql/qtgql/issues/272))
- [x] *Garbage collection.* (partially, [see](https://github.com/qtgql/qtgql/issues/277))
