import sys
from setuptools import setup, Extension

from sysconfig import get_paths
import sys

import sysconfig
python_include_dir = sysconfig.get_path('include')

module = Extension(
    "PyChess",
    sources=[
        "algorithms.c",
        "moveFunctions.c",
        "moveGeneration.c",
        "pychessmodule.c",

        "../src/tables/attackTables.c",
        "../src/tables/boardEvaluation.c",
        "../src/tables/magicBitboards.c",
        "../src/tables/transpositionTable.c",
        "../src/tables/zobristHashing.c",
    ],
    include_dirs=["../include", python_include_dir],
)

setup(
    name="PyChess",
    version="0.1",
    description="Python Chess engine module",
    ext_modules=[module],
)
