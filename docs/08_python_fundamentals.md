#### Python Fundamentals

The way that Python can use properties and descriptors is not familiar to many of us, in particular,
those of us who have come to Python without in-depth training in Python.

We make use of two less-well known pieces of Python technology: descriptors and properties.  

A full example of why one might want to use descriptors (and an explanation of some of the details we use) can be found in an excellent  [online post by Chris Beaumont](https://nbviewer.jupyter.org/urls/gist.github.com/ChrisBeaumont/5758381/raw/descriptor_writeup.ipynb). However, the bottom line is that we use properties to manage access to class attributes, and we use descriptors to manage properties in a reusable way.


Properties provide a way of ensuring that any attempt to change the state of an instance attribute 
(e.g. for a class instance, `f`, something like`f.x=2` ) have to go 
through a `__set` method, which can enforce any type of validation on the right hand side (e.g. to
make sure `x` can only be an integer).


A small working example of how we use descriptors appears in [this python file](python_underpinning.py),
which demonstrates how we use static methods to bind descriptors for attributes (`x` and `y`) to a 
class definition (`Foo`), and use the attribute labels (again, in this case `x` and `y`) as arguments
in the descriptor set up so that the properties can be inserted into the instance dictionaries using
their attribute labels.


We could probably avoid the use of properties given we have descriptors, but for now, we use them to
do the validation against the attribute definitions. A complete working example of how this is done
appears in one of the unit tests (`test_basic_idea.py`). In that test, we use the full PYOSL
property and descriptor magic to work through how this is useful.

__An explanation of `test_basic_idea.py`__

Firstly, we create a really simple ontology consisting of two classes: squares and circles, which share a base property (they belong to the "toy test ontology") but have differing
properties (`name` and `side_length`, and `name` and `radius`, respectively). They are defined using a cut down version
of the method returns dictionary structure we use for pyosl.

We bind these together into a simple `Ontology` class, which 
declares its constituent classes via the `available` attribute, which exposes the ontology dictionary values.

The secret sauce is how we handle the properties which differ between class instances - the side_length and radius - by using a validator method (`cheap_validator`) to ensure that they are always integers (as defined  by the target part of their definition strings (which are of the form `(attribute_name, target_type, cardinality, doc_string)`, just like in the main pyosl.

In this example, our Factory class is used to build instances
of circles and squares, and in the build, makes sure
that the classes each have a `PropertyDescriptor` class associated with each of the properties.

The PropertyDescriptor conforms to the signature of a Python Descriptor, but when we look into the code, we see that it extracts the attribute name from the definition and uses it
as a label just like in our simple example above.

It binds a Property instance to each property, and if you look carefully at the `__set` method in Property you can see the code checking cardinality, then type via the validator (how lists are handled is left as an exercise for the reader).

It is important however to note that it is the calling code that defines the validator used by the Property. Note in the `setUp` method of the `TestCase` in `test_basic_idea.py` how the statement `Property.set_validator(cheap_validator)` uses a static method of `Property` to ensure that all instances of the Property class will use that validator.

In normal use of pyosl, the default factory validator is used unless it is over-ridden by the user (which would not be expected in normal use), and so this step is not necessary - it is included here to show how it all works.



