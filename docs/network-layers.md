In order to know how to access your GraphQL server,
QtGQL requires developers to provide an object implementing the `NetworkLayer` interface when creating an instance of a QtGQL Environment.

The environment uses this network layer to execute queries, mutations, and (if your server supports them) subscriptions.
This allows developers to use whatever transport (HTTP, WebSockets, etc.) and authentication is most appropriate for their application,
decoupling the environment from the particulars of each application's network configuration.
___
## Builtin network layers
QtGQL provides some network layers that are widely spread out-of-the-box:

### [GraphQL-over-HTTP](https://graphql.github.io/graphql-over-http/draft)
>HTTP is the most common choice as the client-server protocol when using GraphQL because of its ubiquity. However the GraphQL specification deliberately does not specify the transport layer.
>The closest thing to an official specification is the article Serving over HTTP. Leading implementations on both client and server have mostly upheld those best practices and thus established a de-facto standard that is commonly used throughout the ecosystem.
>This specification is intended to fill this gap by specifying how GraphQL should be served over HTTP. The main intention of this specification is to provide interoperability between different client libraries, tools and server implementations.

To use this layer, you'll need to pass an instance of it to your environment.

!!! example
    ```cpp
    auto env = std::shared_ptr<qtgql::bases::Environment>(
        new qtgql::bases::Environment("Countries",
        std::unique_ptr<qtgql::bases::NetworkLayerABC>(
            new qtgql::gqloverhttp::GraphQLOverHttp({"https://countries.trevorblades.com/"}))
        )
    );
    qtgql::bases::Environment::set_gql_env(env);
    ```

### [GraphQL-over-WebSocket](https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md)
A widely used protocol mainly for subscriptions.
!!! example
    ```cpp
    auto env = std::shared_ptr<qtgql::bases::Environment>(
        new qtgql::bases::Environment("FooBar",
        std::unique_ptr<gqltransportws::GqlTransportWs>(new gqltransportws::GqlTransportWs({.url={"ws://foobar.com"}}));
        )
    );
    qtgql::bases::Environment::set_gql_env(env);
    ```

## Create your own network layer
To create your own network layer, you'll need to extend `qtgql::bases::NetworkLayerABC`
You have to implement only one method namely `void execute(const std::shared_ptr<HandlerABC> &handler)`.

This method accepts a handler which will contain the query.
Your network layer should communicate with the handler using
- `on_next`: when a graphql message received (on queries and mutations there would only be one like this)
- `on_error`: if there was any **GraphQL error** in the **operation** (network, errors should be handled separately).
- `on_completed`: when the operation is completed.
