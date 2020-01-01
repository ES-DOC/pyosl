import unittest
from pyosl import Factory
from pyosl.tools import named_build, calendar_period, osl_fill_from, online, numeric_value, get_reference_for
from pyosl.tools import osl_encode2json, bundle_instance, Triples
from pyosl.uml import TriplesDelux


def make_archer():
    """ As an example, let's minimally describe ARCHER. In this case with one json document."""

    # establish documents:
    author = Factory.new_document('shared.party')
    archer = Factory.new_document('platform.machine', author)
    cray = Factory.new_document('shared.party', author)
    epcc = Factory.new_document('shared.party', author)

    # flesh out the party attributes
    author.name = 'Bryan Lawrence'
    author.orcid_id = '0000-0001-9262-7860'
    author.url = online('http://wwww.bnlawrence.net','personal website')
    cray.name = "Cray"
    cray.url = online('https://cray.com','Website')
    epcc.name = 'Edinburgh Parallel Computer Centre'
    epcc.url = online('https://epcc.ed.ac.uk', 'Website')

    # now build some class instances
    highmem_nodes = named_build('platform.compute_pool', 'High Memory Nodes')
    normal_nodes = named_build('platform.compute_pool', 'Normal Nodes')
    work = named_build('platform.storage_pool', 'Work Filesystems')
    home = named_build('platform.storage_pool','Home Storage')
    dragonfly = named_build('platform.interconnect','Dragonfly')

    # and build our description of ARCHER:
    archer.name = 'Archer'
    archer.description = "UKRI shared national compute service"
    archer.compute_pools = [highmem_nodes, normal_nodes]
    archer.storage_pools = [home, work]
    archer.vendor = cray
    archer.interconnect = dragonfly
    archer.model_number = 'XC-30'
    archer.online_documentation = [online('https://archer.ac.uk','website'),]
    archer.when_available = calendar_period('2013-11-01','2020-01-16')

    # flesh out some of the class instances
    highmem_nodes.compute_cores_per_node = 24
    highmem_nodes.cpu_type = 'Ivy Bridge'
    highmem_nodes.memory_per_node = numeric_value(128., 'GB')
    highmem_nodes.number_of_nodes = 376
    highmem_nodes.model_number = 'E5-2697 v2'
    highmem_nodes.clock_speed = numeric_value(2.7,'GHz')
    normal_nodes.memory_per_node = numeric_value(64., 'GB')
    normal_nodes.number_of_nodes = 4544
    normal_nodes = osl_fill_from(normal_nodes, highmem_nodes)

    work.description = 'Primary parallel file storage for data. Not backed up.'
    work.type = 'Lustre'
    work.vendor = cray
    work.file_system_sizes = [numeric_value(1.4, 'PB'), numeric_value(1.4, 'PB'),
                              numeric_value(1.6, 'PB'), ]

    home.description = "Storage for code, and important results - backed up"
    home.type = 'NFS'
    home.file_system_sizes = [numeric_value(218., 'TB'), ]

    return archer


def make_archer2():
    """ As an example, let's minimally describe ARCHER2. In this case with several json documents."""

    # establish documents:
    author = Factory.new_document('shared.party')
    author.name = 'Bryan Lawrence'
    author.orcid_id = '0000-0001-9262-7860'
    author.url = online('http://wwww.bnlawrence.net', 'personal website')

    gauthor = get_reference_for(author)
    archer = Factory.new_document('platform.machine', gauthor)
    cray = Factory.new_document('shared.party', gauthor)

    cray.name = "Cray"
    cray.url = online('https://cray.com', 'Website')

    # now build some class instances
    highmem_nodes = named_build('platform.compute_pool', 'High Memory Nodes')
    normal_nodes = named_build('platform.compute_pool', 'Normal Nodes')
    work = named_build('platform.storage_pool', 'Work Filesystems')
    home = named_build('platform.storage_pool', 'Home Storage')
    burst = named_build('platform.storage_pool', 'Burst Buffer')
    slingshot = named_build('platform.interconnect', 'Slingshot Interconnect')
    nic = named_build('platform.nic','Shasta SS-10')

    # and build our description of ARCHER:
    archer.name = 'Archer2'
    archer.description = "UKRI shared national compute service"
    archer.compute_pools = [highmem_nodes, normal_nodes]
    archer.storage_pools = [home, work]
    archer.vendor = cray
    archer.interconnect = slingshot
    archer.online_documentation = [online('https://archer.ac.uk', 'website'), ]
    archer.when_available = calendar_period('2020-06-01','2026-05-30')


    # flesh out some of the class instances
    highmem_nodes.compute_cores_per_node = 128
    highmem_nodes.cpu_type = 'AMD Rome'
    highmem_nodes.memory_per_node = numeric_value(512, 'GB')
    highmem_nodes.number_of_nodes = 292
    highmem_nodes.clock_speed = numeric_value(2.2, 'GHz')
    highmem_nodes.network_cards_per_node=[nic, nic]
    normal_nodes.memory_per_node = numeric_value(256, 'GB')
    normal_nodes.number_of_nodes = 5556
    normal_nodes = osl_fill_from(normal_nodes, highmem_nodes)
    nic.bandwidth = numeric_value(100, 'Gb')
    nic.vendor = cray

    work.description = 'Primary parallel file storage for data. Not backed up.'
    work.type = 'Lustre'
    work.vendor = cray
    work.file_system_sizes = [numeric_value(1.4, 'PB'), numeric_value(1.4, 'PB'),
                              numeric_value(1.6, 'PB'), ]

    home.description = "Storage for code, and important results - backed up"
    home.type = 'NFS'
    home.file_system_sizes = [numeric_value(218., 'TB'), ]

    burst.description = ''
    burst.type = 'lustre'
    burst.file_system_sizes = [numeric_value(1.1,'PB'),]

    return bundle_instance(archer)


class MakeArcher(unittest.TestCase):

    def test_make(self):

        archer = make_archer()
        archer_json = osl_encode2json(archer)

        print(f'\n** Single\n{archer_json}\n**')

    def test_make2(self):
        archer_json2 = make_archer2()
        print('\n## Bundled')
        for x in archer_json2:
            print(x+'\n##')


class TestTriples(unittest.TestCase):
    """ Test output of triples"""

    def setUp(self):
        self.a = make_archer()

    def test_triples(self):
        g = Triples()
        g.add_instance(self.a)
        print(g)
        for i,j in zip(g.triples[0],
                       ('http://esdoc-org/osl/platform.machine/Archer', 'rdf:type', 'platform.machine')):
            self.assertEqual(i,j)
#TODO: Why is the name of the first triple wrong?
#TODO: Check that the doc_meta_infos (and everything else) are linked right.
#TODO: Proper triple serialisation using something we can input to a visualisation package (or do my own).

    def test_graphtriples(self):
        g = TriplesDelux(self.a)
        g.make_graph(dot_required=True)
        g.make_pdf()


if __name__ == "__main__":
    unittest.main()
