from mp_base import Base
from mp_property import Property, PropertyDescriptor
from factory import Factory, Ontology
import unittest


class TestBase(unittest.TestCase):
    """
    Test the ontology base class.
    Of necessity this tests the factory too.
    """
    def setUp(self):
        o = Factory
        o.register(Ontology(Base))
        o.add_descriptor(PropertyDescriptor, Property)
        self.sp = o.build('designing.simulation_plan')
        self.sp2 = o.build('designing.simulation_plan')
        self.sp3 = o.build('designing.simulation_plan')
        self.e = o.build('designing.numerical_experiment')
        self.dr = o.build('shared.doc_reference')


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

    def test_document_metadata(self):
        self.assertFalse(hasattr(self.dr, '_meta'))
        self.assertTrue(hasattr(self.sp, '_meta'))
        self.assertTrue(Factory.core_validator(self.sp._meta, 'shared.doc_meta_info'))


if __name__ == "__main__":
    unittest.main()
