add_library(gqltransport "")
add_library(${PROJECT_NAME}::gqltransport ALIAS gqltransport)
target_sources(
  gqltransport
  PRIVATE gqltransport.cpp
  PUBLIC ${CMAKE_CURRENT_LIST_DIR}/gqltransport.hpp)
target_link_libraries(gqltransport PUBLIC Qt6::Core Qt6::WebSockets)
target_include_directories(gqltransport PUBLIC ${CMAKE_CURRENT_LIST_DIR})
