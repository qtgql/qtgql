add_library(utils "")
add_library(${PROJECT_NAME}::utils ALIAS utils)
target_sources(qtgqlbases PUBLIC utils.hpp)
target_include_directories(qtgqlbases PUBLIC ${CMAKE_CURRENT_LIST_DIR})
