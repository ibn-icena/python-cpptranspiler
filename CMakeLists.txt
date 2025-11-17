cmake_minimum_required(VERSION 3.10)
project(python-cpp-transpiler)

set(CPR_USE_SYSTEM_CURL OFF)
add_subdirectory(third_party/cpr)

add_executable(main cpp_src/main.cpp)
target_link_libraries(main PRIVATE cpr::cpr)
target_include_directories(main PRIVATE third_party)
