cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(qtgql REQUIRED COMPONENTS bases gqlwstransport)

add_executable(example src/example.cpp)
target_link_libraries(example PRIVATE gqlwstransport)
