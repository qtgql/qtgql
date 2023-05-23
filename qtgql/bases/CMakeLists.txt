set(COMPONENT_NAME qtgqlbases)
add_library(${COMPONENT_NAME} "")
add_library(${PROJECT_NAME}::bases ALIAS ${COMPONENT_NAME})
target_sources(
  ${COMPONENT_NAME}
  PUBLIC inc/qtgql/bases/objecttype.hpp inc/qtgql/bases/metadata.hpp
         inc/qtgql/bases/listmodel.hpp inc/qtgql/bases/networklayer.hpp
         inc/qtgql/bases/constants.hpp inc/qtgql/bases/environment.hpp
  PRIVATE environment.cpp)
target_link_libraries(${COMPONENT_NAME} PUBLIC Qt6::Core)
target_include_directories(${COMPONENT_NAME} PUBLIC inc)
