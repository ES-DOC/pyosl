import json

from . osl_encoder import _is_encodable_attribute
from . osl_tools import get_reference_for
from . osl_encoder import SERIAL_VERSION
from pyosl import Property
import uuid
from requests.utils import requote_uri
from rdflib import Graph, URIRef, RDF, BNode, Literal

NAMESPACE = 'http://esdoc-org/osl'
DEBUG = True

MAPPING = {
    str: 'http://www.w3.org/2001/XMLSchema#string',
    bool: 'http://www.w3.org/2001/XMLSchema#boolean',
    int: 'http://www.w3.org/2001/XMLSchema#integer',
    float: 'http://www.w3.org/2001/XMLSchema#ifloat'
}


def _getval_if_exists_and_set(instance, attribute):
    """ Return value of attribute if it exists, or none"""
    if hasattr(instance, attribute):
        return getattr(instance, attribute)
    else:
        return None


def _make_name(k, v):
    """ Create a fully qualified name given klass k, and name v"""
    return requote_uri(f'{NAMESPACE}/{k}/{v}')


def _value(entity):
    if isinstance(entity, Property):
        return entity.value
    else:
        return entity


class CoreRDF:
    """ Mixin interface class for core RDF functionality for one graph."""

    def __init__(self):
        """
        Instantiate an RDF Graph or repository
        :param instance: An initial pyosl instance to be serialised as RDF.
        """

        # External entities (documents via doc_reference, and online resources)
        self.online_resources = {}  # keyed by linkage
        self.documents_referenced = {}  # keyed by id

    @property
    def external_esdoc_references(self):
        """A list of tuples of the form target (id, name, relationship)"""
        return [(v.id, v.name, v.relationship) for v in self.documents_referenced.keys()]

    @property
    def external_resources(self):
        """ A list of online resource linkages"""
        return self.online_resources.keys()

    def _collect_external(self, entity):
        """
        Parse an entity and if it is one of "shared.doc_reference" or "shared.online_resource", check if unique,
        and collect if it is and return True, if not, return False.
        """
        klass = entity.__class__.__name__
        if klass in  ["shared.doc_reference", "shared.online_resource"]:
            key_name = {'shared.doc_reference':'id', 'shared.online_resource':'linkage'}
            repo = {'shared.online_resource':self.online_resources,
                          'shared.doc_reference':self.documents_referenced}[klass]
            key = getattr(entity, key_name[klass])
            if key in repo:
                return False
            else:
                repo[key] = entity
        return True

    def add_triple(self, triple):
        """
        Add a new triple to the graph or repository
        :param triple: A tuple, the first element of which must be unique within the graph/repository
        :return:
        """
        # Must be implemented by sub-classes
        raise NotImplementedError

    def add_instance(self, instance):
        """
        Add a new instance (including all composed attributes as additional triples).
        Include all document links as doc_reference triples.
        Return a list of URIs from any document references which provide them.
        :param instance:
        :return: references: a list of URIS for esdoc entities which are linked to this instance.
        """

        klass = instance.__class__.__name__
        if klass == 'shared.doc_reference':
            self._collect_external(instance)
        name = None
        for key in ('uid', 'id', 'name'):
            val = _getval_if_exists_and_set(instance, key)
            if val:
                name = _make_name(klass, val)
                break

        if not name:
            # blank node then
            name = f'_:{uuid.uuid4()}'
            self.add_triple((name, 'rdf:type', 'rdf:Bag'))

        self.add_triple((name, 'rdf:type', klass))

        if instance._osl.is_document:
            self.add_triple((name, 'rdf:parseType', 'resource'))

        for key, val in instance.__dict__.items():
            # Escape private/magic properties, except for the osl private metadata which we do want to encode
            if not _is_encodable_attribute(key):
                continue

            val = _value(val)
            # Process iterables / non-iterables differently.
            try:
                iter(val)

            # Encode non-iterables:
            except TypeError:
                # ... osl types

                if hasattr(val, '_osl'):
                    target = self.add_instance(val)
                    self.add_triple((name, key, target))

                # ... simple types;
                elif val is not None:
                    self.add_triple((name, key, self._literal(val)))

            # Encode iterables:
            else:
                if len(val) > 0:
                    # ... string types;
                    if isinstance(val, str):
                        self.add_triple((name, key, self._literal(val)))
                    # ... collections;
                    else:
                        # Assume ordered, we can't know ...
                        blank_name = f'_:{uuid.uuid4()}'
                        self.add_triple((name, key, blank_name))
                        self.add_triple((blank_name, 'rdf:type', 'rdf:Seq'))
                        for n, v in enumerate([_value(j) for j in val]):
                            predicate = f'rdf:_{n}'
                            if hasattr(v, '_osl'):
                                self.add_triple((blank_name, predicate, self.add_instance(v)))
                            else:
                                self.add_triple((blank_name, predicate, self._literal(v)))

        return name

    def _literal(self, v):
        """ Annotate builtin literals with datatypes."""
        key = type(v)
        if key in MAPPING:
            return f'{v}^^{MAPPING[key]}'
        else:
            raise ValueError(f"Unexpected builtin type {key} ({v})")


class Triples (CoreRDF):
    """ Lightweight RDF encoder"""

    def __init__(self):
        super().__init__()
        self.triples = []
        
    def add_triple(self, triple):
        if triple not in self.triples:
            self.triples.append(triple)

    def __repr__(self):
        """ String representation"""
        return '\n'.join([str(i) for i in self.triples])


