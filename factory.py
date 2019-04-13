from collections import OrderedDict
import unittest
from pyosl.loader import NAME, VERSION, DOCUMENTATION, PACKAGES


def meta_fix(constructor):
    """ Fix constructors to conform to metamodel defaults"""
    if 'is_document' not in constructor:
        constructor['is_document'] = False
    return constructor


class OntoMeta:
    """ Use to hold all the ontology metadata that provides class typing"""
    def __init__(self, constructor):
        for k, v in constructor.items():
            setattr(self, k, v)


class OntoBase:

    """ A base class for defining ontology classes """

    def __init__(self):
        pass

    def __str__(self):
        """ If we have a name attribute use it, otherwise just say what we are."""
        if hasattr(self, 'name'):
            return '{} ({})'.format(self.name, self._osl.type_key)
        else:
            return 'Instance of {}'.format(self._osl.type_key)


class Ontology:

    """ Representation of a complete ontology """

    def __init__(self, base_class=OntoBase):
        """ Initialise ontology with a base class """

        (self.name, self.version, self.documentation, self.constructors) = (
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
                constructor['ontology_name'] = self.name
                constructor['package'], constructor['class_name'] = k.split('.')

                # if the metamodel has some defaults that need propagation
                constructor = meta_fix(constructor)

                # it is important to add all the base properties in too, if they exist
                # it is possible for base classes to redefine properties, handle that too
                if base_hierarchy and constructor['type'] == 'class':
                    properties = OrderedDict()
                    for b in base_hierarchy:
                        pp, kk = b.split('.')
                        for prop in self.constructors[pp][b]['properties']:
                            properties[prop[0]] = prop
                    constructor['inherited_properties'] = [properties[kk] for kk in properties]
                else:
                    constructor['inherited_properties'] = []

                meta = OntoMeta(constructor)
                klass = type(k, (self.BaseClass,), {'_osl': meta})

                self.klasses[k] = klass

    def __repr__(self):
        result = '== ontology: {} == \n'.format(self.name)
        for k, p in self.constructors.items():
            result += str(k)+': '+', '.join([k.split('.')[-1] for k in p.keys()])+'\n'
        result += '======='
        return result


class Factory:

    known_subclasses = {}
    client_factories = {}
    ontology = Ontology()

    @staticmethod
    def register(ontology):
        Factory.ontology = ontology

    @staticmethod
    def build(klass_name, *args, **kwargs):

        if klass_name in Factory.ontology.builtins:
            return Factory.ontology.builtins[klass_name]

        if klass_name not in Factory.known_subclasses:

            if klass_name not in Factory.ontology.klasses:
                raise ValueError('Unknown class "{}" requested from {} Ontology'.format(
                    klass_name, Factory.ontology.name))

            klass = type(klass_name, (Factory.ontology.klasses[klass_name],),{})
            Factory.known_subclasses[klass_name] = klass

        return Factory.known_subclasses[klass_name](*args, **kwargs)


class TestOntology(unittest.TestCase):
    """ Test ontology stack. Need at least two tests to ensure we handle
    attempted reloads of the Ontology class."""

    def setUp(self):
        self.o = Ontology()
        assert isinstance(self.o, Ontology)

    def test_printable(self):
        print(self.o)

    def test_klass_build_numerical_experiment(self):
        """ Need to make sure we build classes and class instances properly"""
        experiment = self.o.klasses['designing.numerical_experiment']()
        assert hasattr(experiment._osl, 'cim_version')
        assert hasattr(experiment._osl, 'type_key')

    def test_package_contents(self):
        """ Need to make sure we build package lists properly"""
        contents = self.o.get_package_contents('time')
        assert isinstance(contents,list)
        print(contents)
        assert 'time.calendar' in contents


class TestFactory(unittest.TestCase):

    def setUp(self):

        self.f = Factory

    def testFactorySimple(self):

        klass = 'designing.numerical_requirement'
        instance = self.f.build(klass)
        assert hasattr(instance._osl, 'cim_version')
        assert hasattr(instance._osl, 'type_key')

    def test_builts(self):
        """ Need to know we can generate a builtin"""
        x = self.f.build('int')
        y = x()
        assert isinstance(y,int)

class TestOntoBase(unittest.TestCase):

    def setUp(self):
        f = Factory()
        self.k = f.build('designing.numerical_experiment')
        assert hasattr(self.k, '_osl')


    def test_str(self):
        assert str(self.k) == 'Instance of cim.designing.numerical_experiment'




if __name__ == "__main__":
    unittest.main()
