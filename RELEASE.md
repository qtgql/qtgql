Release type: patch

Fix a case that updates on Node implementors might try to compare to a field that
is null ATM of updating it. See #381.
