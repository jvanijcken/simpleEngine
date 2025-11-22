cmake_minimum_required(VERSION 3.15)
project(PyChess C)

set(CMAKE_C_STANDARD 99)

# Find Python includes and library automatically
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

include_directories(${Python3_INCLUDE_DIRS})
include_directories("../include")

# List your source files explicitly for clarity and adding subfolders
set(SOURCES
        ../src/C/algorithms.c
        ../src/C/moveFunctions.c
        ../src/C/moveGeneration.c
        ../src/C/pychessmodule.c

        ../src/C/attackTables.c
        ../src/C/boardEvaluation.c
        ../src/C/magicBitboards.c
        ../src/C/transpositionTable.c
        ../src/C/zobristHashing.c

        ../testing/debugTools.c
)

# Specify the output directory for the built library
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/.venv/Lib/site-packages")

add_library(PyChess MODULE ${SOURCES})

target_link_libraries(PyChess PRIVATE ${Python3_LIBRARIES})

# Remove the 'lib' prefix and force .pyd suffix for Python extension on Windows
set_target_properties(PyChess PROPERTIES
        PREFIX ""
        SUFFIX ".pyd"
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/.venv/Lib/site-packages"
)
