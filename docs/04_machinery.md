## Core Metaprogramming tools

The core metaprogramming tools are the `Ontology` and `Factory` classes that can be imported 
from the `factory.py` module.

These provide the machinery both to build python object instances of the ontology's classes, but also
the scaffolding to build more bespoke tools which use those classes.

The most important task is to connect the basic Ontology class to the python
definitions, wherever they lie. This is achieved by ensuring that the 
`PYOSL_CONFIG` environment variable is set to the location of the `pysol configuration.ini`
file.

_**TODO**: Currently the code only looks for the configuration.ini file in the same place
as the factory.py class and ignores any environment variable._

The configuration.ini file must point to the location of the parent directory of the 
python classes or the appropriate pip installed package.

_**TODO**: Add the appropriate example_

#### Using the core tools

The core tools simply build the instances, and populate an attribute of each instance with 
a private attribute `_osl` which itself holds the ontology definitions, e.g.

```python
from factory import Factory
 
f = Factory()
klass = 'designing.numerical_requirement'
instance = f.build(klass)
instance._osl.name='Fred'
print (instance._osl.is_document, instance._osl.name)

``` 

The underlying code here makes all classes and enums instances of the ``OntoBase`` class.

The factory also includes a validator for checking to see if any specific
instance is an acceptable value for a particular property attribute. This 
validator adds some additional functionality over the standard python
`is_instance` method, because not only can any linked_to property target
be an instance of `doc_reference` or the actual property_target type, but 
any property target can also be an instance of `nil_reason`. 


An example of the use of the core validator is ensuring
that an instance of _temporal_constraint_ is in fact an instance
of a _numerical_requirement.

```python
from factory import Factory

f = Factory()
eg_tc = f.build('designing.temporal_constraint')
assert f.core_validator(eg_tc, 'designing.numerical_requirement') == True

```

In addition to the `build` and `core_validator` methods, the factory also two more 
important methods which provide extensibility:

1. a `register` method that can be used to change the base class used for 
the Ontology, and
2. an `add_descriptor` method which can bind pyosl attributes to specific properties.

These methods provide the extensibility to allow designers to use pyosl to develop their
own tooling. Two simple examples are provided

 - the [UML tooling](05_uml_tooling.md) makes use of the register functionality to build
 tools to help design and understand an ontology, and 
 - the [the simple extension example](06_simple_examples.md) makes use of both methods
 to provide tools for using the ontology to manipulate information.

