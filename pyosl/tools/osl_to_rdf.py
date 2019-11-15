import json

from . osl_encoder import _is_encodable_attribute
from . osl_encoder import SERIAL_VERSION
from pyosl import Property
import uuid
from requests.utils import requote_uri

NAMESPACE = 'http://esdoc-org/osl'


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

    def add_instance(self, instance):
        """ Add a pyosl instance"""
        klass = instance.__class__.__name__
        name = None
        if instance._osl.is_document:
            name = _make_name(klass, instance._meta.id)
            # TODO add document attributes to triples
        else:
            for key in ('uid', 'id', 'name'):
                val = _getval_if_exists_and_set(instance, key)
                if val:
                    name = _make_name(klass, val)
                    break
        if not name:
            # blank node then
            name = f'_:{uuid.uuid4()}'
            self.triples.append((name, 'rdf:type', 'rdf:Bag'))

        self.triples.append((name, 'rdf:type', klass))

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
                    self.add_instance(val)

                # ... simple types;
                elif val is not None:
                    self.triples.append((name, key, val))

            # Encode iterables:
            else:
                if len(val) > 0:
                    # ... string types;
                    if isinstance(val, str):
                        self.triples.append((name, key, val))
                    # ... collections;
                    else:
                        # Assume ordered, we can't know ...
                        blank_name = f'_:{uuid.uuid4()}'
                        self.triples.append((name, key, blank_name))
                        self.triples.append((blank_name, 'rdf:type', 'rdf:Seq'))
                        for n, v in enumerate([_value(j) for j in val]):
                            predicate = f'rdf:_{n}'
                            if hasattr(v, '_osl'):
                                self.triples.append((blank_name, predicate, self.add_instance(v)))
                            else:
                                self.triples.append((blank_name, predicate, v))

        return name

    def __repr__(self):
        """ String representation"""
        return '\n'.join([str(i) for i in self.triples])








