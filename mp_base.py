from pyosl.factory import Ontology, OntoBase, Factory
from pyosl.mp_property import PropertyDescriptor
import unittest


class Base(OntoBase):
    """ This is the ontology base class, used to ensure that the properties
    defined in the ontology are respected."""

    def __str__(self):
        if hasattr(self._osl, 'pstr'):
            values = [getattr(self, s) for s in self._osl.pstr[1]]
            return self._osl.pstr[0].format(values)
        else:
            return super().__str__()

    def __eq__(self, other):
        if not isinstance(other, Base):
            return False
        if self._osl != other._osl:
            return False
        for p in self._osl.properties + self._osl.inherited_properties:
            if getattr(self, p[0]) != getattr(other, p[0]):
                return False
        return True

    def __ne__(self, other):
        return self == other


class OntoFactory(Factory):
    Factory.register(Ontology(Base))
    Factory.add_descriptor(PropertyDescriptor)


class TestBase(unittest.TestCase):
    """ Test the ontology base class. Of necessity this tests the factory too."""
    def setUp(self):
        self.sp = OntoFactory.build('designing.simulation_plan', with_properties=True)
        self.sp2 = OntoFactory.build('designing.simulation_plan', with_properties=True)
        self.sp3 = OntoFactory.build('designing.simulation_plan', with_properties=True)

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

    def test_property_behaviour(self):
        with self.assertRaises(ValueError):
            self.sp.name = 1






if __name__ == "__main__":
    unittest.main()

