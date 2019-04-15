
class PropertyDescriptor:

    """ This python descriptor applied to the class ensures
    that class instances use the Property type for all the
    osl ontology attributes. """
    # Useful explanations of how this works:
    # https://stackoverflow.com/questions/44548995/how-to-add-and-bind-descriptors-dynamically-in-pytho

    def __init__(self, definition):
        self.__value = Property(definition)

    def __set__(self, instance, value):
        self.__value.value = value

    def __get__(self, instance, owner):
        return self.__value.value


class PropertyList (list):
    """ Lightweight type checking"""
    # TODO intercept the other methods if there is a case for it.

    def __init__(self, target, value=[]):
        self._target = target
        for e in value:
            if not Property.validator(e, self._target):
                raise ValueError('List element [{}, type {}] is not of type {}'.format(
                    e, type(e), type(self._target)))
        list.__init__(self, value)

    def append(self, value):

        if Property.validator(value, self._target):
            list.append(value)
        else:
            raise ValueError('Attempt to add wrong type to list')


class Property:
    """ Provides a class property """

    validator = lambda x,y : True

    @staticmethod
    def set_validator(validator):
        """ Property needs to be told how to validator a value against
        a target, otherwise it will just default to allowing any
        value to be set, regardless of target type."""
        Property.validator = validator

    def __init__(self, definition):
        """ Initialise with a property tuple from the schema definition. """
        # In practice initialising the doc string isn't very useful, since
        # it appears that there is no way to get to it, but we do it anyway
        # in case we find a way to do it in the future.
        self._name, self._target, self._cardinality, self._doc = definition
        if self._cardinality in ['0.0','0.1','1.1']:
            self.__value = None
        else:
            self.__value = PropertyList(self._target, [])
        self._initialised = False

    def __set(self, value):

        # TODO include support for a one time initialisation of something that cannot be changed.

        # does it respect cardinality?
        if self._cardinality == '0.0':
            return ValueError('Attempt to assign value to property with cardinality 0.0 [{}]'.format(self._name))
        elif self._cardinality not in ['0.1','1.1']:
            if not isinstance(value, list):
                raise ValueError('Attempt to set single value to list type')
            # check types of list members
            self.__value = PropertyList(self._target, value)

        else:
            # is it the right kind of thing?
            if Property.validator(value, self._target):
                self.__value = value
            else:
                raise ValueError('Attempt to set inconsistent type on property {}'.format(self._name))

    def __get(self):
        return self.__value

    def append(self, value):
        if Property.validator(value, self._target):
            self.__value.append(value)
        else:
            raise ValueError('Attempt to add inconsistent type to list in property')

    def __eq__(self, other):
        if not isinstance(other, Property):
            return False
        for n in ['_name', '_cardinality', '_target', '_doc']:
            if getattr(self, n) != getattr(other, n):
                return 0
        if self.value != other.value:
            return 0
        return 1

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return '{}: {}'.format(self.name, str(self.value))

    value = property(__get, __set)



