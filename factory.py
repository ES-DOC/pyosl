import os, sys
import unittest
from pyosl.loader import NAME, VERSION, DOCUMENTATION, PACKAGES


def meta_fix(constructor):
    """ Fix constructors to conform to metamodel defaults"""
    if 'is_document' not in constructor:
        constructor['is_document'] = False
    return constructor


class OntoBase:

    """ A base class for defining ontology classes """

    def __init__(self):

        self.ontology, self.ontology_package, self.ontology_class = self.type_key.split('.')


class Ontology:

    """ Representation of a complete ontology """

    def __init__(self, base_class= OntoBase):
        """ Initialise ontology with a base class """

        (self.name, self.version, self.documentation, self.constructors)  = (
            NAME, VERSION, DOCUMENTATION, PACKAGES)

        self.BaseClass = base_class
        self.__initialise_classes()
        self.builtins = {
            'int': int,
            'str': str,
            'datetime': str,
            'float': float,
            'bool': bool,
            'text': str,
        }

    def get_package_from_key(self, key):
        my_key = key.split('.')
        options = {1:0, 2:0, 3:1}
        if len(my_key) <= 3:
            return my_key[options[len(my_key)]]
        else:
            raise ValueError('Unrecognised type key [{}]'.format(key))

    def get_package_contents(self, p):
        """ Return list of classes/enums within a package"""
        if p not in self.constructors:
            raise ValueError('Unrecognised package - ', p)
        return [k for k, c in self.constructors[p].items()]

    def __initialise_classes(self):
        """ Initialise the complete set of available classes. This is effectively a class factory"""
        self.klasses = {}
        for p in self.constructors:
            for k, constructor in self.constructors[p].items():
                # it is useful to have the base hierarchy
                base_hierarchy = []
                constructor['cim_version'] = self.version
                if 'base' in constructor:
                    next_base = constructor['base']
                    while next_base:
                        base_hierarchy.append(next_base)
                        bp = self.get_package_from_key(next_base)
                        next_base = self.constructors[bp][next_base]['base']
                constructor['base_hierarchy'] = base_hierarchy

                # it is useful to inject a complete description of the key as the type name
                constructor['type_key'] = '{}.{}'.format(self.name, k)

                constructor = meta_fix(constructor)

                klass = type(k, (self.BaseClass,), constructor)
                self.klasses[k] = klass

    def __repr__(self):
        result = '== ontology: {} == \n'.format(self.name)
        for k, p in self.constructors.items():
            result += str(k)+': '+', '.join([k.split('.')[-1] for k in p.keys()])+'\n'
        result += '======='
        return result

    def get_instance(self, class_type):
        return self.klasses[class_type]()



class TestOntology(unittest.TestCase):
    """ Test ontology stack. Need at least two tests to ensure we handle
    attempted reloads of the Ontology class."""

    def setUp(self):
        self.o = Ontology()

    def test_printable(self):
        print(self.o)

    def test_klass_build_numerical_experiment(self):
        experiment = self.o.klasses['designing.numerical_experiment']()
        print(experiment.cim_version, experiment.type_key)

    def test_package_contents(self):
        contents = self.o.get_package_contents('time')
        assert isinstance(contents,list)
        print(contents)
        assert 'time.calendar' in contents

if __name__ == "__main__":
    unittest.main()
