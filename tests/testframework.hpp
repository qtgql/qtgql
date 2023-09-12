#include "doctest/doctest.h"
// TODO: remove if migrating to doctest.

#define SECTION(name) DOCTEST_SUBCASE(name)

// only if tags are used: will concatenate them to the test name string literal
#undef TEST_CASE
#define TEST_CASE(name, tags) DOCTEST_TEST_CASE(tags " " name)
#define TEST_CASE(name) DOCTEST_TEST_CASE(name)