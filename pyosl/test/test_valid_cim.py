import unittest

from pyosl import Factory


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



if __name__ == "__main__":
    unittest.main()