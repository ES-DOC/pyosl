### The Metamodel
 
 
#### Classes, Enums and Documents

The metamodel for the activity was inherited straight from Metafor 
(Lawrence, et al. 2012). The base concept is that:

1. Information is structured into _classes_ and enumerations with attributes limited to strings, booleans, integers, floats, and other class or enumerations (_enums_) from within the ontology.
1. Classes an enums are broken up into packages to aid understanding.
1. Information will be created in, and managed via, discrete _documents_ each of which will have their 
own life cycle and versioning. Accordingly, the ontology defines the specific types of documents which are expected to be involved in a simulation workflow, e.g. we have "Experiment" documents  which describe what is intended to be done, and  "Model" documents which describe the scientific content of the software used. It is expected that  instances of each will be maintained and evolved by quite different communities.
1. Documents carry metadata to aid in the management of the documents, but which carry no scientific meaning. Such metadata should include authorship and versioning information.   
1. Each document has structure which is controlled by the ontology and which will be rendered in different  ways for different purposes (e.g. for web pages, or tables in pages).
1. Documents will be linked using an extended notion of a hyperlink - the _doc_reference_ - allowing navigation between documents as well as some summary information about the target to be rendered with the source  without resolving the link (although in many applications, a useful rendering will require a full resolution of a set of linked documents, e.g. see _bundles_ below).
1. It should be expected that documents are shared between individuals and repositories.
    
1. The basic ontology should be exensible, so that custom profiles can be built for particular projects.


#### Documents, Bundles and Repositories

The use of _documents_ in the core metamodel has implications for how content is created
and used.  In particular, it immediately introduces issues around creation, serialisation 
management, and rendering for consumption. For example, while it is desirable to manage entities such
as bibliographic content and people as independent documents, experience has shown that 
the machinery around document creation needs to hide as much of that as possible. Similarly,
the machinery for publishing documents (e.g. for websites or tables in papers), needs to 
extract the relevant content into rendered coherent views. 

In previous versions of the ontology, definitions included XML schema, and Atom feeds were 
mandated as the mechanism for publishing content for aggregation between documents and types.
Views were extracted as html documents which did not match the underlying document structure
directly. Ad hoc solutions to this "bundling" problem were developed.

The need to have a different concept of document for creation, viewing and publication remains, 
and so in order to minimise ad hoc solutions, the metamodel now explicitly includes the 
notions of _bundles_ and _repositories_ as well as _documents_, to support clearer information 
workflows. 

A _bundle_ is a serialised set of documents, where some (or all) _doc\_reference_ instances have  been replaced by a complete serialisation of the target document. The bundle may be
 
* _uninitialised_, in which case some or all of the documents do not include UIDs, since there may be a subsequent disambiguation step expected (e.g. the content has been parsed from a creator's spreadsheet, but the internal references need disambiguation or tentative links need to resolved to actual links), or
* _initialised_ in which case all the content includes unique identifiers for any documents, whether included as actual documents or referred to via  _doc\_reference_.
  
Any _repository_ of documents is expected to be be able to handle receiving and exporting either type of document, and ideally be able to carry out internal disambiguation and resolution to minimise exporting of uninitialised documents.

It should be clear that the metamodel says nothing about how serialisation should be carried out, whether for documents or bundles, or how repositories should be implemented.


 


