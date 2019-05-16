
### Application Profile

The vocabulary is fully defined by _classes_ and vocabulary lists (_enums_) organised in 
_packages_.

All classes should consist of a set of class properties,  a set of instance properties, and an 
optional set of constraints on those properties. All instances should be populated with appropriate 
values for those properties.

* Property definitions should include a name, property target types, 
the acceptable cardinality of the property, and documentation.
* "Appropriate" values may be `None` or `[]` for cardinalities of `0.1` and `0.N` respectively, and must
otherwise comply with the cardinality, and be instances of the property type, or in the case of property types which 
are documents, an instance of the `doc_reference` class, or for any value, an instance of the
special `nil_reason` class.
    * _nil_reason_ provides a way of explaining why a value is not present when one is required or 
    expected. 

All enums should consist of a set of enum properties, a set of values which satisfy the enumeration, 
and in an instance, an optional selection from that enumeration.

### Defining an Ontology in Python

We implement packages as simple python files, with each package fully defined by up to two files -  
one for classes, and one for enums (or just one file with both for the smaller packages). 
Both classes and and enums are defined using simple functions within the files.

Each _class_ is defined by a function which returns a dictionary with the following 
keys:

 * **type**: class
 * **base**: None or an \esdoc\ base class
 * **is\_abstract**: boolean
 * **pstr**: a simple format expression to indicate how an instance of the class may be named.
 * **properties**: a list of the class attributes (see below)
 * **constraints**: empty list, or if a subclass, a list of constraints which might be applied to base properties

Note the explict and easy support for inheritance via the base class attribute. 
Classes which describe documents have an additional attribute:

 * **is\_document**: True

which indicate that there are additional document metadata attributes 
(such as author, version number, last changed date etc, see table \ref{tab:docmeta}) 
associated with the class.

The enum vocabulary lists are similarly defined by functions which return dictionaries, 
which include three attributes: 

* **type**: enum
* **is\_open**: boolean
* **members**: a list of terms and definitions

If **is\_open** attribute indicates that users may substitute their own
values rather than be required to select from the enumeration.


#### Property Definitions and Constraints

All properties are defined with a four member tuple:

 * **property_name** (which may not begin with a "_") - the name of the class property,
 * **property target** - the type of the class property 
 * **cardinality**  - one of ("0.1", "1.1", "0.N", "1.N")
 * **documentation string** - a short description of the property (e.g. suitable for a tooltip in a GUI).
  
The project class shows a number of important characteristics of class and property definitions, 
as well as introducing a simple constraint:

```python
def project():
    """Describes a scientific project.

    """
    return {
        'type': 'class',
        'base': 'activity.activity',
        'is_abstract': False,
        'properties': [
            ('homepage', 'str', '0.1',
                "Project homepage."),
            ('objectives', 'str', '0.N',
                "Project objectives."),
            ('previous_projects', 'linked_to(designing.project)', '0.N',
                "Previous projects with similar aims."),
            ('required_experiments', 'linked_to(designing.numerical_experiment)', '0.N',
                "Experiments required to deliver project."),
            ('governed_experiments', 'linked_to(designing.numerical_experiment)', '0.N',
                "Experiments governed by this project."),
            ('sub_projects', 'linked_to(designing.project)', '0.N',
                "Activities within the project with their own name and aim(s).")
        ],
        'constraints': [
            ('cardinality', 'description', '1.1')
        ]
    }

```
This example shows the project class, which is a sub-class of an _activity_ class, and because
of that, it is necessarily managed as a standalone document (_activity_ carries the attribute
``` is_document: True```).

There are three different types of property targets, two of which are shown in this example

 1. builtin types - str, int, float, datetime,
 1. other ontology classes or enums, or 
 1. documents, themselves being of one or another class within the ontology.  
 
Document links are "stereotyped" with the "linked\_to" notation.
 
This examples also shows a simple constraint on a property inherited from the base class, 
 in this case the  _description_ property from _activity_.
 (The _name_ property of the _activity_ base class also has cardinality of "1.1", and so name 
 and description are the minimal requirements for describing a project.)
 
If the linked_to attributes are provided, then they will normally (see the 
 [discussion on bundles](01_metadata#Documents, Bundles and Repositories)) be "represented" 
 by an instance of the _doc\_reference_" class.
 
 
 
