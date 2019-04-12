## Some History ##

This activity grew out of a sequence of European funded activities which aimed at documenting climate models and their workflow. Key to that activity was a "Common Information Model" or CIM.  

In the beginning, the CIM was defined using three architectural layers and a vocabulary layer. The three architectural layers were:

 * The "CIM Metamodel", that is, a set of rules of how we would use UML to define the CIM.
 * The Conceptual CIM (ConCIM), that is, the CIM defined in UML using the CIM metamodel, and
 * The Application CIM (ApCIM), that is, the implementation of the UML using XML schema, which allowed actual CIM documents (in XML) to be validated against XSD representations of the CIM.

The vocabulary layer effectively treated one particular (the Model) CIM document as a special case, by defining a set of nested component descriptions each of was effectively a set of (key, value, docstring)  properties and a list of possible sub-components defined in the same way. This allowed "standardised" comparison of models since they all used the same structure of components and property keys.

These prescribed lists of components and their possible properties were defined in mind-maps, and machinery was built to (effectively) take these definitions and populate XML documents which needed only to be completed by adding the various values to the properties in the trees of components.

Machinery was developed to exploit these XML documents which depended on a python rendering of the XSD content, and then allowed CIM documents to be instantiated in more than just XML, using (amongst other things) python objects to instantiate CIM documents. In essence, this pythonic representation implemented the ApCIM. The pythonic representation has been (pre 2016) known as *the* "mp" formalism, since it formed part of the es-doc [metaprogramming](https://github.com/ES-DOC/esdoc-mp) framework.

In practice, the esdoc meta-programming framework has all the conceptual parts required to define any CIM, there is

 * A metamodel, which is implicit in the rules used to define what may appear in the schema definitions used in the metaprogramming framework,
 * A conceptual model, consisting of the schema definitions (e.g., [CIM1.5](https://github.com/ES-DOC/esdoc-mp/tree/master/esdoc_mp/schemas/cim/v1)) themselves, and 
 * Multiple application instances produced by using the esdoc-mp software to produce a python class instances - e.g. [CIM1.5](https://github.com/ES-DOC/esdoc-py-client/tree/master/pyesdoc/ontologies/cim/v1) - capable of being imported and used to create, manipulate, and render CIM instances.

## Current State ##

As part of the development of a second version of the CIM ([CIM2](https://github.com/ES-DOC/es-doc-cim2-schema)), a de facto decision was taken to move the primary CIM representation into the pythonic representation based on the existing mp framework. 

Of necessity the mp framework evolved, in part because of new requirements from CIM2, and in part because of a blurring of concerns between the concepts of metamodel, ApCIM, and ConCIM. This blurring could have been further compounded by a decision to use the same mp framework to define the vocabularies - since they were *effectively* specialisations of the core components. However, for CIM2,  a different choices was made:  to *actually* make the extensions real specialisations, but with all the specialisations outside of the CIM2 schema itself, using a separate metamodel for describing them, with supporting software. 

Even within CIM2 itself, we can now consider three specific conceptual layers. We still have a metamodel, a set of CIM2 definitions, and a programming framework. While most of this is actively quite generic, the programming framework evolved to be the "CIM2 CMIP6 programming framework", so this package includes some simplified [machinery](machinery.md) which is aimed at:

1. Supporting _Ontology design_ ([uml tooling](uml_tooling.md)), and 
2. Providing a [simple example](simple_examples.md) of how to build tools which utilise it.

How an ontology can be designed and used by the tools is documented in

 * the [metamodel](metamodel.md) description,
 * exactly how python is used to [define](definitions.md) the vocabulary contents within files, and 
 * the [layout](layout.md) needed for the [software machinery](machinery.md) to work.