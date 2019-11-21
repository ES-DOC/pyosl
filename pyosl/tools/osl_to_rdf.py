import json

from . osl_encoder import _is_encodable_attribute
from . osl_encoder import SERIAL_VERSION
from pyosl import Property
import uuid
from requests.utils import requote_uri

NAMESPACE = 'http://esdoc-org/osl'

MAPPING = {
    str: 'http://www.w3.org/2001/XMLSchema#string',
    bool: 'http://www.w3.org/2001/XMLSchema#boolean',
    int: 'http://www.w3.org/2001/XMLSchema#integer',
    float: 'http://www.w3.org/2001/XMLSchema#ifloat'
}


def literal(v):
    """ Annotate builtin literals with datatypes."""
    key = type(v)
    if key in MAPPING:
        return f'{v}^^{MAPPING[key]}'
    else:
        raise ValueError(f"Unexpected builtin type {key} ({v})")


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


class Triples:
    """ Lightweight RDF encoder"""

    def __init__(self, instance, include_metadata=False):
        self.triples = []
        self.include_metadata = include_metadata
        if self.include_metadata:
            raise NotImplementedError("Code for including document metadata doesnt't exist yet")
        self.add_instance(instance)
        
    def add_triple(self, triple):
        if triple not in self.triples:
            self.triples.append(triple)

    def add_instance(self, instance):
        """ Add a pyosl instance"""
        klass = instance.__class__.__name__
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
                    self.add_triple((name, key, literal(val)))

            # Encode iterables:
            else:
                if len(val) > 0:
                    # ... string types;
                    if isinstance(val, str):
                        self.add_triple((name, key, literal(val)))
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
                                self.add_triple((blank_name, predicate, literal(v)))

        return name

    def __repr__(self):
        """ String representation"""
        return '\n'.join([str(i) for i in self.triples])








