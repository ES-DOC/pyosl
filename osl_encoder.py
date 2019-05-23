from mp_property import Property
SERIAL_VERSION = 'json by osl_encode V0.1'
import json

def _is_encodable_attribute(name):
    """Returns flag indicating whether an attribute is encodable.
    """
    if name == '_meta':
        return True
    elif name.startswith("_") or name.startswith("__") or name == "ext":
        return False
    else:
        return True

def osl_encode(doc):
    """Encodes an osl instance (whether a full doc, or a part there-of).
    :param doc: Content being encoded.
    :type doc: osl object
    :returns: An encoded document representation.
    :rtype: dict
    """
    obj = dict()

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
                obj[key] = osl_encode(val)
              
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
                    obj[key] = [osl_encode(i) if hasattr(i, '_osl') else i for i in [_value(j) for j in val]]

    # Inject type info to simplify decoding. We could use _osl, but that would be excessive duplication in output.
    klass = doc.__class__.__name__
    if klass != "shared.doc_meta_info":
        if '_meta' not in obj:
            obj['_meta'] = {}
        obj['_meta']['type'] = doc._osl.type_key
        if klass == 'shared.doc_reference':
            obj['type'] = f"{doc._osl.ontology_name}.{doc._osl.cim_version}.{obj['type']}"
        print(klass, obj['_meta']['type'])
    return obj


def osl_encode2json(obj):
    """ Given an instance of an OSL document, encode into json. """

    if obj._meta.source_key:
       if SERIAL_VERSION not in obj._meta_source_key:
           obj._meta.source_key += f'\n{SERIAL_VERSION}'
    else:
        obj._meta.source_key = SERIAL_VERSION

    return json.dumps(osl_encode(obj))

