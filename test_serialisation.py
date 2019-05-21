from factory import Ontology, Factory
import unittest
from pathlib import Path
from mp_base import Base
from mp_property import Property, PropertyDescriptor
from factory import Factory, Ontology
from esd_decoder import esd_decode, de_camel_attribute
from esd_encoder import esd_encode
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
                r = esd_decode(FACTORY, doc_as_json)
                print(r)

    def test_roundtrip(self):
        for x in self.instances:
            with x.open() as f:
                json_version = json.load(f)
                python_version = esd_decode(FACTORY, json_version)
                new_json_version = esd_encode(python_version)
                new_python_version = esd_decode(FACTORY, new_json_version)
                assert python_version == new_python_version


if __name__=="__main__":
    unittest.main()
