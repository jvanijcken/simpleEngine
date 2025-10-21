from setuptools import setup, Extension

module = Extension('PyChess', sources=['pychess.c'])

setup(
    name='PyChess',
    version='1.0',
    ext_modules=[module],
)