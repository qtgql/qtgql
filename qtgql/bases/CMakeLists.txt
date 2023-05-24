set(COMPONENT_NAME qtgqlbases)
add_library(${COMPONENT_NAME} "")
add_library(${PROJECT_NAME}::bases ALIAS ${COMPONENT_NAME})
target_sources(
  ${COMPONENT_NAME}
  PUBLIC objecttype.hpp metadata.hpp listmodel.hpp networklayer.hpp
         constants.hpp environment.hpp
  PRIVATE environment.cpp)
target_link_libraries(${COMPONENT_NAME} PUBLIC Qt6::Core)
target_include_directories(${COMPONENT_NAME} PUBLIC inc)
