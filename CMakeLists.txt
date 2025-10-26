cmake_minimum_required(VERSION 3.15)
project(PyChess C)

set(CMAKE_C_STANDARD 99)

# Find Python includes and library automatically
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

include_directories(${Python3_INCLUDE_DIRS})
include_directories("../include")

# List your source files explicitly for clarity and adding subfolders
set(SOURCES
        ../src/algorithms.c
        ../src/moveFunctions.c
        ../src/moveGeneration.c
        ../src/pychessmodule.c

        ../src/tables/attackTables.c
        ../src/tables/boardEvaluation.c
        ../src/tables/magicBitboards.c
        ../src/tables/transpositionTable.c
        ../src/tables/zobristHashing.c

        ../testing/debugTools.c
)

add_library(PyChess MODULE ${SOURCES})

target_link_libraries(PyChess PRIVATE ${Python3_LIBRARIES})

# Remove the 'lib' prefix and force .pyd suffix for Python extension on Windows
set_target_properties(PyChess PROPERTIES
        PREFIX ""
        SUFFIX ".pyd"
)
