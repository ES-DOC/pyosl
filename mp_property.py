import unittest


class Property:
    """ Provides a class property """

    def __init__(self, property_string, constraint_string=None):
        """ Initialise with a property tuple from the schema definition"""
        self.__definition = property_string
        self.__constraint = constraint_string
        self.__constrained_value = False
        self.__value = None
        self.__doc__ = property_string[3]

    @property
    def isFixed(self):
        """Constraint property may make this property unchangeable """
        if self.__constrained_value:
            return 1
        return 0

    @property
    def name(self):
        return self.__definition[0]

    @property
    def target(self):
        return self.__definition[1]

    @property
    def cardinality(self):
        return self.__definition[2]


    def __set(self, value, initialisation=False):

        # does it respect cardinality?
        if self.cardinality not in ['0.0', '0.1']:
            if not isinstance(value, list):
                raise ValueError('Attempt to set single value to list type')
            # check types of list members
            for e in value:
                if not isinstance(e, self.target):
                    raise ValueError('List element [{}, type {}] is not of type {}'.format(e, type(e), self.target))
        else:
            # is it the right kind of thing?
            if isinstance(value, self.target):
                self.__value = value
            else:
                raise ValueError('Attempt to set inconsistent type on property')

        if self.__constrained_value:
            # is this initialisation?
            if initialisation:
                self.__value = value
            else:
                raise ValueError('Cannot set constrained property')

    def __get(self):
        return self.__value

    def append(self, value):
        if self.__constrained_value:
            raise ValueError('Cannot set constrained property')
        else:
            if isinstance(value, self.target):
                self.__value.append(value)
            else:
                raise ValueError('Attempt to add inconsistent type to list in property')

    def constrain(self, constraint_type, constraint_value):
        """ Apply a constraint to this property"""
        if constraint_type == 'constant':
            self.__constrained_value = True
            self.set(constraint_value, True)
        elif constraint_type == 'cardinality':
            mutable = list(self.__definition)
            mutable[2] = constraint_value
            self.__definition = tuple(mutable)
            if constraint_type == '0.0':
                self.__constrained_value = True
        else:
            raise ValueError('Constraint {} not yet supported'.format(constraint_type))

    def __eq__(self, other):
        if self.__definition != other.__definition:
            return 0
        if self.value != other.value:
            return 0
        return 1

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return '{}: {}'.format(self.name, str(self.value))

    value = property(__get, __set)


class TestProperty(unittest.TestCase):
    """ These tests all use builtin properties, ontology class
    types are tested in the ontology class code that uses these properties."""

    def setUp(self):
        self.definitions = [
            ('my_attribute', str, '0.1', 'Not very interesting'),
            ('my_list_attr', int, '0.N', 'bunch of numbers')
        ]

    def test_builtin(self):
        """ Test this works with a builtin python type as the target type"""
        p = Property(self.definitions[0])
        with self.assertRaises(ValueError):
            p.value = 1
            p.value = ['abc', 'def']
        p.value = 'irrelevant'

    def test_lists(self):
        """ Test we can't set single values or use the wrong type in a list"""
        p = Property(self.definitions[1])
        p.value = [1, 2, 3]
        with self.assertRaises(ValueError):
            p.value = 1
        with self.assertRaises(ValueError):
            p.value = [1, 2, '3']
        with self.assertRaises(ValueError):
            p.value = [1, 2, 3]
            p.append('4')


if __name__ == "__main__":
    unittest.main()
