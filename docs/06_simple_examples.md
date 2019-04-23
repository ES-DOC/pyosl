#### Simple Example

The `mp_base.py` and `mp_property.py` modules provide the necessary core functionality for extending 
OntoBase class to support making instances fully respect class properties, so that 

1. instances respects the `pstr` property,
1. instances of documents have document metadata, 
1. instances can be compared, and
1. instances of classes have typed attributes from the ontology.

The first three of these are implemented by methods in the ``Base`` class. The fourth
is achieved by ensuring that where a class has a property definition of the form:

```("name", "target", "cardinality", "docstring")```

instances of that class not only have an attribute of `name`, but attempts to assign
values to that attribute are forced to ensure that the value is of type `target` 
(or an appropriate substition such as `nil_reason` or for documents, `doc_reference`)
and that the cardinality is respected.

This enforcement of property typing, which is not normal in Python - which normally 
prefers [duck typing](https://en.wikipedia.org/wiki/Duck_typing) - is included since 
experience has shown that in using metadadta sourced from scientists in full stack work 
with  serialisation and deserialisation with html and pdf views it is simpler to enforce 
typing at source (to be specific, something might pass quite a long way along, quacking
happily until it reaches a point where some extra method/property/attribute is expected
but not available, and this may be a very long way from the source - in another
repository for example).

Enforcing `pstr`, document metadata,  and equality is achieved by a simple subclass of `OntoBase` - `Base`, 
and the property typing is enforced by one further function of the core factory: 
the `add_descriptor` method, which supports binding a user defined property class to all the
pyosl attributes via a user defined descriptor class. 

The set up for this functionality is simple:

```python
from factory import Factory, Ontology
from mp_base import Base
from mp_property import Property, PropertyDescriptor

o = Factory
o.register(Ontology(Base))
o.add_descriptor(PropertyDescriptor, Property)
```

and now all use of the factory `build` method using `o` will build instances which fully
respect the pyosl property definitions in the source ontology. These instances can be used
throughout the tool chain, especially when they are further enhanced to support
[serialisation and deserialisation](07_serialisation.md).



