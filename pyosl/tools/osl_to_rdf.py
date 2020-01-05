import json

from . osl_encoder import _is_encodable_attribute
from . osl_encoder import SERIAL_VERSION
from pyosl import Property
import uuid
from requests.utils import requote_uri
from rdflib import Graph, URIRef, RDF, BNode, Literal

NAMESPACE = 'http://esdoc-org/osl'

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

        # a list of tuples of the form target (id, name, relationship)
        self.external_esdoc_references = []

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
            self._add_reference(instance)
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

    def _add_reference(self, doc_reference):
        """
        Parse a doc_reference instance, and if available, add esdoc reference to internal list of references
        :param doc_reference:
        :return:
        """
        try:
            assert doc_reference.__class__.__name__ == "shared.doc_reference"
        except AssertionError or AttributeError:
            raise ValueError(f"Argument to _add_reference is not a pyosl doc_reference instance {doc_reference}")
        if doc_reference.id:
            self.external_esdoc_references.append((doc_reference.id, doc_reference.name, doc_reference.relationship))


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
    def __init__(self):
        """ Initialise with a choice of whether or not to include internal osl metadata"""
        super().__init__()
        self.g = Graph()
        self.resource_space = 'https://es-doc.org/resources/'
        self.type_space = 'https://es-doc.org/types/'

    def add_triple(self, triple):
        """" Need to encode triple using the proper RDFlib classes"""
        self.g.add(triple)

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

        # Setup Node
        klass = instance.__class__.__name__
        q_klass = URIRef(self.type_space + klass)
        # All documents are resources
        if instance._osl.is_document:
            for key in ('id', 'uid'):
                val = _getval_if_exists_and_set(instance._meta, key)
                if val:
                    node = URIRef(self.resource_space+val)
                    self.add_triple((node, RDF.type, q_klass))
                    break
            if not val:
                # A document which has no uid, bad, bad behaviour
                raise ValueError(f"RDF Encoding problem\n[[{instance}]]\n[[Malformed document has no ID]]")
        else:
            if klass == 'shared.doc_reference':
                self._add_reference(instance)
            # Literal of some sort
            node = BNode()
            self.add_triple((node, RDF.type, q_klass))

        for key, val in instance.__dict__.items():
            # Escape private/magic properties, except for the osl private metadata which we do want to encode
            if not _is_encodable_attribute(key):
                continue

            rdfkey = URIRef(self.type_space + klass + '/' + key)
            # Process iterables / non-iterables differently.
            try:
                iter(val)
            # Encode non-iterables:
            except TypeError:
                v = self._value(val)
                if self._value(val):
                    self.add_triple((node, rdfkey, v))

            # Encode iterables:
            else:
                if len(val) > 0:
                    # ... string types;
                    if isinstance(val, str):
                        self.add_triple((node, rdfkey, Literal(val)))
                    # ... collections;
                    else:
                        bag = BNode()
                        self.add_triple((node, rdfkey, bag))
                        for v in val[0:1]:
                            self.add_triple((bag, RDF.first, self._value(v)))
                        for v in val[1:]:
                            self.add_triple((bag, RDF.next, self._value(v)))

        return node

    def _value(self, entity):
        """ Return an RDF encode-able value for an instance"""
        if isinstance(entity, Property):
            return self._value(entity.value)
        elif hasattr(entity, '_osl'):
            return self._get_entity(entity)
        else:
            if entity:
                return Literal(entity)
            else:
                return entity

    def __repr__(self):
        return self.g.serialize(format='turtle')




