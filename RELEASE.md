Release type: patch

This release adds `currentObject` property for codegen BaseModel.
This is useful in QML where you have to access the current selected object outside
the delegate.
Fixes [#65](https://github.com/nrbnlulu/qtgql/issues/65)
