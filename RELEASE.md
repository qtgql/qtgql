Release type: patch

Migrate to "singleton" root types.
The advantage for this architecture is that the ui won't be updated every-time
a (next) message arrives, as well as for cross-operation updates.

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
as well.
