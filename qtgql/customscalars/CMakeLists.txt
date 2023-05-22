set(COMPONENT_NAME qtgqlcustomscalars)
add_library(${COMPONENT_NAME} STATIC "")
target_sources(
  ${COMPONENT_NAME}
  PUBLIC qtgqlcustomscalar.hpp qtgqlcustomscalars.hpp
  PRIVATE qtgqlcustomscalars.cpp)
add_library(${PROJECT_NAME}::${COMPONENT_NAME} ALIAS ${COMPONENT_NAME})
target_include_directories(${COMPONENT_NAME} PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(${COMPONENT_NAME} PUBLIC Qt6::Core ${PROJECT_NAME}::bases)
