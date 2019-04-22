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
f._osl.name='Fred'
print (f._osl.is_document, f._osl.name)

``` 

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

It will be seen in the examples to come, that much more functionality
can be built on these simple types.

#