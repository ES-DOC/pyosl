# Decode json from the pyesdoc family
# Heavily based on Mark Greenslade's pyesdoc/_codecs/dictionary/decoder.py
import re

def translate_type_to_osl_from_esd(doc_type):
    """ Translate from esd document types (e.g. 'cim2.designing.EnsembleRequirement)
    to pyosl document types (e.g 'cim.designing.ensemble_requirement').
    """
    o, v, p, d = doc_type.split('.')
    assert (o, v) == ('cim', '2')
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', d)
    d2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return '.'.join([p,d2])


def _decode(factory, content, instance):
    """ Decode json content into a python instance of that content"""

    for name, value in content.items():
        print(type(instance), instance, name, value)
        if isinstance(value, dict):
            setattr(instance, name, esd_decoder(factory, value))
        elif isinstance(value, list):
            alist = []
            for v in value:
                if isinstance(v, dict):
                    alist.append(esd_decoder(factory, v))
                else:
                    alist.append(v)
            setattr(instance, name, alist)
        else:
            setattr(instance, name, value)
        print ('done')
    return instance


def esd_decoder(factory, json_dict):
    """ Decodes json esdoc content into a pyosl instance"""

    try:
        doc_type = json_dict['meta']['type']
    except KeyError:
        raise KeyError('Document pyesdoc type key is invalid.')

    # two important differences between pyesdoc and pyosl:
    doc_type = translate_type_to_osl_from_esd(doc_type)
    if len(json_dict['meta'].keys()) == 1:
        del json_dict['meta']
    else:
        json_dict['_meta'] = json_dict.pop('meta')

    return _decode(factory, json_dict, factory.build(doc_type))





