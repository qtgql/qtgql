#include <catch2/catch_test_macros.hpp>

static int return_two(int number) { return 2; };

TEST_CASE("Should be 2", "[single-file]") { REQUIRE(return_two(1) == 2); };
