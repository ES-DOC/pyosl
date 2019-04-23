#### UML Code - an example of exploiting the Ontology Machinery

The code which underpins the UML tools is a simple extension to the basic `Ontology, Factory` machinery.

The key is that instead of using the base factory to build instances of the `OntoBase` class, the UML
code creates a subclass of `OntoBase`  called `UmlBase` (in `uml_base.py`), and the factory 
can then be told to use that to build instances which know how to label themselves in an
appropriate way to be used in a UML diagram.

The code to do this makes use of the `register` method of the factory class:

```python
from factory import Factory, Ontology, OntoBase

class UmlBase(OntoBase):
    """ UML machinery"""
    def label(self):
        """ return a UML label for a particular class"""
        ...
    
Factory.register(Ontology(UmlBase))
```

and the UML tools make use of this functionality.


#### Using the UML tools


There are two basic UML tools availble: `BasicUML` and `PackageUML`. The latter provides 
a view of the entire ontology via package lists. The former provides flexibility for
a range of UML views of selected content.

_**TODO** Add examples of usage... meanwhile, check out the unit tests_

