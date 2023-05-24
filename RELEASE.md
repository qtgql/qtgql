Release type: minor

This release adds support for optional (nullable) scalars.

and initial support for setting variables.
i.e for this query:
```graphql
query MainQuery($returnNone: Boolean! = false) {
  user(retNone: $returnNone) {
    name
    age
    agePoint
    uuid
    birth
  }
}
```

You could set `$returnNone` to `true` like this.

```cpp
auto mq = std::make_shared<mainquery::MainQuery>();
mq->setVariables({true});
mq->fetch();
```
