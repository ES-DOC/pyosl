from errors import DocRefNoType
from anacronisms import group_hack
from uuid import uuid4
from ontology import Ontology, OntoMeta


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
            ok = isinstance(value, Factory.ontology.builtins[target])
            if not ok and target == 'bool':
                """ Handle duck typing booleans as a special case."""
                try:
                    x = bool(value)
                    ok = True
                except:
                    pass
            return ok
        elif target.startswith('linked_to'):
            # need to handle doc references and their internal type
            target_type = target[10:-1]
            if isinstance(value, type(Factory.known_subclasses[target_type]())):
                return True
            else:
                if not isinstance(value, type(Factory.known_subclasses['shared.doc_reference']())):
                    return False
                if value.type:
                    return isinstance(Factory.build(group_hack(value.type)), type(Factory.build(target_type)))
                else:
                    raise DocRefNoType('Doc_Reference used in assignment does not have a target type')
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

        klass_name = group_hack(klass_name)
        klass_name = Factory.ontology.check_and_strip(klass_name)

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

        if hasattr(candidate, 'is_abstract'):
            if candidate._osl.is_abstract:
                raise ValueError("Attempt to instantiate abstract class")
        return candidate


    @staticmethod
    def new_document(klass, author=None):
        """ Build and initialise a new document"""
        doc = Factory.build(klass)
        if not hasattr(doc,'_meta'):
            raise ValueError(f'Not-a-Document: Cannot build "{klass}" via new_document method')
        doc._meta.uid = str(uuid4())
        if author:
            doc._meta.author = author
        return doc


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

            if klass._osl.is_document:
                p = ('_meta', 'shared.doc_meta_info', '1.1', 'Document Metadata')
                setattr(klass, p[0], Factory.descriptor(p))


        return klass



