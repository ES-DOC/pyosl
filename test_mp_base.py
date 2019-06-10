from factory import Factory
import unittest


class TestBase(unittest.TestCase):
    """
    Test the ontology base class.
    Of necessity this tests the factory too.
    """
    def setUp(self):
        o = Factory
        o.reset_descriptor()
        self.sp = o.build('designing.simulation_plan')
        self.sp2 = o.build('designing.simulation_plan')
        self.sp3 = o.build('designing.simulation_plan')
        self.e = o.build('designing.numerical_experiment')
        self.dr = o.build('shared.doc_reference')
        self.o = o

    def test_class_isolation(self):
        """ It looks like assigning a variable to an instance
        is also assigning it to the class ... something is
        wrong. """
        x = str(self.sp.name)
        self.sp.name = 'a'
        assert x == str(self.sp2.name)

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
        """ some horrendous bug in the factory """
        alist = []
        for a in ['fred','joe']:
            p = self.o.build('shared.doc_reference')
            p.name = a
            p.type = 'shared.party'
            alist.append(p)
        r = self.o.build('shared.responsibility')
        r.role_code = 'point of contact'
        r.parties = alist
        assert self.o.known_subclasses['shared.doc_reference'].name != 'joe'

    def test_document_metadata(self):
        self.assertFalse(hasattr(self.dr, '_meta'))
        self.assertTrue(hasattr(self.sp, '_meta'))
        self.assertTrue(Factory.core_validator(self.sp._meta, 'shared.doc_meta_info'))

    def test_docstring(self):
        self.sp.name = 'Bryan'
        # nb: can't do the next line without accessing .name somehow first ... so it will appear in the dictionary!
        print(f'Docstring for "name" is "{self.sp.__dict__["name"]._doc}"')

    def test_delete(self):
        self.sp.name = 'Bryan'
        del (self.sp.name)
        self.assertEqual(None,self.sp.name)


if __name__ == "__main__":
    unittest.main()
