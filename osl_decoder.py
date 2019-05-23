import json
from osl_encoder import SERIAL_VERSION


def check_target_understood(key):
    o, v, p, d = key.split('.')
    assert (o, v) == ('cim', '2')
    return '.'.join([p,d])


def _decode(factory, content, klass):
    """ Decode json content into a python instance of that content"""

    instance = factory.build(klass)

    for name, value in content.items():
      
        if isinstance(value, dict):
            if name == '_meta':
                metav = _decode(factory, value, 'shared.doc_meta_info')
                setattr(instance, name, metav)
            else:
                newv = osl_decode(factory, value)
                setattr(instance, name, newv)
               
        elif isinstance(value, list):
            alist = []
            for v in value:
                if isinstance(v, dict):
                    alist.append(osl_decode(factory, v))
                else:
                    alist.append(v)
            setattr(instance, name, alist)
        else:
            if instance._osl.type_key == 'cim.2.shared.doc_reference':
                if name == 'type':
                    value = check_target_understood(value)
            setattr(instance, name, value)
    return instance


def osl_decode(factory, json_dict):
    """ Decodes json esdoc content into a pyosl instance"""

    try:
        doc_type = json_dict['_meta']['type']
    except KeyError:
        print(json_dict)
        raise KeyError('Document has invalid type key.')

    return _decode(factory, json_dict, doc_type)


def osl_decode_json(factory, json_content):
    """ Decodes osl data encoded """
    json_dict = json.loads(json_content)
    assert '_meta' in json_dict
    assert 'source_key' in json_dict['_meta']
    assert json_dict['_meta']['source_key'].endswith(SERIAL_VERSION)
    return osl_decode(factory, json_dict)



