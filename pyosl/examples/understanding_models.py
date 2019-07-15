from pathlib import Path

from pyosl import Factory, Base
from pyosl import esd_decode, de_camel_attribute
from pyosl import esd_encode
from pyosl import osl_encode2json, bundle_instance
from pyosl import osl_decode_json

import json

Factory.reset_descriptor()


def find_interesting_properties(instance):
    """ Find all the interesting (non None) properties for a pysosl instance """
    props = [k for k in instance.__dict__ if not k.startswith('_')]
    props = [k for k in props if getattr(instance, k) and getattr(instance, k) != 'n/a']
    return props


class Representation:
    """ Used to provide a text representation of any given pyosl class instance"""
    def __init__(self, klass_instance, depth=1, maxdepth=2):
        props = find_interesting_properties(klass_instance)
        for k in props:
            line = ['-' for i in range(depth*3)]
            print(''.join(line))
            value = getattr(klass_instance, k)
            if isinstance(value, list):
                print(f'{k}:')
                for v in value:
                    print('..:',v)
                    if isinstance(v,Base) and depth < maxdepth:
                        rr = Representation(v, depth+1, maxdepth)
            else:
                print(f'{k}:{value}')
                if isinstance(value, Base) and depth < maxdepth:
                    rr= Representation(value, depth+1, maxdepth)


class CoupledModel:
    """ Provides a high level view of a coupled model."""
    def __init__(self, klass_instance):
        props = find_interesting_properties(klass_instance)
        print(props)
        self.instance = klass_instance
        self.components = ''
        print(f'---\n{klass_instance.description}\n---')
        for k in self.instance.coupled_components:
            self.components += f'{k.name}\n'

    @property
    def hdr(self):
        """ Return name and coupler"""
        return f'{self.instance.name}: ({self.instance.coupler}) ({self.instance.long_name})'

    def __repr__(self):
        return self.hdr + '\n' + f'---\n{self.instance.description}\n---' + self.components


class CMIP6CoupledModel(CoupledModel):
    """ Instantiates a specialised version of a coupled model"""
    def __init__(self, *args, **kwargs):
        super(CMIP6CoupledModel, self).__init__(*args, **kwargs)
        r = Representation(self.instance.key_properties, 1, 1)


def get_model():
    """ Get a pyosl instance of a model to work with"""
    esd_archive_base = 'Code/esdoc19/esdoc-archive/esdoc/cmip6'
    esd_archive_dirs = ['spreadsheet-models']
    mdir = Path.home() / esd_archive_base / esd_archive_dirs[0]
    models = mdir.glob('*.json')
    index = 0
    instances = []
    for model in models:
        with model.open() as f:
            json_version = json.load(f)
            py_version = esd_decode(Factory, json_version)
            print(index, py_version.name)
            index += 1
            instances.append(py_version)
    return instances[-1]


if __name__ == "__main__":

    pv = get_model()
    #r = Representation(pv)
    h = CMIP6CoupledModel(pv)
    print(h)