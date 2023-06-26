Release type: patch

This release adds support for updates of list of nodes.

When operation X queries for list of nodes, the list would
get deserialized and each proxy that contains that list would update it's model based on the new data.
if the node itself has changed the changed fields would emit their own signals
to indicate the UI for updates.
