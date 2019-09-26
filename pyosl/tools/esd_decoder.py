# Decode json from the pyesdoc family
# Based on Mark Greenslade's pyesdoc/_codecs/dictionary/decoder.py
import re

from pyosl import DocRefNoType
from .osl_tools import make_time


def translate_type_to_osl_from_esd(doc_type):
    """ Translate from esd document types (e.g. 'cim2.designing.EnsembleRequirement)
    to pyosl document types (e.g 'cim.designing.ensemble_requirement').
    """
    o, v, p, d = doc_type.split('.')
    assert (o, v) == ('cim', '2')
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', d)
    d2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return '.'.join([o,v,p,d2])


def de_camel_attribute(n):
    """ Undo a camel case attribute string """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', n)
    d2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return d2


def _decode(factory, content, klass, debug=True):
    """ Decode json content into a python instance of that content"""

    instance = factory.build(klass)

    for name, value in content.items():
        name = de_camel_attribute(name)
        if isinstance(value, dict):
            if name == '_meta':
                metav = _decode(factory, value, 'shared.doc_meta_info')
                metav.type = translate_type_to_osl_from_esd(metav.type)
                setattr(instance, name, metav)
            else:
                newv = esd_decode(factory, value)
                try:
                    setattr(instance, name, newv)
                except DocRefNoType:
                    # FIXME: Raise an issue in pyesdoc about this, the serialisation
                    # should include an author type.
                    if klass == 'shared.doc_meta_info':
                        newv.type = 'cim.2.shared.party'
                        setattr(instance, name, newv)
                    else:
                        raise
        elif isinstance(value, list):
            alist = []
            for v in value:
                if isinstance(v, dict):
                    alist.append(esd_decode(factory, v))
                else:
                    alist.append(v)
            try:
                setattr(instance, name, alist)
            except:
                print('wait')# this is debug code for what looks like data
                raise
        else:
            if instance._osl.type_key == 'cim.2.shared.doc_reference':
                if name == 'type':
                    value = translate_type_to_osl_from_esd(value)
            try:
                setattr(instance, name, value)
            except ValueError as err:
                # Some esd encodings do not respect the time package. Is this one of those?
                try:
                    value = make_time(value)
                except:
                    raise err

    if instance and debug:
        ### Used to look for classes which may be problematic in some way.
        if 'software' in instance._osl.type_key:
            print(f'Deserialised {instance._osl.type_key}')

    return instance


def esd_decode(factory, json_dict):
    """ Decodes json esdoc content into a pyosl instance"""

    try:
        doc_type = json_dict['meta']['type']

    except KeyError:
        print(json_dict)
        raise KeyError('Document from pyesdoc has invalid type key.')

    # two important differences between pyesdoc and pyosl:
    doc_type = translate_type_to_osl_from_esd(doc_type)
    if len(json_dict['meta'].keys()) == 1:
        del json_dict['meta']
    else:
        json_dict['_meta'] = json_dict.pop('meta')

    return _decode(factory, json_dict, doc_type)





