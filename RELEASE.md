Release type: minor

This release adds support for updates.
It does this by generating for each query handler
an object that represents the selections for this query.
Then if the data is being compared against local data as follows

1. __builtin scalars__ - compared against the current value.
2. __custom scalars__ - By default compared against the inner value of the custom scalar.
3. __object_type__ - will compare against each field (generated on `update()`)
edge cased:
 - new id reached: resolution -> create a new object and replace the pointer with the field setter.
 - field was null before (ATM objecttypes are the only real fields that can be null): resolution -> use setter on this field
 -
4. __unions__ - if `__typename` is different will cause a whole update, else fallback to (3)
5. __enums__ - compare against the enum value / name (which the same string).
6. __lists a.k.a models__ -- since lists just store a pointer (or a key in the store) to a node and the node itself
already compared when `.from_dict` called on the raw-node,
we should just compare if the pointers points the right index so first crop the length of the list
to the length of the arrived data, then for each index compare the `ID!` and replace correspondingly.



This release also introduce `typename` property on each object type.
This is used by unions deserializers and can be useful for rendering specific component
based on the typename.
