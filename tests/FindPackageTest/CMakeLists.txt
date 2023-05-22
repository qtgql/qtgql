cmake_minimum_required(VERSION 3.0.0 FATAL_ERROR)

project(QtGqlFindPackageTest)

find_package(QtGql REQUIRED)

add_executable(QtGqlFindPackageTest main.cpp)
target_link_libraries(QtGqlFindPackageTest QtGql::QtGql)
