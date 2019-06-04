import unittest
from mp_base import Base
from mp_property import Property, PropertyDescriptor
from factory import Factory, Ontology
from copy import copy
from osl_tools import volume, named_build, calendar_period, osl_fill_from, online, numeric_value

# make a factory to use in the test cases
FACTORY = Factory
FACTORY.register(Ontology(Base))
FACTORY.add_descriptor(PropertyDescriptor, Property)

def make_archer():
    """ As an example, let's describe ARCHER"""

    # establish documents
    author = Factory.new_document('shared.party')
    author.name = 'Bryan Lawrence'
    author.orcid_id = '0000-0001-9262-7860'
    author.url = online('http://wwww.bnlawrence.net','personal website')

    archer = Factory.new_document('platform.machine', author)
    cray = Factory.new_document('shared.party', author)
    cray.name = "Cray"
    cray.url = online('https://cray.com','Website')
    epcc = Factory.new_document('shared.party', author)
    epcc.name = 'Edinburgh Parallel Computer Centre'
    epcc.url = online('https://epcc.ed.ac.uk', 'Website')

    highmem_nodes = named_build('platform.compute_pool', 'High Memory Nodes')
    normal_nodes = named_build('platform.compute_pool', 'Normal Nodes')
    work = named_build('platform.storage_pool', 'Work Filesystems')
    home = named_build('platform.storage_pool',' Home Storage')
    dragonfly = named_build('platform.interconnect',' Dragonfly')

    archer.name = 'Archer'
    archer.description = "UKRI shared national compute service"
    archer.compute_pools = [highmem_nodes, normal_nodes]
    archer.storage_pools = [home, work]
    archer.vendor = cray
    archer.interconnect = dragonfly
    archer.model_number = 'XC-30'
    archer.online_documentation = [online('https://archer.ac.uk','website'),]
    archer.when_available = calendar_period('2013-11-01','2020-01-16')

    highmem_nodes.compute_cores_per_node = 24
    highmem_nodes.cpu_type = 'Ivy Bridge'
    highmem_nodes.memory_per_node = volume(128, 'GB')
    highmem_nodes.number_of_nodes = 376
    highmem_nodes.model_number = 'E5-2697 v2'
    highmem_nodes.clock_speed = numeric_value(2.7,'GHz')

    normal_nodes.memory_per_node = volume(64, 'GB')
    normal_nodes.number_of_nodes = 4544
    normal_nodes = osl_fill_from(normal_nodes, highmem_nodes)

    #TODO Storage Pools







class MakeArcher(unittest.TestCase):



   def test_make(self):
       archer = make_archer()


if __name__=="__main__":
    unittest.main()