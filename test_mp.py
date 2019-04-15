import unittest
from mp_property import Property
from mp_base import OntoFactory


class TestProperty(unittest.TestCase):
    """
    These tests all use builtin properties,
    ontology class types are tested in the ontology class code that uses these properties.
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


class TestBase(unittest.TestCase):
    """
    Test the ontology base class.
    Of necessity this tests the factory too.
    """
    def setUp(self):
        self.sp = OntoFactory.build('designing.simulation_plan')
        self.sp2 = OntoFactory.build('designing.simulation_plan')
        self.sp3 = OntoFactory.build('designing.simulation_plan')
        self.e = OntoFactory.build('designing.numerical_experiment')
        self.dr = OntoFactory.build('shared.doc_reference')

    def test_basic_attributes(self):
        assert hasattr(self.sp, 'expected_model')

    def test_pstr(self):
        name = 'Core Simulations'
        expected_name = '{} ({})'.format(name, self.sp._osl.type_key)
        self.sp.name = name
        assert expected_name == str(self.sp)

    def test_equality(self):
        self.sp.name = 'a'
        self.sp2.name = 'b'
        self.sp3.name = 'a'
        self.assertEqual(self.sp, self.sp3)
        self.assertNotEqual(self.sp, self.sp2)

    def test_simple_property_behaviour(self):
        with self.assertRaises(ValueError):
            self.sp.name = 1
        self.sp.name = 'fred'

    def test_complex_property_behaviour(self):
        """ Test a range of interesting options"""
        self.sp.will_support_experiments = []
        with self.assertRaises(ValueError):
            self.sp.will_support_experiments.append(1)
        with self.assertRaises(ValueError):
            self.sp.will_support_experiments.append([self.e,1])
        with self.assertRaises(ValueError):
            self.sp.will_support_experiments = [self.sp2]
        self.sp.will_support_experiments = [self.e]

    def test_doc_reference_behaviour(self):
        pass


if __name__ == "__main__":
    unittest.main()