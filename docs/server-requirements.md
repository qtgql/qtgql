!!! Note
    This document contains assumptions that qtgql makes about your server.
    If your server does not comply with these you might experience unwanted
    behaviours or the codegen will just not work.
___
### Pure fields
All the fields in the server are considered [Pure Functions](https://en.wikipedia.org/wiki/Pure_function).
Meaning that they should return the same value
if they were to be called with the same arguments
at the same time with same context.

Not only that this assumption is a GraphQL best-practice, it also has a great benefit
in global updates.
To demonstrate the purpose of this specification image that
operation X queried for
```graphql
me{
    name
    profilePic
}
```

And after a while operation Y queried for:
```graphql
me{
    nickName
    profilePic
}
```
Assuming that the profile picture has changed, operation X **would be updated**
as well with the new picture.
