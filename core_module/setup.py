from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension

from Cython.Build import cythonize
extensions = [Extension("core", ["core.pyx"])]
extensions = cythonize(extensions)

setup(
    name = "Core Python for Quadtree",
    ext_modules = extensions
)