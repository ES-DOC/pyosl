from factory import Ontology, Factory
import unittest
from pathlib import Path
from mp_base import Base
from mp_property import Property, PropertyDescriptor
from factory import Factory, Ontology
from esd_decoder import esd_decoder, de_camel_attribute
import json

# make a factory to use in the test cases
FACTORY = Factory
FACTORY.register(Ontology(Base))
FACTORY.add_descriptor(PropertyDescriptor, Property)


class TestESDread(unittest.TestCase):
    """ Tests de-serialisation from an ES-DOC json instance"""

    def setUp(self):
        self.instances = Path.cwd().glob('test_input/*')

    def test_decamel(self):
        s1 = 'responsibleParties'
        s2 = 'responsible_parties'
        assert de_camel_attribute(s1) == s2


    def test_read(self):
        for x in self.instances:
            print(x)
            with x.open() as f:
                doc_as_json = json.load(f)
                r = esd_decoder(FACTORY, doc_as_json)
                print(r)

if __name__=="__main__":
    unittest.main()
