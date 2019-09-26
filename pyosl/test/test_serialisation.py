import unittest
from pathlib import Path

from pyosl import Factory
from pyosl.tools import esd_decode, de_camel_attribute
from pyosl.tools import esd_encode
from pyosl.tools import osl_encode2json, bundle_instance
from pyosl.tools import osl_decode_json

import json


Factory.reset_descriptor()

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
                r = esd_decode(Factory, doc_as_json)
                print(r)

    def test_esdroundtrip(self):
        for x in self.instances:
            with x.open() as f:
                json_version = json.load(f)
                python_version = esd_decode(Factory, json_version)
                new_json_version = esd_encode(python_version)
                new_python_version = esd_decode(Factory, new_json_version)
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
                        python_version = esd_decode(Factory, json_version)
                    except:
                        print(f"Error reading {docfile}")
                        raise

    def test_model(self):
        """ Test manipulating a model document."""
        mdir = self.folders[1]
        models = mdir.glob('*.json')
        for model in models:
            with model.open() as f:
                json_version = json.load(f)
                py_version = esd_decode(Factory, json_version)
            #break


class TestOSLroundtrip(unittest.TestCase):
    """ Tests round tripping an original ESD document via OSL encode/decode"""

    def setUp(self):
        self.instances = Path.cwd().glob('test_input/*')

    def test_oslroundtrip(self):
        for x in self.instances:
            with x.open() as f:
                json_version = json.load(f)
                python_version = esd_decode(Factory, json_version)
                new_json_version = osl_encode2json(python_version)
                new_python_version = osl_decode_json(Factory, new_json_version)
                assert python_version == new_python_version

    def test_bundle(self):
        author = Factory.new_document('shared.party')
        document = Factory.new_document('designing.project', author)
        author.name = 'Bryan'
        document.name = 'My Big Fat Experiment'
        docs = bundle_instance(document)
        self.assertEqual(len(docs), 2, 'Wrong number of documents returned')
        for doc in docs:
            odoc = osl_decode_json(Factory,doc)
            print(odoc)


if __name__ == "__main__":
    unittest.main()
