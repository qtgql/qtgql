Release type: minor

This release adds support for optional input objects / scalar.

### Internal changes
- arguments are not stored on with dynamically generated tuple because
input objects might refer to themselves also the tuple approach is too hard to maintain.

- This release changes the way root types are instantiated.
Previously they were static heap allocated instance.
Now we use a shared pointer solution
that would be collected if there is no operation using this concrete root type.

- Scalars are now shared pointers. this is because root type fields
might be empty (if this operation is the first to use this root type) so we need to use either
shared pointer or std::optional.
Another reason to move to `sp` is because the scalars won't get copied all the time.
Also in the future we'll might use this for garbage collection.
