class PropertyDescriptor:

    """
    This python descriptor applied to the class ensures that instances use the Property type for all the
    osl ontology attributes.
    """
    # Useful explanations of how this works:
    # https://stackoverflow.com/questions/44548995/how-to-add-and-bind-descriptors-dynamically-in-python
    # https://nbviewer.jupyter.org/urls/gist.github.com/ChrisBeaumont/5758381/raw/descriptor_writeup.ipynb

    def __init__(self, definition):
        """
        Initialise with the property definition, and create a label so we can ensure we use the instance dictionary
        to store state. Using a weak dictionary doesn't work because we have non-hashable instances.
        """
        self.definition = definition
        self.label = definition[0]

    def __set__(self, instance, value):
        """
        Set value of the property
        """
        p = self.__myget(instance)
        p.value = value

    def __get__(self, instance, owner):
        """
        Get value of the instance property. There i no value for a class instance (or more correctly,
        there had better not be, since we have no way to do it with this methodology.
        """
        if instance:
            return self.__myget(instance).value
        else:
            return 'Class variable not initialised'

    def __myget(self, instance):
        """
        Slightly more efficient form than building the Property when it already exists
        (as would happen if we used the get(x, default) API).
        """
        if self.label not in instance.__dict__:
            instance.__dict__[self.label] = Property(self.definition)
        return instance.__dict__[self.label]


class PropertyList (list):
    """
    Lightweight type checking
    """
    # TODO intercept the other methods if there is a case for it.

    def __init__(self, target, value=[]):
        self._target = target
        for e in value:
            if not Property.validator(e, self._target):
                raise ValueError(f'List element [{e}, type {type(e)}] is not of type {self._target}')
        list.__init__(self, value)

    def append(self, value):

        if Property.validator(value, self._target):
            list.append(value)
        else:
            raise ValueError('Attempt to add wrong type to list')


class Property:
    """
    Provides a class property
    """

    validator = lambda x, y: True

    @staticmethod
    def set_validator(validator):
        """ Property needs to be told how to validator a value against
        a target, otherwise it will just default to allowing any
        value to be set, regardless of target type."""
        Property.validator = validator

    def __init__(self, definition):
        """
        Initialise with a property tuple from the schema definition.
        """

        self._name, self._target, self._cardinality, self._doc = definition
        if self._cardinality in ['0.0','0.1','1.1']:
            self.__value = None
        else:
            self.__value = PropertyList(self._target, [])
        self._initialised = False

    def __set(self, value):
        """ This is the setter method"""

        # TODO include support for a one time initialisation of something that cannot be changed.

        # does it respect cardinality?
        if self._cardinality == '0.0':
            return ValueError('Attempt to assign value to property with cardinality 0.0 [{}]'.format(self._name))
        elif self._cardinality not in ['0.1', '1.1']:
            if not isinstance(value, list):
                raise ValueError('Attempt to set single value to list type')
            # check types of list members
            self.__value = PropertyList(self._target, value)

        else:
            # is it the right kind of thing?
            if Property.validator(value, self._target):
                self.__value = value
            else:
                raise ValueError('Attempt to set inconsistent type {} on property {} (expected {})'.format(type(value), self._name, self._target))

    def __get(self):
        """ This is the getter method """
        return self.__value

    def append(self, value):
        """ Need to deal with append for list types """
        if Property.validator(value, self._target):
            self.__value.append(value)
        else:
            raise ValueError('Attempt to add inconsistent type to list in property')

    def __eq__(self, other):
        """ Properly compare. Not used in anger, but can be useful in tests. (Not used in
        anger since property values are normally exposed."""
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

    value = property(__get, __set)
