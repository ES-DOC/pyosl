from pyosl.factory import Ontology, OntoBase, Factory
from pyosl.mp_property import Property
import unittest


class Base(OntoBase):
    """ This is the ontology base class, used to ensure that the properties
    defined in the ontology are respected."""

    def __init__(self):
        super().__init__()
        for p in self._osl.inherited_properties:
            self = setters_and_getters(self, p)
        for p in self._osl.properties:
            self = setters_and_getters(self, p)

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
            # bypass the property setters and getters
            pk = '__{}'.format(p[0])
            if getattr(self, pk) != getattr(other, pk):
                return False
        return True

    def __ne__(self, other):
        return self == other


class OntoFactory(Factory):
    Factory.register(Ontology(Base))


def setters_and_getters(klass, this_property_definition):

    """ Construct and assign dynamic setters and getters to the klass in hand"""
    # Yes, we know this is very "old school", but it helps a lot for metadata
    # validation if the ontology cannot be seeded with the wrong stuff!

    def set_property(c, k, v):
        """ Set property k on class c with value v"""
        p = getattr(c, k)
        p.value = v

    name = this_property_definition[0]
    setter_name = '__set_{}'.format(name)
    getter_name = '__get_{}'.format(name)
    hidden_name = '__{}'.format(name)

    if hasattr(klass, hidden_name):
        raise AttributeError('Attempt to reset  property {}'.format(name))

    setattr(klass, hidden_name, Property(this_property_definition))

    s = lambda i, v: set_property(i, hidden_name, v)
    g = lambda i: getattr(i, hidden_name)

    setattr(klass, setter_name, s)
    setattr(klass, getter_name, g)
    setattr(klass, name, property(g, s, doc=this_property_definition[3]))

    return klass


class TestBase(unittest.TestCase):
    """ Test the ontology base class. Of necessity this tests the factory too."""
    def setUp(self):
        self.sp = OntoFactory.build('designing.simulation_plan')
        self.sp2 = OntoFactory.build('designing.simulation_plan')
        self.sp3 = OntoFactory.build('designing.simulation_plan')

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
        self.assertNotEquals(self.sp, self.sp2)

    def test_david(self):
        assert isinstance(self.sp.name, property)
        with self.assertRaises(ValueError):
            self.sp.name = 1
            print(self.sp)




if __name__ == "__main__":
    unittest.main()

