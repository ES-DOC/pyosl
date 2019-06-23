import importlib.util
import os, sys
from inspect import getmembers, isfunction
import unittest
import configparser

from . import __file__


def setup_ontology(section='TESTING', name='cim'):

    """ Read ontology choice from configuration and load ontology """

    config = configparser.ConfigParser()

    config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'etc/configuration.ini'))

    config.read(config_file)
    ontodir = config[section][name]
    if '~' in ontodir:
        ontodir = os.path.expanduser(ontodir)
    return load_ontology(name, ontodir)


def load_ontology(modulename, ontodir):

    """ Load an ontology from a specific directory laid out according to the meta model,
     or does nothing if it"""

    def ok(k):
        """ Used to parse the ontology module to grab only packages with
        no underscore in their names, and exclude the ones we handle explicitly elsewhere"""
        if k in ['NAME', 'VERSION', 'DOC']:
            return False
        if '_' not in k:
            return True
        return False

    # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
    if not os.path.exists(ontodir):
        raise ValueError('Attempt to load ontology from non-existent folder - {}'.format(ontodir))
    init_file = os.path.join(ontodir,'__init__.py')
    if not os.path.exists(init_file):
        if not os.path.exists(ontodir):
            raise ValueError('Ontology folder [{}] doesnot exist'.format(ontodir))
        raise ValueError('No __init__.py found at {}'.format(init_file))
    if modulename in sys.modules.keys():
        raise ValueError('Attempt to load existing ontology')

    spec = importlib.util.spec_from_file_location(modulename, init_file)
    foo = importlib.util.module_from_spec(spec)
    sys.modules[modulename] = foo
    spec.loader.exec_module(foo)
    members = {k:m for k,m in getmembers(foo)}
    definitions = {k: v() for k, v in members.items() if ok(k)}
    packages = {}
    name = members['NAME']
    version = members['VERSION']
    documentation = members['DOC']
    for p, d in definitions.items():
        packages[p] = {}
        for x in d:
            functions = [o for o in getmembers(x, isfunction)]
            for n, k in functions:
                key = '{}.{}'.format(p, n)
                packages[p][key] = k()
                packages[p][key]['__doc__'] = k.__doc__

    return name, version, documentation, packages


NAME, VERSION, DOCUMENTATION, PACKAGES = setup_ontology()


class TestLoader(unittest.TestCase):
    """ Test loader """

    def setUp(self):
        assert NAME == 'cim'

    def test_documentation(self):
        print(DOCUMENTATION)


if __name__ == "__main__":
    unittest.main()
