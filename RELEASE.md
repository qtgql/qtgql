Release type: minor

### This release adds QML query handlers generation.

i.e:

**File**: _main.qml_

```qml
import QtGql 1.0 as Gql

Item{
    // `MainQuery` is generated from the query we write here.
    // the name is based on the operationName (MainQuery)
    Gql.MainQuery{id: query
        graphql: `query MainQuery {...}`
    }
    Text{
        text: query.data.somefield
    }
}
```
