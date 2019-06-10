from factory import Factory,Base
from ontology import Ontology

import unittest


class TestOntology(unittest.TestCase):
    """ Test ontology stack. Need at least two tests to ensure we handle
    attempted reloads of the Ontology class."""

    def setUp(self):
        self.o = Ontology(Base)
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
        self.f.reset_descriptor()

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
        self.f = Factory
        self.k = self.f.build('designing.numerical_experiment')
        self.kbb = self.f.build('designing.temporal_constraint')
        self.nr = self.f.build('designing.numerical_requirement')
        self.dr = self.f.build('shared.doc_reference')

    def test_fundamentals(self):
        assert hasattr(self.k, '_osl')

    def test_str(self):
        assert str(self.k) == 'Instance of cim.2.designing.numerical_experiment'

    def test_core_validator(self):
        self.assertTrue(self.f.core_validator(self.kbb, 'designing.numerical_requirement'))
        self.assertFalse(self.f.core_validator(self.kbb, 'platform.platform'))

    def test_core_validator_subclass(self):
        """ Subclass test"""
        self.assertTrue(self.f.core_validator(self.kbb, 'designing.numerical_requirement'))

    def test_core_validator_reference(self):
        """ Doc Reference test"""
        self.dr.name = 'fred'
        self.dr.type = 'designing.numerical_requirement'
        self.assertTrue(self.f.core_validator(self.dr, 'linked_to(designing.numerical_requirement)'))

    def test_enum_validation(self):
        """ make sure only appropriate values are assigned to an enum value. There
        are three interesting cases:
        (1) assigning an acceptable value to any kind of enum,
        (2) assigning a value from outside to a closed enum which should raise an error, and
        (3) assigning a value from outside to an open enum which is fine.
        """
        # build a few things to get them in the known subclasses
        a, b = self.f.build('shared.role_code'), self.f.build('activity.conformance_type')
        self.assertTrue(self.f.core_validator('point of contact', 'shared.role_code'))
        self.assertFalse(self.f.core_validator('aviator', 'shared.role_code'))
        self.assertTrue(self.f.core_validator('Not on your nelly', 'activity.conformance_type'))


class TestNewDocument(unittest.TestCase):

    def setUp(self):
        self.a = Factory.new_document('shared.party')
        self.a.name = 'Test Author'

    def testUUID(self):
        from uuid import UUID
        should_be_a_uuid = UUID(self.a._meta.uid)
        self.assertEqual(str(should_be_a_uuid), self.a._meta.uid)

    def testCreateWithAuthor(self):
        document = Factory.new_document('designing.project', self.a)
        self.assertEqual(document._meta.author.name,'Test Author')


if __name__ == "__main__":
    unittest.main()
