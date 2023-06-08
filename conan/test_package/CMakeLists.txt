cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(qtgql)
find_package(Qt6 REQUIRED COMPONENTS Core)

add_executable(example src/example.cpp)

target_link_libraries(example PRIVATE qtgql::qtgql Qt6::Core)
