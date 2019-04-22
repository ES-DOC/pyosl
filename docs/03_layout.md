### Defining an Ontology - Layout of Files

The ontology is [defined](definitions.md) in files. In this section we describe how these files need to be organised on disk. 

The idea here is that we support both direct editing of the ontology on disk, and the use of the python code sharing machinery for community use. To do that, the ontology needs to be  "pip installable", so that when the ontology is ready to go (and has been appropriate [registered](https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives), it can be made available to anyone via

`pip install "ontology name"`

*__TODO__: Actually we need to add the code to support either local directory or pip, but that will be straight forward.*

All ontologies will consist of `packages`, `classes` and `enums`.

`packages` are a convenient way of organising `classes`  and `enums` into themes, which both allows classes with the same name in different contexts, and provides isolation to allow work on all the classes and enums relevant to one part of the problem at a time.

* Each package consist of one or more python source files.
	 * For a small package, one  file is sufficient, and it might contain both classes and enums. There is no naming convention for these files, but it is sensible to name this file with the package name. For example, for a _small_ "time" package, one might have a small "time.py" file containing  all the necessary classes  and enums.
	* With multiple files, it is recommended that the file is called something useful which explicitly indicates the relationship to the package and the structural reason for the file split. For example with a large "time" package, one might have a "time\_classes.py" and a "time\_enums.py".  An even larger package might have multiple class or enum files, with meaningful names delineating what appears where.
* All the package definition files are organised into one common  directory, with an `__init__.py`file which makes the formal link between the packages and the files. 

The `__init__.py` has three functions. It is necessary to:

1. Support the python machinery,
2. Make the link between files and packages, and
3. Provide ontology metadata (name, version, documentation).

The mere presence of an `__init__.py` file (regardless of content) achieves most of the first purpose, but the machinery requires specific content for the second two functions to work. For this.

* Each file containing ontology content must be explicitly imported, and their relationship to the package is via a package definition statement which returns a set of the relevant modules. For example:

```python
import . time_classes
import . time_enums

def time():
	""" Set of types for describing and manipulating time """
	return { time_classes, time_enums }
```
*__TODO__ Consider whether relative imports really are the right thing here.*

If there is only one file in a package, it is important not to mangle the package and the source file since they could share the same name. This is easy to handle using the "import ... as" notation, for example, with that hypothetical small itme package:

```python
import . time as time_types

def time():
	""" Set of types for describing and manipulating time """
	return { time_types }
```

Ontology metadata appears in the __init__ file, with three mandatory pieces of information:

```python

# Ontology name.
NAME = 'the ontology name'

# Ontology version.
VERSION = 'X.Y.Z'

# Ontology doc string.
DOC = """ 
As much information  in one place about the scope and
intention of the ontology as is appropriate. 

It could be a short reference to a paper, or a lengthy exposition right here.
"""

```

A complete example appears in the TEST ontology.

*__TODO__: Need to add a test ontology and change the unit tests to use it*



