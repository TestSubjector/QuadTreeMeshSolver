#!python
#cython: language_level=3

from distutils.core import setup
from distutils.extension import Extension
import numpy

from Cython.Build import cythonize
from Cython.Compiler import Options

Options.annotate = True


extensions = [Extension("core", ["core.pyx"],
            include_dirs=[numpy.get_include()]),
        ]
extensions = cythonize(extensions)

setup(
    name = "Core Python for Quadtree",
    ext_modules = extensions
)