import json

from pyosl import Property
from .osl_tools import get_reference_for


SERIAL_VERSION = 'json by osl_encode V0.2'


def _is_encodable_attribute(name):
    """Returns flag indicating whether an attribute is encodable.
    """
    if name == '_meta':
        return True
    elif name.startswith("_") or name.startswith("__") or name == "ext":
        return False
    else:
        return True


def osl_encode(doc, shard_to_bundle=False):
    """Encodes an osl instance (whether a full doc, or a part there-of).
    :param doc: Content being encoded.
    :type doc: osl object
    :returns: An encoded document representation.
    :rtype: dict
    """
    obj = dict()
    bundle = []

    def _value(entity):
        if isinstance(entity, Property):
            return entity.value
        else:
            return entity

    for key, val in doc.__dict__.items():
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
                obj[key], docs = osl_encode(val, shard_to_bundle)
                if docs:
                    bundle += docs
              
            # ... simple types;
            elif val is not None:
                obj[key] = val

        # Encode iterables:
        else:
            if len(val) > 0:
                # ... string types;
                if isinstance(val, str):
                    obj[key] = val
                # ... collections;
                else:
                    results = [osl_encode(i) if hasattr(i, '_osl') else i for i in [_value(j) for j in val]]
                    obj[key] = []
                    for r in results:
                        if len(r) == 0:
                            # not a pyosl type
                            obj[key].append(r)
                        else:
                            # pyosl type, if sharded, did we get documents?
                            obj[key].append(r[0])
                            if r[1]:
                                bundle.append(r)

    # Inject type info to simplify decoding.
    # We could use _osl, but that would be excessive duplication in output.
    klass = doc.__class__.__name__
    if klass != "shared.doc_meta_info":
        if '_meta' not in obj:
            obj['_meta'] = {}
        obj['_meta']['type'] = doc._osl.type_key
        obj['_meta']['source_key'] = SERIAL_VERSION
        print(klass, obj['_meta']['type'])
    if doc._osl.is_document and shard_to_bundle:
        bundle = [obj,] + bundle
        dr_obj = get_reference_for(doc)
        obj, ignore = osl_encode(dr_obj, False)

    return obj, bundle


def osl_encode2json(obj):
    """ Given an instance of an OSL document, encode into json. Optionally """

    content, bundle = osl_encode(obj, False)
    # encoding should not bundle!
    assert bundle == []

    return json.dumps(content)


def bundle_instance(obj):
    """ Given an object, crack into constituent documents and encode those into a bundle."""

    content, contents = osl_encode(obj, True)
    # should be a bunch of documents, not just one.
    bundle = [json.dumps(c) for c in contents]
    return bundle





