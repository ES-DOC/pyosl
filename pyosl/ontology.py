from collections import OrderedDict

from .loader import NAME, VERSION, DOCUMENTATION, PACKAGES


def meta_fix(constructor):
    """ Fix any deficiencies in the constructor needed to conform to the metamodel"""
    if 'is_document' not in constructor:
        constructor['is_document'] = False
    return constructor


def info(klass, attribute=None):
    """" Return  information about a class. Approximates what one might do with
    a docstring, but allows us to get past descriptors."""

    if hasattr(klass, '_osl'):
        oslmeta = klass._osl
    elif isinstance(klass ,OntoMeta):
        # assume we have a constructor instance as part of class instantiation
        oslmeta = klass
    else:
        raise ValueError(f'Object  {klass} is not a  pyosl entity')

    if attribute:
        if hasattr(oslmeta,'properties'):
            for alist in [oslmeta.properties, oslmeta.inherited_properties]:
                for p in alist:
                    k, d = p[0], f'{p[0]} - {p[3]} (cardinality {p[2]}, type {p[1]})'
                    if k == attribute:
                        return d
            raise ValueError(f'No such attribute {attribute} for {klass}')
        elif hasattr(oslmeta, 'members'):
            for p in oslmeta.members:
                k, d = p[0], f'{p[0]} - {p[1]}'
                if k == attribute:
                    return d
            raise ValueError(f'No member {attribute} in {klass}')
        else:
            raise ValueError(f'{klass} is not a pyosl entity')

    docstring = f"\n__ Class {oslmeta.class_name} ({oslmeta.type_key}) __\n\n {oslmeta.__doc__.rstrip().lstrip()}\n\n"
    if hasattr(oslmeta, 'properties'):
        for alist, ptype in [(oslmeta.properties, 'Properties:\n'),
                             (oslmeta.inherited_properties, 'Inherited Properties:\n')]:
            docstring += ptype
            for p in alist:
                docstring += f'  {p[0]} - {p[3]} (cardinality {p[2]}, type {p[1]})\n'
        if hasattr(oslmeta,'constraints'):
            if oslmeta.constraints:
                docstring += 'Constraints:\n'
                for p in  oslmeta.constraints:
                    docstring += f'  {p}\n'
    elif hasattr(oslmeta, 'members'):
        docstring += 'Members\n'
        for p in oslmeta.members:
            docstring +=  f'  {p[0]} - {p[1]}\n'
    else:
        raise ValueError('Unknown OSL entity')
    return docstring


class OntoMeta:
    """ Use to hold all the ontology metadata that provides class typing"""
    def __init__(self, constructor):
        for k, v in constructor.items():
            setattr(self, k, v)


def fixlist(v):
    """ Make sure all lists have string valued members for printing"""
    if isinstance(v, list):
        s = ", ".join([str(vv) for vv in v])
        return f'[{s}]'
    else:
        return v


class OntoBase:

    """ A base class for defining ontology classes """

    def __str__(self):
        if hasattr(self._osl, 'pstr'):
            values = [fixlist(getattr(self, s)) for s in self._osl.pstr[1]]
            return self._osl.pstr[0].format(*values)
        elif hasattr(self, 'name'):
            if self.name:
                return f'{self.name} ({self.__class__.__name__})'
            return f'Instance of {self.__class__.__name__}'
        else:
            return f'Instance of {self.__class__.__name__}'

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if self._osl != other._osl:
            return False
        for p in self._osl.properties + self._osl.inherited_properties:
            if getattr(self, p[0]) != getattr(other, p[0]):
                return False
        return True

    def __ne__(self, other):
        return not self == other


class Ontology:

    """ Representation of a complete ontology """

    def __init__(self, base_class=OntoBase):
        """ Initialise ontology with a base class """

        (self.name, self.full_version, self.documentation, self.constructors) = (
            NAME, VERSION, DOCUMENTATION, PACKAGES)

        self.version = self.full_version.split('.')[0]
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

    def check_and_strip(self, key):
        """ Given a key, if just a naked package.klass, return, otherwise
        check ontology and version, then return the naked package.klass"""
        info = key.split('.')
        if len(info) == 1:
            return key
        elif len(info) == 2:
             return key
        elif len(info) == 4:
            try:
                assert (info[0], info[1]) == (self.name, self.version)
            except:
                raise ValueError(f'Ontology {self.name}.{self.version} cannot build {key}')
            return '.'.join(info[2:])
        else:
            raise ValueError(f'Unrecognised key {key}')

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
