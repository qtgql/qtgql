add_library(qtgqlbases "")
add_library(${PROJECT_NAME}::qtgqlbases ALIAS qtgqlbases)
target_sources(
  qtgqlbases
  PRIVATE baseqgraphqlobject.cpp
  PUBLIC ${CMAKE_CURRENT_LIST_DIR}/baseqgraphqlobject.hpp)
target_link_libraries(qtgqlbases PUBLIC Qt6::Core)
target_include_directories(qtgqlbases PUBLIC ${CMAKE_CURRENT_LIST_DIR})
