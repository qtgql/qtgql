Release type: patch

Add support list of objects.
When a list is deserialized the instances are mapped based on operation ID
since lists are not part of the [field stability](https://graphql.org/learn/global-object-identification/#field-stability)
spec.
