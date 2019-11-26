import unittest, os

from pyosl import setup_ontology

from pyosl.uml import BasicUML
from pyosl.uml import PackageUML
from pyosl.uml import UmlBase


class TestOriginal(unittest.TestCase):

    """ View packages in the original ontology (where here we assume
    the "original" ontology is the operational one, and the testing
    one is a variant from it, covered in the other test cases.
    """
    def setUp(self):
        NAME, VERSION, DOCUMENTATION, PACKAGES = setup_ontology()

