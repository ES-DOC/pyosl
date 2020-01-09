import unittest
from pyosl import Factory
from pyosl.tools import named_build, calendar_period, osl_fill_from, online, numeric_value, get_reference_for, \
    new_document
from pyosl.tools import osl_encode2json, bundle_instance, Triples, Triples2
from pyosl.uml import TriplesDelux

from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

def make_archer():
    """ As an example, let's minimally describe ARCHER. In this case with one json document."""

    # establish documents:
    author = Factory.new_document('shared.party')
    archer = new_document('platform.machine', 'Archer', author)
    cray = new_document('shared.party', 'Cray', author)
    epcc = new_document('shared.party', 'Edinburgh Parallel Computer Centre', author)

    # flesh out the party attributes
    author.name = 'Bryan Lawrence'
    author.orcid_id = '0000-0001-9262-7860'
    author.url = online('http://www.bnlawrence.net','personal website')

    cray.url = online('https://cray.com','Website')
    epcc.url = online('https://epcc.ed.ac.uk', 'Website')

    # now build some class instances
    highmem_nodes = named_build('platform.compute_pool', 'High Memory Nodes')
    normal_nodes = named_build('platform.compute_pool', 'Normal Nodes')
    work = named_build('platform.storage_pool', 'Work Filesystems')
    home = named_build('platform.storage_pool','Home Storage')
    dragonfly = named_build('platform.interconnect','Dragonfly')

    # and build our description of ARCHER:

    archer.description = "UKRI shared national compute service"
    archer.compute_pools = [highmem_nodes, normal_nodes]
    archer.storage_pools = [home, work]
    archer.vendor = cray
    archer.interconnect = dragonfly
    archer.model_number = 'XC-30'
    archer.online_documentation = [online('https://archer.ac.uk','website'),]
    archer.when_available = calendar_period('2013-11-01', '2020-01-16')
    archer.institution = epcc

    # flesh out some of the class instances
    highmem_nodes.compute_cores_per_node = 24
    highmem_nodes.cpu_type = 'Ivy Bridge'
    highmem_nodes.memory_per_node = numeric_value(128., 'GB')
    highmem_nodes.number_of_nodes = 376
    highmem_nodes.model_number = 'E5-2697 v2'
    highmem_nodes.clock_speed = numeric_value(2.7,'GHz')
    normal_nodes.memory_per_node = numeric_value(64., 'GB')
    normal_nodes.number_of_nodes = 4544
    osl_fill_from(normal_nodes, highmem_nodes)

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
    author.url = online('http://www.bnlawrence.net', 'personal website')

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
    highmem_nodes.memory_per_node = numeric_value(512., 'GB')
    highmem_nodes.number_of_nodes = 292
    highmem_nodes.clock_speed = numeric_value(2.2, 'GHz')
    highmem_nodes.network_cards_per_node=[nic, nic]
    normal_nodes.memory_per_node = numeric_value(256., 'GB')
    normal_nodes.number_of_nodes = 5556
    normal_nodes = osl_fill_from(normal_nodes, highmem_nodes)
    nic.bandwidth = numeric_value(100., 'Gb')
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
    burst.file_system_sizes = [numeric_value(1.1, 'PB'), ]

    return bundle_instance(archer)


def view_archer(a):
    """ Example code for very simple plotting using semantic triples output by Triples2."""

    def clean(s):
        """ Used to clean up node names """
        if s.find('(') != -1:
            s = s[0:s.find('(')].rstrip(' ')
        return "{}".format(s.replace(' ', '\n').replace('https://', ''))

    def cleanp(s):
        """ Used to clean predicates """
        return s.replace('_', '\n')

    ts = Triples2()
    ts.add_instance(a)

    G = nx.MultiDiGraph()
    clean_triples = [(clean(i), cleanp(j), clean(k))
                     for i, j, k in ts.semantic_triples]
    G.add_edges_from([(i, k) for i, j, k in clean_triples])

    # We want some more spreading
    df = pd.DataFrame(index=G.nodes(), columns=G.nodes())
    for row, data in nx.shortest_path_length(G):
        for col, dist in data.items():
            df.loc[row, col] = dist

    # 0.61 is a subjective prettiness factor as I've used it here.
    df = df.fillna(df.max().max() * 0.6)
    #pos = nx.kamada_kawai_layout(G, dist=df.to_dict())
    pos = nx.nx_agraph.graphviz_layout(G, prog='twopi', args='-Gweight=0.1')

    # pos = nx.spring_layout(G)
    # 6000 is a subjective prettiness factor as I've used it here.

    # We could do this, but we want some control over label size etc
    # nx.draw(G, pos, with_labels=True, node_size=5600, font_size=10)

    docs = [clean(n) for n in ts.semantic_nodes['shared.doc_reference']]
    others = [x for x in G.nodes() if str(x) not in docs]
    otherlabels = {n: n for n in others}
    doclabels = {n: n for n in docs}
    nx.draw_networkx_nodes(G, pos, others,  node_size=5800,  node_color='r')
    nx.draw_networkx_labels(G, pos, otherlabels, font_size=10)
    nx.draw_networkx_nodes(G, pos, docs, node_size=5800,  node_color='b')
    nx.draw_networkx_labels(G, pos, doclabels, font_size=12)
    nx.draw_networkx_edges(G, pos)
    edge_labels = {(i, k): j for i, j, k in clean_triples}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    plt.show()



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

    def test_rdflib(self):
        """ Test serialisation using rdflib"""
        ts = Triples2()
        ts.add_instance(self.a)
        ts.g.serialize(destination='turtle.txt', format='turtle')

    def test_drawing(self):
        """ This is a somewhat concocted exemplar drawing"""
        def get_edge(s, p, o):
            pp = p.split('/')[-1]
            return {'label': pp}

        def get_node(n):
            r = n.find('resources')
            t = n.find('types')
            pp = n.split('/')[-1]
            if r != -1:
                return 'doc-'+pp
            elif t !=-1:
                return 'typ-'+pp
            elif len(n) == 33:
                return 'bla-'+pp
            else:
                return pp

        ts = Triples2()
        ts.add_instance(self.a)

        G = rdflib_to_networkx_multidigraph(ts.g,
                                            edge_attrs=get_edge,
                                            transform_s=get_node,
                                            transform_o=get_node)
        pos = nx.kamada_kawai_layout(G, scale=3)


        # draw all document nodes

        # edge_labels = nx.get_edge_attributes(G, 'r')
        # print(edge_labels)
        # nx.draw_networkx_edge_labels(G, pos, labels=edge_labels)
        #nx.draw(G, with_labels=False)

        # find documents and types
        # node labels were annotated in the transform so they were findable

        docs = [n for n in G.nodes() if n.find('doc') == 0]
        types = [n for n in G.nodes() if n.find('typ') == 0]
        blanks = [n for n in G.nodes() if n.find('bla') == 0]
        attrs = [n for n in G.nodes()
                 if n.find('bla') !=0 and n.find('doc') != 0 and n.find('typ') != 0]

        nx.draw_networkx_nodes(G, pos, attrs, node_color='b', with_labels=False)
        nx.draw_networkx_nodes(G, pos, blanks, node_color='k', node_size=50, with_labels=False)
        nx.draw_networkx_nodes(G, pos, types, node_color='g', with_labels=False)
        nx.draw_networkx_nodes(G, pos, docs, with_labels=True, node_shape='s')
        nx.draw_networkx_edges(G, pos)
        plt.show()

    def test_semantic_triples(self):
        view_archer(self.a)



if __name__ == "__main__":
    unittest.main()