class Triples2(CoreRDF):
    """ RDF triples using rdflib for a triple store"""
    def __init__(self, collect_semantic_triples=True, skip_meta=True):
        """ Initialise graph and list of internal linkages,
        optionally flag desire to collect semantic triples as well.
        (semantic triples? for pyosl plotting)"""
        super().__init__()
        self.g = Graph()
        self.resource_space = 'https://es-doc.org/resources/'
        self.type_space = 'https://es-doc.org/types/'
        self.objects = {}
        self.semantic_nodes = {'shared.doc_reference': [],
                               'shared.online_resource': [],
                               'other_osl': []}
        self.semantic_triples = []
        self.go_semantic = collect_semantic_triples
        self.skip_meta=skip_meta

    def _check_add_external(self, entity):
        """ Add an external entity if necessary"""
        klass = entity.__class__.__name__
        assert klass in ["shared.doc_reference", "shared.online_resource"]
        key_name = {'shared.doc_reference': 'id', 'shared.online_resource': 'linkage'}
        key = getattr(entity, key_name[klass])
        if key in self.objects:
            return True, self.objects[key][1]
        else:
            self.objects[key] = [entity, URIRef(key)]
            if self.go_semantic:
                self.semantic_nodes[klass].append(str(entity))
            return False, self.objects[key][1]

    def add_triple(self, triple):
        """" Need to encode triple using the proper RDFlib classes"""
        self.g.add(triple)

    def add_semantic(self,triple):
        """ Add a semantically meaningful triple """
        s, p, o = triple
        if hasattr(o, '_osl'):
            self.semantic_triples.append((str(s), p, str(o)))

    def add_instance(self, instance):
        """
        Add a new instance (including all composed attributes as additional triples).
        Include all document links as doc_reference triples.
        Return a list of URIs from any document references which provide them.
        :param instance:
        """
        node = self._get_entity(instance)
        return self.external_esdoc_references

    def _get_entity(self, instance):
        """

        :return: entity: a suitable object for an RDFlib triple
        :return: references: a list of URIS for esdoc entities which are linked to this instance.
        """

        # Five interesting types of instances to deal with:
        # 1: documents
        # 2: doc_references - links to documents (singular, so don't repeat the document description)
        # 3: references to real resources that aren't documents: online_resources
        # 4: other osl types
        # 5: everything else

        # Setup Node
        klass = instance.__class__.__name__
        q_klass = URIRef(self.type_space + klass)
        noderef = None
        # All documents are resources
        if instance._osl.is_document:
            for key in ('id', 'uid'):
                val = _getval_if_exists_and_set(instance._meta, key)
                if val:
                    # have we seen it before?
                    object_key = self.resource_space+val
                    if object_key in self.objects:
                        return self.objects[object_key][1]
                    else:
                        node = URIRef(object_key)
                        self.objects[object_key] = [instance, node]
                        if self.go_semantic:
                            noderef = get_reference_for(instance)
                            self.semantic_nodes['shared.doc_reference'].append(str(noderef))
                    self.add_triple((node, RDF.type, q_klass))
                    break
            if not val:
                # A document which has no uid, bad, bad behaviour
                raise ValueError(f"RDF Encoding problem\n[[{instance}]]\n[[Malformed document has no ID]]")
        elif klass in ['shared.doc_reference', 'shared.online_resource']:
            already_seen, node = self._check_add_external(instance)
            if already_seen:
                return node
            else:
                self.add_triple((node, RDF.type, q_klass))
                noderef = instance
        else:
            # pyosl literal of some sort
            node = BNode()
            self.add_triple((node, RDF.type, q_klass))

        for key, val in instance.__dict__.items():
            # Escape private/magic properties, except for the osl private metadata which we do want to encode
            if not _is_encodable_attribute(key) or (self.skip_meta and key == '_meta'):
                continue

            rdfkey = URIRef(self.type_space + klass + '/' + key)

            # Process iterables / non-iterables differently.
            # Unlike generic serialisation, we only have lists as iterables, let's use that knowledge

            if isinstance(val, Property):
                val = val.value

            if not isinstance(val, list): # captures PropertyList too
                entity = self._value(val)
                if entity:
                    self.add_triple((node, rdfkey, entity))
                    if noderef and self.go_semantic:
                        self.add_semantic((instance, key, val))

            # Encode list items
            else:
                if len(val) > 0:
                    if DEBUG:
                        print('List Item ',rdfkey)
                    bag = BNode()
                    self.add_triple((node, rdfkey, bag))
                    for v in val[0:1]:
                        self.add_triple((bag, RDF.first, self._value(v)))
                    for v in val[1:]:
                        self.add_triple((bag, RDF.rest, self._value(v)))
                    if noderef and self.go_semantic:
                        for v in val:
                            self.add_semantic((instance, key, v))

        return node

    def _value(self, entity):
        """ Return an RDF encode-able value for an instance"""
        if isinstance(entity, Property):
            return self._value(entity.value)
        elif hasattr(entity, '_osl'):
            if self.skip_meta and entity.__class__.__name__=='_meta':
                return entity
            else:
                return self._get_entity(entity)
        else:
            if entity:
                return Literal(entity)
            else:
                return entity

    def __repr__(self):
        return self.g.serialize(format='turtle')




