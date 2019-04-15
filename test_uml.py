import unittest
from uml_base import UMLFactory


class TestUMLFactory(unittest.TestCase):

    def test_experiment(self):

        """ Test that we can build a klass, and that it has the correct typekey
        (i.e. it's come from the ontology), and that it has one of the new
        attributes (i.e. it is a proper subclass)."""

        e = UMLFactory.build('designing.numerical_experiment')
        assert e._osl.type_key == 'cim.designing.numerical_experiment'
        assert e.label() == 'numerical\nexperiment'


if __name__=="__main__":
    unittest.main()
