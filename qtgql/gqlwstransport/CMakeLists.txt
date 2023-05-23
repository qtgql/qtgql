set(COMPONENT_NAME gqlwstransport)
add_library(${COMPONENT_NAME})
add_library(${PROJECT_NAME}::${COMPONENT_NAME} ALIAS ${COMPONENT_NAME})
target_sources(
  ${COMPONENT_NAME}
  PRIVATE gqlwstransport.cpp operationhandler.cpp
  PUBLIC inc/qtgql/gqlwstransport/gqlwstransport.hpp
         inc/qtgql/gqlwstransport/operationhandler.hpp)
target_link_libraries(${COMPONENT_NAME} PUBLIC Qt6::Core Qt6::WebSockets
                                               qtgql::bases)
target_include_directories(${COMPONENT_NAME} PUBLIC inc)
