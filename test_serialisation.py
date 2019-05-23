from factory import Ontology, Factory
import unittest
from pathlib import Path
from mp_base import Base
from mp_property import Property, PropertyDescriptor
from factory import Factory, Ontology
from esd_decoder import esd_decode, de_camel_attribute
from esd_encoder import esd_encode
from osl_encoder import osl_encode2json
from osl_decoder import osl_decode_json

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

    def test_esdroundtrip(self):
        for x in self.instances:
            with x.open() as f:
                json_version = json.load(f)
                python_version = esd_decode(FACTORY, json_version)
                new_json_version = esd_encode(python_version)
                new_python_version = esd_decode(FACTORY, new_json_version)
                assert python_version == new_python_version


class TestESDArchive(unittest.TestCase):
    """ Tests reading everything in a copy of the ESD archive"""

    def setUp(self):
        esd_archive_base = 'Code/esdoc19/esdoc-archive/esdoc/cmip6'
        esd_archive_dirs = ['spreadsheet-experiments', 'spreadsheet-models']
        base = Path.home() / esd_archive_base
        self.folders = []
        for folder in esd_archive_dirs:
            self.folders.append(base / folder)

    def test_rwesddocs(self):
        for f in self.folders:
            docfiles = f.glob('*.json')
            for docfile in docfiles:
                print(docfile)
                with docfile.open() as f:
                    try:
                        json_version = json.load(f)
                        python_version = esd_decode(FACTORY, json_version)
                    except:
                        print(f"Error reading {docfile}")
                        raise


class TestOSLroundtrip(unittest.TestCase):
    """ Tests round tripping an original ESD document via OSL encode/decode"""

    def setUp(self):
        self.instances = Path.cwd().glob('test_input/*')

    def test_oslroundtrip(self):
        for x in self.instances:
            with x.open() as f:
                json_version = json.load(f)
                python_version = esd_decode(FACTORY, json_version)
                new_json_version = osl_encode2json(python_version)
                new_python_version = osl_decode_json(FACTORY, new_json_version)
                assert python_version == new_python_version


if __name__=="__main__":
    unittest.main()
