cmake_minimum_required(VERSION 2.8)
project(MyHello)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_MACOSX_BUNDLE NO)

add_executable(hello hello.c)
include_directories(${CONAN_INCLUDE_DIRS})
target_link_libraries(hello ${CONAN_LIBS})

