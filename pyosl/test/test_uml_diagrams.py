import unittest

from pyosl import Factory, Ontology

from pyosl.uml import BasicUML
from pyosl.uml import PackageUML
from pyosl.uml import UmlBase



class TestGraphCases(unittest.TestCase):

    def setUp(self):
        Factory.register(Ontology(UmlBase))

    def test_experiment(self):
        """ Test that we can build a klass, and that it has the correct typekey
        (i.e. it's come from the ontology), and that it has one of the new
        attributes (i.e. it is a proper subclass)."""

        e = Factory.build('designing.numerical_experiment')
        assert e._osl.type_key == 'cim.2.designing.numerical_experiment'
        assert e.label() == 'numerical\nexperiment'

    def test_makediagrams(self):
        """ Simply makes activity diagrams """
        d = BasicUML('test_output/testing', option='box')
        d.set_visible_classes(['designing.numerical_experiment', ], expand_base=False)
        d.set_association_edges(multiline=True)
        d.direct_edge_ports([('designing.project','designing.project','sub_projects','s','s'),])
        d.generate_pdf()

    def test_makediagrams_and_omit(self):
        """ Simply makes activity diagrams """
        d = BasicUML('test_output/testing1', option='uml')
        d.set_visible_classes(['designing.numerical_experiment', ], expand_base=False, omit_classes=['designing.project',])
        d.set_association_edges(multiline=True)
        d.generate_pdf()

    def test_makediagrams_and_omit_BOX(self):
        """ Simply makes activity diagrams """
        d = BasicUML('test_output/testing3', option='box')
        d.set_visible_classes(['designing.numerical_experiment', ], expand_base=False, omit_classes=['designing.project',])
        d.set_association_edges(multiline=True)
        d.generate_pdf()

    def test_explain_requirements(makedot=False):
        """ A diagram to explain numerical requirements. Exercises direct_layout and direct_edge_ports"""
        d = BasicUML('test_output/testing2', option='bubble')
        d.set_visible_package('designing',
                              omit_classes=['activity.axis_member', 'designing.project', 'activity.activity',
                                            'designing.numerical_experiment', 'designing.simulation_plan',
                                            'designing.experimental_relationships',
                                            ])
        d.direct_layout([('designing.numerical_requirement', 'Hidden'),
                         ('Hidden', 'designing.initialisation_requirement'),
                         ('designing.initialisation_requirement', 'designing.output_requirement'),
                         ('Hidden', 'designing.domain_requirements'),
                         ('Hidden', 'designing.temporal_constraint'),
                         ('designing.multi_ensemble', 'designing.start_date_ensemble'),
                         ('Hidden', 'designing.forcing_constraint')])
        d.direct_edge_ports([('designing.numerical_requirement', 'designing.numerical_requirement', 'additional_requirements', 'nw', 'ne'), ])
        d.set_association_edges(multiline=True)
        d.generate_pdf()

    def test_software(self):
        """ Examine the software package"""
        d = BasicUML('test_output/testsw', option='uml')
        d.set_visible_package('software', restrict=True)
        d.set_association_edges(multiline=True)
        d.generate_pdf()

    def test_science(self):
        """ Examine the science package"""
        d = BasicUML('test_output/testsci', option='uml')
        d.set_visible_package('science', restrict=False)
        d.set_association_edges(multiline=True)
        d.generate_pdf()

    def test_design(self):
        """ Examine the design package"""
        d = BasicUML('test_output/testdes', option='uml')
        d.set_visible_package('designing', restrict=True, show_base_links=False)
        d.set_association_edges(multiline=True)
        d.fix_layout(3, ['designing.numerical_requirement_scope',])
        d.generate_pdf()

class TestPackageUML(unittest.TestCase):

    def test_umlontology(self):

        p = PackageUML('test_all-uml')
        p.generate_pdf()


if __name__ == "__main__":
    unittest.main()
