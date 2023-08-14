Release type: minor

This release adds support for optional input objects / scalar.

### Internal changes
- arguments are not stored on with dynamically generated tuple because
input objects might refer to themselves (though i)
- This release changes the way root types are instantiated.
Previously they were static heap allocated instance.
Now we use a shared pointer solution
that would be collected if there is no operation using this concrete root type.
