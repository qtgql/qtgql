add_library(gqlwstransport "")
add_library(${PROJECT_NAME}::gqlwstransport ALIAS gqlwstransport)
target_sources(
  gqlwstransport
  PRIVATE gqlwstransport.cpp
  PUBLIC ${CMAKE_CURRENT_LIST_DIR}/gqlwstransport.hpp)
target_link_libraries(gqlwstransport PUBLIC Qt6::Core Qt6::WebSockets)
target_include_directories(gqlwstransport PUBLIC ${CMAKE_CURRENT_LIST_DIR})
target_link_libraries(gqlwstransport PUBLIC qtgql::bases)
