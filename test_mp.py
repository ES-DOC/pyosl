import unittest
from mp_property import Property


class TestProperty(unittest.TestCase):
    """
    These tests all use builtin properties,
    Ontology class types are tested in the ontology class code that uses these properties.
    """

    def setUp(self):

        self.definitions = [
            ('my_attribute', 'str', '0.1', 'Not very interesting'),
            ('my_list_attr', 'int', '0.N', 'bunch of numbers')
        ]
        test_validator = lambda x, y: type(x) == {'str':str, 'int':int} [y]
        Property.set_validator(test_validator)

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
