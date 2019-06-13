from distutils.core import setup
import os
import re
import fnmatch

def find_package_data_files(directory):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, '*'):
                filename = os.path.join(root, basename)
                yield filename.replace('pyosl/', '', 1)

def _read(fname):
    """Returns contents of a file.
    """
    fpath = os.path.dirname(__file__)
    fpath = os.path.join(fpath, fname)
    with open(fpath, 'r') as file_:
        return file_.read()

def _get_version():
    """Returns library version by inspecting pyosl/__init__.py file.
    """
    return re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                     _read("pyosl/__init__.py"),
                     re.MULTILINE).group(1)


long_description = """
Python based ontology specification language, with tools
========================================================

The Python Ontology Specfication Lanaguage (pyosl) provides the documentation and implementation
of a methodology, with tools, for manipulating an ontology expressed in python according to a
metamodel documented in this package.

It should be used with one or more ontologies, defined in python as described in the 
documentation, and identified via the configuration.

"""

setup(name = "pyosl",
      long_description = long_description,
      version      =  _get_version(),
      description  = "TODO",
      author       = "Bryan Lawrence",
      maintainer   = "Bryan Lawrence",
      maintainer_email = "bryan.lawrence@ncas.ac.uk",
      author_email = "bryan.lawrence@ncas.ac.uk",
      url          = "https://ncas-cms.github.io/pyosl",
      download_url = "https://pypi.org/project/pyosl/#files",
      platforms    = ["Linux", "MacOS", "Windows"],
      keywords     = ['metadata', 'science', 'simulation', 'ontology',
                      'oceanography', 'meteorology', 'climate'],
      classifiers  = ["Development Status :: 4 - Beta",
                      "Intended Audience :: Science/Research", 
                      "License :: OSI Approved :: MIT License", 
                      "Topic :: Software Development",
                      "Topic :: Scientific/Engineering",
                      "Operating System :: OS Independent",
                      "Programming Language :: Python :: 3",
                      ],
      packages     = ['pyosl',
                      'pyosl/uml',
                      'pyosl/test',
                      ],
      package_data = {'pyosl': ['etc/*.ini']},
)
