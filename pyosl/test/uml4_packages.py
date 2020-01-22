
from pyosl.uml import BasicUML
from pyosl import Factory, Ontology
from pyosl.uml import UmlBase

Factory.register(Ontology(UmlBase))


def uml4_activity(iso_package_exists=True):
    d = BasicUML('test_output/doc_activity', option='uml', title="Activity Package", rankdir='LR')
    extras = {0: [], 1: ['iso.process_step', ]}[iso_package_exists]
    d.set_visible_package('activity', extra_classes=extras, restrict=True, show_base_links=False)
    d.set_association_edges(multiline=True)
    d.direct_samerank([('activity.conformance', 'activity.conformance_type', 'iso.process_step'),
                       ('activity.child_simulation', 'activity.axis_member', 'activity.ensemble_axis'),
                       ('activity.ensemble', 'activity.simulation')])
    d.generate_pdf()


def uml4_cmip():
    d = BasicUML('test_output/doc_cmip', option='uml', title="CMIP Package")
    d.set_visible_package('cmip', restrict=True, show_base_links=False)
    d.set_association_edges(multiline=True)
    d.generate_pdf()

def uml4_data(iso_package_exists=True):
    d = BasicUML('test_output/doc_data', option='uml', title="Data Package")
    extras = {0: [], 1: ['iso.lineage', ]}[iso_package_exists]
    d.set_visible_package('data', extra_classes=extras, restrict=True, show_base_links=False)
    d.set_association_edges(multiline=True)
    d.generate_pdf()


def uml4_design():
    """ Examine the design package"""
    d = BasicUML('test_output/doc_designing', option='uml', title="Designing Package", )
    d.set_visible_package('designing', restrict=True, show_base_links=False)
    d.set_association_edges(multiline=True)
    d.direct_layout([('designing.simulation_plan','designing.experimental_relationships'),
                     ('designing.initialisation_requirement', 'designing.domain_requirements'),
                     ('designing.temporal_constraint', 'designing.output_requirement'),
                     ('designing.ensemble_types', 'designing.start_date_ensemble')
                       ])

    d.generate_pdf()


def uml4_drs():
    d = BasicUML('test_output/doc_drs', option='uml', title='DRS Package')
    d.set_visible_package('drs', restrict=True)
    d.set_association_edges(multiline=True)
    d.direct_layout([('drs.drs_geographical_operators', 'drs.drs_simulation_identifier'),
                         ('drs.drs_time_suffixes','drs.drs_experiment')])
    d.generate_pdf()


def uml4_iso():
    d = BasicUML('test_output/doc_iso', option='uml', title="ISO Package")
    d.set_visible_package('iso', restrict=True, show_base_links=False)
    d.set_association_edges(multiline=True)
    # make diagram a bit more compact:
    # d.direct_samerank([('iso.quality_evaluation_output','iso.md_progress_code')])
    d.direct_layout([('iso.quality_issue', 'iso.ds_initiative_typecode'),
                     ('iso.ds_initiative_typecode', 'iso.md_cellgeometry_code'),
                     ('iso.process_step_report', 'iso.md_progress_code')])
    d.generate_pdf()

def uml4_platform():
    """ Examine the platform package"""
    d = BasicUML('test_output/doc_platform', option='uml', title="Platform Package")
    d.set_visible_package('platform', extra_classes=[], restrict=True)
    d.set_association_edges(multiline=True)
    # make the graph a bit more vertical and less horizontal:
    d.direct_samerank([('platform.machine', 'platform.partition'), ('platform.interconnect', 'platform.nic'), ])
    d.direct_edge_ports([('platform.partition', 'platform.machine', '', 'se', 'w')])
    d.generate_pdf()


def uml4_science():
    """ Examine the science package"""
    d = BasicUML('test_output/doc_science', option='uml', title="Science Package")
    d.set_visible_package('science', restrict=True)
    d.set_association_edges(multiline=True)
    d.direct_samerank([('science.topic_property_set','science.topic_property'),
                       ('science.topic', 'science.realm')])
    #d.direct_layout([('science.realm','science.model_types')])
    d.generate_pdf()


def uml4_shared():
    d = BasicUML('test_output/doc_shared', option='uml', title="Shared Package")
    d.set_visible_package('shared', restrict=True, show_base_links=False)
    d.set_association_edges(multiline=True)
    d.generate_pdf()

def uml4_software():
    """ Examine the software package"""
    d = BasicUML('test_output/doc_software', option='uml', title="Software Package")
    d.set_visible_package('software', restrict=True)
    d.set_association_edges(multiline=True)
    d.generate_pdf()


def uml4_time():
    d = BasicUML('test_output/doc_time', option='uml', title='Time Package')
    d.set_visible_package('time', restrict=True)
    d.set_association_edges(multiline=True)
    d.generate_pdf()
