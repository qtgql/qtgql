add_library(qtgqlbases "")
add_library(${PROJECT_NAME}::bases ALIAS qtgqlbases)
target_sources(
  qtgqlbases PUBLIC qtgqlobjecttype.hpp qtgqlmetadata.hpp qtgqllistmodel.hpp
                    qtgqlnetworklayer.hpp qtgqlconstants.hpp)
target_link_libraries(qtgqlbases PUBLIC Qt6::Core)
target_include_directories(qtgqlbases PUBLIC ${CMAKE_CURRENT_LIST_DIR})
