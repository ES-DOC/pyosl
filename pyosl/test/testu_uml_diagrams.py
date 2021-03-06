import unittest, os

from pyosl import Factory, Ontology

from pyosl.uml import BasicUML
from pyosl.uml import PackageUML
from pyosl.uml import UmlBase

from pyosl.uml import uml4_activity, uml4_cmip, uml4_data, uml4_design, \
    uml4_drs, uml4_iso, uml4_platform, uml4_science, uml4_shared, uml4_software, \
    uml4_time


class TestGraphCases(unittest.TestCase):

    def setUp(self):
        # pycharm test hack follows, allows pycharm test auto discover to co-exist
        # with an independent sub package for the tests, and find the output directory.
        if os.getcwd().endswith('pyosl'):
            os.chdir(os.path.join(os.getcwd(), 'test'))

        Factory.register(Ontology(UmlBase))

        self.v2p1 = Factory.ontology.full_version > '2.1.0'
        print(f'Running Graph tests with {Factory.ontology.full_version} ({self.v2p1})')

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
        uml4_software()

    def test_drs(self):
        uml4_drs()

    def test_science(self):
        uml4_science()

    def test_platform(self):
        uml4_platform()

    def test_design(self):
        uml4_design()

    def test_activity(self):
        uml4_activity(self.v2p1)

    def test_data(self):
        uml4_data(self.v2p1)

    def test_iso(self):
        if self.v2p1:
            uml4_iso()

    def test_shared(self):
        uml4_shared()

    def test_cmip(self):
        if self.v2p1:
            uml4_cmip()

    def test_time(self):
        uml4_time()

    def test_simulation(self):
        """ Understand how the various simulation pieces go together"""
        d = BasicUML('test_output/understand_simulation', option='uml', title="Explain Simulation")
        if self.v2p1:
            klasses = ['activity.ensemble_axis',
                               'activity.ensemble',
                               'activity.simulation',
                               'activity.child_simulation',
                               'activity.conformance',
                               'cmip.cmip_simulation',
                               'cmip.cmip_dataset'
                               ]
        else:
            klasses = ['activity.ensemble_axis',
                       'activity.ensemble_member',
                       'activity.ensemble',
                       'data.simulation',
                       'activity.parent_simulation',
                       'activity.conformance',
                       ]
        d.set_visible_classes(klasses, expand_base=False, expand_associated=False,
                              )
        d.set_association_edges(multiline=True)
        d.generate_pdf()

    def test_models(self):
        """ Explain relationships between some key entities in the model/software world."""
        d = BasicUML('test_output/understand_models', option='uml', title="Explain Models")
        d.set_visible_classes(['science.model', 'software.software_component',
                               'software.component_base','science.realm','science.realm_coupling',
                               'science.topic','science.model_types',
                               'software.coupling_framework','software.composition','software.implementation',
                               'software.development_path'], expand_base=False, expand_associated=False)
        d.set_association_edges(multiline=True)
        d.generate_pdf()

    def test_simple_perf(self):
        """ Explain the relationship between performande and software as it currently stands. """
        d = BasicUML('test_output/understand_perf', option='uml', title="Performance and Software")
        d.set_visible_classes(['science.model', 'software.software_component','science.realm',
                               'platform.performance',
                               'software.composition', 'software.implementation',
                               ], expand_base=True, expand_associated=False)
        d.set_association_edges(multiline=True)
        d.generate_pdf()

    def test_twoeg(self):
        """ Produce twoeg UML diagram for the core paper"""
        d = BasicUML('test_output/twoeg', option='uml', coloured=False)
        d.set_visible_classes(['time.date_time', 'iso.md_cellgeometry_code'],
                              expand_base=True, expand_associated=False)
        d.set_association_edges(multiline=True)
        d.generate_pdf()


    def test_quality(self):
        """ Produce two UML diagrams for quality figure in core paper"""
        d = BasicUML('test_output/quality_meta', option='uml', coloured=False,)
                     #title='Metadata Quality (from Shared package)')
        d.set_visible_classes(['shared.quality_review', 'shared.quality_status'],
                              expand_base=True, expand_associated=False)
        d.set_association_edges(multiline=True)
        d.generate_pdf()
        d = BasicUML('test_output/quality_science', option='uml', coloured=False,)
                     #title='Scientific Metadata Quality (from ISO package)')
        d.set_visible_classes(['iso.quality_report', 'iso.quality_evaluation_result','iso.quality_issue',
                                'iso.quality_evaluation_output','iso.dq_evaluation_result_type'],
                              expand_base=False, expand_associated=False)
        d.direct_samerank([('iso.quality_evaluation_output', 'iso.dq_evaluation_result_type')])
        d.set_association_edges(multiline=True)
        d.generate_pdf()

class TestPackageUML(unittest.TestCase):

    def setUp(self):
        # pycharm test hack follows, allows pycharm test auto discover to co-exist
        # with an independent sub package for the tests, and find the output directory.
        if os.getcwd().endswith('pyosl'):
            os.chdir(os.path.join(os.getcwd(), 'test'))

    def test_umlontology(self):

        p = PackageUML('test_output/test_all-uml')
        p.generate_pdf()


if __name__ == "__main__":
    unittest.main()
