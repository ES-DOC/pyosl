from factory import Ontology, Factory
import unittest


class TestOntology(unittest.TestCase):
    """ Test ontology stack. Need at least two tests to ensure we handle
    attempted reloads of the Ontology class."""

    def setUp(self):
        self.o = Ontology()
        assert isinstance(self.o, Ontology)

    def test_printable(self):
        print(self.o)

    def test_klass_build_numerical_experiment(self):
        """ Need to make sure we build classes and class instances properly"""
        experiment = self.o.klasses['designing.numerical_experiment']()
        assert hasattr(experiment._osl, 'cim_version')
        assert hasattr(experiment._osl, 'type_key')

    def test_package_contents(self):
        """ Need to make sure we build package lists properly"""
        contents = self.o.get_package_contents('time')
        assert isinstance(contents,list)
        assert 'time.calendar' in contents

    def test_subclass(self):
        e = self.o.klasses['designing.numerical_requirement']()
        nr = self.o.klasses['designing.temporal_constraint']()
        self.assertTrue(isinstance(nr, type(e)))


class TestFactory(unittest.TestCase):

    def setUp(self):

        self.f = Factory

    def testFactorySimple(self):

        klass = 'designing.numerical_requirement'
        instance = self.f.build(klass)
        assert hasattr(instance._osl, 'cim_version')
        assert hasattr(instance._osl, 'type_key')

    def test_builts(self):
        """ Need to know we can generate a builtin"""
        x = self.f.build('int')
        y = x()
        assert isinstance(y,int)


class TestOntoBase(unittest.TestCase):

    def setUp(self):
        self.f = Factory()
        self.k = self.f.build('designing.numerical_experiment')
        self.kbb = self.f.build('designing.temporal_constraint')

    def test_fundamentals(self):
        assert hasattr(self.k, '_osl')

    def test_str(self):
        assert str(self.k) == 'Instance of cim.designing.numerical_experiment'

    def test_core_validator(self):
        self.assertTrue(self.f.core_validator(self.kbb, 'designing.numerical_requirement'))
        self.assertFalse(self.f.core_validator(self.kbb, 'platform.platform'))





if __name__ == "__main__":
    unittest.main()