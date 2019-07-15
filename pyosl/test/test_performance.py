import unittest

from pyosl import Factory, online


def make_performance():
    """ As an example, let's describe the performance of the N1280 model on ARcher."""

    bryan = Factory.new_document('shared.party')
    bryan.name = 'Bryan Lawrence'
    bryan.orcid_id = '0000-0001-9262-7860'
    bryan.url = online('http://wwww.bnlawrence.net', 'personal website')

    # establish reference to documents we wont need, but for which we need a weak reference.
    n1280 = Factory.build('shared.doc_reference')
    n1280.name = 'N1280 Unified Model'
    n1280.canonical_name = 'UM GC X.Y @ N1280'
    n1280.type = 'science.model'

    # build performance from a spreadsheet
    expected_performance = Factory.new_document('platform.performance', author=bryan)
    expected_performance.model = n1280
    expected_performance.resolution = 1



class MakePerf(unittest.TestCase):

   def test_make(self):
       make_performance()

if __name__=="__main__":
    unittest.main()





