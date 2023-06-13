Release type: patch

This release removes the previose `loose()` approach mainly due to complexity reasons.
Starting from now we have a periodic garbage collector on all `Node` derived classes.