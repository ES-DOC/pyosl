# Encode json in the pyesdoc format
# Based on Mark Greenslade's pyesdoc/_codecs/dictionary/encoder.py

from pyosl import Property

def _is_encodable_attribute(name):
    """Returns flag indicating whether an attribute is encodable.
    """
    if name == '_meta':
        return True
    elif name.startswith("_") or name.startswith("__") or name == "ext":
        return False
    else:
        return True

def encamel(key):
    """ Turn attribute name into camel case"""
    bits = key.split('_')
    if len(bits) > 1:
        capital_bits = bits[1:]
        bits = [bits[0],] + [b.capitalize() for b in capital_bits]
    return ''.join(bits)


def esd_encode(doc):
    """Encodes a document.
    :param doc: Document being encoded.
    :type doc: object
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

        if key == '_meta':
            newkey = 'meta'
        else:
            newkey = encamel(key)

        val = _value(val)
        # Process iterables / non-iterables differently.
        try:
            iter(val)

        # Encode non-iterables:
        except TypeError:
            # ... pyesdoc types;

            if hasattr(val, '_osl'):
                obj[newkey] = esd_encode(val)
                #FIXME: Probably some things we have to pull out of meta and encode directly ...
            # ... simple types;
            elif val is not None:
                obj[newkey] = val

        # Encode iterables:
        else:
            if len(val) > 0:
                # ... string types;
                if isinstance(val, str):
                    obj[newkey] = val
                # ... collections;
                else:
                    obj[newkey] = [esd_encode(i) if hasattr(i, '_osl') else i for i in [_value(j) for j in val]]

    # Inject type info to simplify decoding.
    klass = doc.__class__.__name__
    if klass != "shared.doc_meta_info":
        if 'meta' not in obj:
            obj['meta'] = {}
        obj['meta']['type'] = encamel(doc._osl.type_key)
        #if klass == 'shared.doc_reference':
        #    obj['type'] = f"{doc._osl.ontology_name}.{doc._osl.cim_version}.{obj['type']}"
        print(klass, obj['meta']['type'])
    return obj
