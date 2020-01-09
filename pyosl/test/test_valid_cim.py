import unittest

from pyosl import Factory
from pyosl.tools import named_build, new_document, numeric_value


class TestValidity(unittest.TestCase):
    """"
    Test that the CIM definitions accessed via the Ontology meet
    some simple consistency tests (all attributes are of known type,
    and the linked_to reference stereotype is used appropriately.
    """

    def test_linked_to(self):
        """ Test usage of linked_to stereotype"""
        klasses = Factory.ontology.klasses
        for k in klasses:
            # Test we can build the core class
            x = Factory.build(k)
            # Now test we can build all the named attributes
            konstructor = klasses[k]
            if hasattr(konstructor._osl, 'properties'):
                for prop in konstructor._osl.properties:
                    ptype = prop[1]
                    if ptype.startswith('linked_to'):
                        ptype = ptype[10:-1]
                        linked = True
                    else:
                        linked = False
                    try:
                        y = Factory.build(ptype)
                    except ValueError as e:
                        ee = str(e) + f' for "{k}"'
                        raise ValueError(ee)
                    if ptype in klasses:
                        if klasses[ptype]._osl.is_document:
                            if not linked:
                                raise ValueError(f'Property {prop[0]} of {k} does not use "linked_to"')
                        elif linked:
                            raise ValueError(f'Property {prop[0]} of {k} should NOT use "linked_to"')

    def test_pstr(self):
        """ Test all variables in a pstr are actually properties"""
        klasses = Factory.ontology.klasses

        for k in klasses:
            konstructor = klasses[k]._osl
            if hasattr(konstructor, 'pstr'):
                variables = konstructor.pstr[1]
                properties = [p[0] for p in konstructor.properties] + [p[0] for p in konstructor.inherited_properties]
                for v in variables:
                    if v not in properties:
                        raise ValueError(f'pstr needs variable [{v}] not found in properties for [{k}]')

    def test_str(self):
        """ Test it is possible to return a string value for anything"""
        klasses = Factory.ontology.klasses
        for k in klasses:
            x = Factory.build(k)
            try:
                y = str(x)
            except:
                raise ValueError(f'Unable to construct a string for {k}')

    def test_specific_strings(self):
        """ Test some specific string representations"""
        a = Factory.build('shared.party')
        archer = new_document('platform.machine', 'Archer', a)
        self.assertEqual(str(archer), 'Archer')

        n = named_build('platform.storage_pool', 'Storage')
        fs1 = numeric_value(2., 'PB')
        fs2 = numeric_value(3., 'PB')
        n.file_system_sizes = [fs1, fs2]
        self.assertEqual(str(n), "Storage ['2.0PB', '3.0PB']")


if __name__ == "__main__":
    unittest.main()