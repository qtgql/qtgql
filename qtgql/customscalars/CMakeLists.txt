set(COMPONENT_NAME customscalars)
add_library(${COMPONENT_NAME})
target_sources(
  ${COMPONENT_NAME}
  PUBLIC inc/qtgql/customscalars/basecustomscalar.hpp
         inc/qtgql/customscalars/customscalars.hpp
  PRIVATE customscalars.cpp)
add_library(${PROJECT_NAME}::${COMPONENT_NAME} ALIAS ${COMPONENT_NAME})
target_link_libraries(${COMPONENT_NAME} PUBLIC Qt6::Core)
target_include_directories(${COMPONENT_NAME} PUBLIC inc)
