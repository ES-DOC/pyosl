from collections import OrderedDict
from loader import NAME, VERSION, DOCUMENTATION, PACKAGES


def meta_fix(constructor):
    """ Fix any deficiencies in the constructor needed to conform to the metamodel"""
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
            if self.name:
                return '{} ({})'.format(self.name, self._osl.type_key)
        return 'Instance of {}'.format(self._osl.type_key)

    def __eq__(self, other):
        print('Oh no!')
        return self == other


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
        options = {1: 0, 2: 0, 3: 1}
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
                else:
                    constructor['base'] = None

                constructor['base_hierarchy'] = base_hierarchy

                # it is useful to inject a complete description of the key as the type name
                constructor['type_key'] = '{}.{}.{}'.format(self.name, self.version, k)
                constructor['ontology_name'] = self.name
                constructor['package'], constructor['class_name'] = k.split('.')

                # it is important to add all the base properties in too, if they exist
                # it is possible for base classes to redefine properties, handle that too
                if base_hierarchy and constructor['type'] == 'class':
                    properties = OrderedDict()
                    for b in base_hierarchy:
                        pp, kk = b.split('.')
                        for prop in self.constructors[pp][b]['properties']:
                            properties[prop[0]] = prop
                        if 'is_document' not in constructor:
                            if 'is_document' in self.constructors[pp][b]:
                                constructor['is_document'] = self.constructors[pp][b]['is_document']
                    constructor['inherited_properties'] = [properties[kk] for kk in properties]
                else:
                    constructor['inherited_properties'] = []

                constructor = meta_fix(constructor)

        # now we have nice tidy constructors, lets' go through and build off base classes
        for p in self.constructors:
            for k, constructor in self.constructors[p].items():
                if k not in self.klasses:
                    self.klasses[k] = self.__build_class(k, constructor)
                # else it was already built as a base class

    def __build_class(self, key, constructor):

        meta = OntoMeta(constructor)
        base = constructor['base']
        if base:
            if base not in self.klasses:
                package = base.split('.')[0]
                self.klasses[base] = self.__build_class(base, self.constructors[package][base])
            return type(key, (self.klasses[base],), {'_osl': meta})
        else:
            return type(key, (self.BaseClass,), {'_osl': meta})

    def __repr__(self):
        result = '== ontology: {} == \n'.format(self.name)
        for k, p in self.constructors.items():
            result += str(k)+': '+', '.join([k.split('.')[-1] for k in p.keys()])+'\n'
        result += '======='
        return result

class Factory:

    known_subclasses = {}
    ontology = Ontology()
    descriptor = None
    my_property = None

    @staticmethod
    def register(ontology):

        """
        Used to specialise the ontolology beyond the core functionality which
        simply creates empty classes with _pyosl definitions attached to them.
        """

        Factory.ontology = ontology
        Factory.known_subclasses = {}

    @staticmethod
    def add_descriptor(descriptor, d_property):

        """ If the Factory.descriptor is present, it is used to bind the property d_property
        to factory attributes defined in the properties of the pyosl. If it is not present,
        then the pysol properties are not bound to attributes."""

        Factory.descriptor = descriptor
        Factory.my_property = d_property

    @staticmethod
    def core_validator(value, target):

        """ Returns True if value is of type target, where target is a string
        description of a type of the form which appears in property definitions """

        # Why not use isinstance? Because inside a property definition
        # we don't want to carry an instance of anything ... and in any
        # case we want to support DocReference and NilReason

        if isinstance(value, type(Factory.known_subclasses['shared.nil_reason']())):
            return True
        if target in Factory.ontology.builtins:
            return isinstance(value, Factory.ontology.builtins[target])
        elif target.startswith('linked_to'):
            # need to handle doc references and their internal type
            target_type = target[10:-1]
            if isinstance(value, type(Factory.known_subclasses[target_type]())):
                return True
            else:
                if not isinstance(value, type(Factory.known_subclasses['shared.doc_reference']())):
                    return False
                tmp = value.type == target_type
                if not tmp:
                    print ('wait')
                return tmp
        elif target in Factory.known_subclasses:
            if Factory.known_subclasses[target]._osl.type == 'enum':
                if isinstance(value, str):
                    if Factory.known_subclasses[target]._osl.is_open:
                        return True
                    else:
                        return value in [x[0] for x in Factory.known_subclasses[target]._osl.members]
                return False
            return isinstance(value, type(Factory.known_subclasses[target]()))
        else:
            return False

    @staticmethod
    def build(klass_name):

        """ Builds a specific classs and adds it to the classes known to the factory. """

        if klass_name in Factory.ontology.builtins:
            return Factory.ontology.builtins[klass_name]

        # needed for proper usage of nearly any class, so just build them now.
        # FIXME: We do this everytime ... which must be wasteful, even if
        # it is only the loop over minimal to find out all classes are done.
        if Factory.descriptor:
            # we probably need all the classes, so let's just build them all now
            minimal = Factory.ontology.klasses
        else:
            minimal = ['shared.doc_reference', 'shared.nil_reason']
        for k in minimal:
            if k not in Factory.known_subclasses:
                Factory.known_subclasses[k] = Factory.__build(k)

        # only build it if we don't know about it.
        if klass_name not in Factory.known_subclasses:

            if klass_name not in Factory.ontology.klasses:
                raise ValueError('Unknown class "{}" requested from {} Ontology'.format(
                    klass_name, Factory.ontology.name))

            Factory.known_subclasses[klass_name] = Factory.__build(klass_name)

        candidate = Factory.known_subclasses[klass_name]()

        if hasattr(candidate,'is_abstract'):
            if candidate._osl.is_abstract:
                raise ValueError("Attempt to instantiate abstract class")
        return candidate

    def __build(key):

        """ Convenience method for building classes. Isolated for code readability. """

        # `We need to build off base classes here too ...
        package, name = key.split('.')
        base = Factory.ontology.constructors[package][key]['base']
        if base:
            if base not in Factory.known_subclasses:
                Factory.known_subclasses[base] = Factory.__build(base)
            meta = OntoMeta(Factory.ontology.constructors[package][key])
            klass = type(key, (Factory.known_subclasses[base],), {'_osl': meta})
        else:
            klass = type(key, (Factory.ontology.klasses[key],), {})

        if Factory.descriptor:

            Factory.my_property.set_validator(Factory.core_validator)
            if hasattr(klass._osl, 'properties'):
                for p in klass._osl.properties + klass._osl.inherited_properties:
                    setattr(klass, p[0], Factory.descriptor(p))

        return klass



