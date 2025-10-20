cmake_minimum_required(VERSION 4.0)
project(simpleEngine C)

set(CMAKE_C_STANDARD 99)


# Adjust this path to wherever your Python install is
set(PYTHON_INCLUDE_DIR "C:/Users/jvani/AppData/Local/Programs/Python/Python312/include")
set(PYTHON_LIB_DIR "C:/Users/jvani/AppData/Local/Programs/Python/Python312/libs")

include_directories(${PYTHON_INCLUDE_DIR})
link_directories(${PYTHON_LIB_DIR})

file(GLOB SOURCES "src/*.c")

add_library(simpleEngine MODULE ${SOURCES})

target_link_libraries(simpleEngine PRIVATE python312)
set_target_properties(simpleEngine PROPERTIES PREFIX "" SUFFIX ".pyd")
