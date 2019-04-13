import unittest


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


class Property:
    """ Provides a class property """

    def __init__(self, definition):
        """ Initialise with a property tuple from the schema definition"""
        self.__value = None
        self._name, self._target, self._cardinality, self._doc = definition
        self._initialised = False

    def __set(self, value):

        # does it respect cardinality?
        if self._cardinality == '0.0':
            return ValueError('Attempt to assign value to property with cardinality 0.0 [{}]'.format(self._name))
        elif self._cardinality not in ['0.1','1.1']:
            if not isinstance(value, list):
                raise ValueError('Attempt to set single value to list type')
            # check types of list members
            for e in value:
                if not isinstance(e, type(self._target)):
                    raise ValueError('List element [{}, type {}] is not of type {}'.format(e, type(e), type(self._target)))
            self.__value = value
        else:
            # is it the right kind of thing?
            if isinstance(value, type(self._target)):
                self.__value = value
            else:
                raise ValueError('Attempt to set inconsistent type [{}] on property - expected [{}]'.format(
                    type(value), type(self._target)))

    def __get(self):
        return self.__value

    def append(self, value):
        if isinstance(value, self._target):
            self.__value.append(value)
        else:
            raise ValueError('Attempt to add inconsistent type to list in property')

    def __eq__(self, other):
        if not isinstance(other, Property):
            return False
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

    def test_equality(self):
        """ Test equality"""
        p1 = Property(self.definitions[0])
        p2 = Property(self.definitions[0])
        p1.value = 'fred'
        p2.value = 'fred'
        self.assertEqual(p1, p2)

    def test_inequality(self):
        """ Test equality"""
        p1 = Property(self.definitions[0])
        p2 = Property(self.definitions[0])
        p1.value = 'fred'
        p2.value = 'jane'
        self.assertNotEqual(p1, p2)


if __name__ == "__main__":
    unittest.main()
