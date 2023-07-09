!!! Note
    This document contains assumptions that qtgql makes about your server.
    If your server does not comply with these you might experience unwanted
    behaviours or the codegen will just not work.
___
## Node Interface
The Node interface is defined like this

```graphql
# An object with a Globally Unique ID
interface Node {
  # The ID of the object.
  id: ID!
}
```
Any object that implements this interface
is considered globally unique, thus allowing certain optimizations
to be implemented by the client (in this case qtgql compiler).

For example for this schema:
```graphql
interface Node {
  id: ID!
}

type User implements Node {
  id: ID!
  name: String!
  age: Int!
  profilePicture: String!
}

type Query {
  me: User!
}

type Mutation{
    changeProfilePicture(source: String!): User!
}
```
If when you start the app you were querying for:
```graphql
me{
    name
    profilePicture
}
```
And you got your image. All good for now.
But then the user sent this mutation:
```graphql
changeProfilePicture(source: "https://t.ly/q4akF"){
    profilePicture
}
```
You would need to imperatively update the picture link
where ever you show that in the UI.

**But** Node Interface saves you here, since there is only
**one** instance of a node at an application lifetime, the picture
will be updated automatically when this mutation arrives.

This is not the only advantage, think of a case where some other
fields might have changed in the server since you fetched them.
If you were to fetch them in one operation the changes will be
mirrored in all the other operations.

## Pure fields
All the fields in the server are considered [Pure Functions](https://en.wikipedia.org/wiki/Pure_function).
Meaning that they should return the same value
if they were to be called with the same arguments.
!!! Warning
    This means i.e that if a field would be changed based on
    some arbitrary context (i.e headers) you might get unwanted behaviours.

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
