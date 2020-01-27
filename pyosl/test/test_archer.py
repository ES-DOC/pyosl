import unittest
from pyosl import Factory
from pyosl.tools import named_build, calendar_period, osl_fill_from, online, numeric_value, get_reference_for, \
    new_document
from pyosl.tools import osl_encode2json, bundle_instance, Triples, Triples2
from pyosl.uml import TriplesDelux

import networkx as nx
import matplotlib.pyplot as plt
import math

from collections import namedtuple, OrderedDict


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
    nic = named_build('platform.nic', 'Shasta SS-10')

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
    highmem_nodes.network_cards_per_node = [nic, nic]
    normal_nodes.memory_per_node = numeric_value(256., 'GB')
    normal_nodes.number_of_nodes = 5556
    osl_fill_from(normal_nodes, highmem_nodes)
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


def shells_with_adjacent_layout(G, root):
    """ Provides and populates a canvas of node positions for a networkx
    graph, [[G]] in shells around a central [[root]] node. Returns a dictionary
    of nodes positions keyed from node name."""

    class Slot:
        def __init__(self, a, x, y):
            self.a, self.x, self.y = a, x, y
            self.used = False

    class Slots:
        """ Set up the list of possible places for a node to be """

        def __init__(self, rank_sizes, radius=1.5, scale=1.0):
            """ Initialise with a list of rank sizes, which we assume we will have found via
            graph analysis. """
            self.radius, self.scale = radius, scale
            self.slots = [[Slot(0, 0.0, 0.0), ], ]
            for i, size in enumerate(rank_sizes[1:]):
                self.slots.append(self.get_slots(i + 1, size))
            self.nodes = {}
            self.rank_delta = [0, ]
            for rnk in range(len(rank_sizes))[1:]:
                self.rank_delta.append(self.slots[rnk][1].a - self.slots[rnk][0].a)

        def get_slots(self, index, n):
            """ Get [[n]] slots for [[index]] shell"""

            def getxy(i, n, radius, offset=0):
                """ Get the ith slot of n at distance radius from origin starting from offset radians """
                angle = offset + i * 2 * math.pi / n
                x = math.sin(angle) * radius
                y = math.cos(angle) * radius
                return Slot(angle, x, y)

            r = self.radius * self.scale * index
            return [getxy(i, n, r) for i in range(n)]

        def add_node(self, node, rank, inner_node=None):
            """ Place node in unused slot in rank,
            if inner_node present, attempt to place near in angle terms to inner_node"""
            if inner_node:
                if rank < 2:
                    raise ValueError("Cannot use inner_node option for ranks less than 2")
                try:
                    first_guess = self.nodes[inner_node].a
                except KeyError:
                    raise ValueError(f'Attempt to use inner_node ({inner_node}) not seen before')
                ip = round(first_guess / self.rank_delta[rank])
                for s in self.slots[rank][ip:]:
                    if not s.used:
                        s.used = True
                        self.nodes[node] = s
                        return
                for s in reversed(self.slots[rank][0:ip]):
                    if not s.used:
                        self.nodes[node] = s
                        return
            else:
                for s in self.slots[rank]:
                    if not s.used:
                        s.used = True
                        self.nodes[node] = s
                        return
            raise ValueError(f'Unable to insert f{node} into rank {rank}')

    ranks = [[root], list(G.neighbors(root)),]
    collected = ranks[0]+ranks[1]
    ranks.append([])
    current = 2
    while len(collected) < len(G.nodes()):
        for s in ranks[current-1]:
            nodes = G.neighbors(s)
            for n in nodes:
                if n not in collected:
                    ranks[current].append(n)
                    collected.append(n)
        current += 1

    rank_sizes = [len(rank) for rank in ranks]
    if len(rank_sizes) > 4:
        nn = len(G.nodes())
        raise ValueError(f'This code not suitable for {nn} nodes')

    possible_sizes = [1, 8, 24, 48]
    placement_sizes = [max(n,p) for n,p in zip(rank_sizes, possible_sizes)]

    allslots = Slots(placement_sizes)

    for i in range(len(ranks)):
        if i > 1:
            # do it as adjacencies from inner rank
            for n in ranks[i-1]:
                edges = G.edges(n)
                for s,o in edges:
                    print('edge',s, o)
                    if o not in allslots.nodes:
                        allslots.add_node(o, i, inner_node=n)
        else:
            for node in ranks[i]:
                allslots.add_node(node, i)

    return {k: (v.x, v.y) for k,v in allslots.nodes.items()}


class Viewer:
    """ Provides at least one way of plotting a pyosl instance"""
    def __init__(self, instance):
        self.ts = Triples2()
        self.ts.add_instance(instance)
        self.clean_triples = [(self._clean(i), self._cleanp(j), self._clean(k))
                         for i, j, k in self.ts.semantic_triples]
        self.docs = [self._clean(n) for n in self.ts.semantic_nodes['shared.doc_reference']]
        self.urls = [self._clean(n) for n in self.ts.semantic_nodes['shared.online_resource']]

        # removing duplicates as we go
        subjects = list(dict.fromkeys([a for a,b,c in self.clean_triples]))
        objects = list(dict.fromkeys([c for a,b,c in self.clean_triples]))
        nodes = list(dict.fromkeys(subjects+objects))
        self.others = [x for x in nodes if str(x) not in self.docs+self.urls]

    def _clean(self, s):
        """ Used to clean up node names """
        if s.find('(') != -1:
            s = s[0:s.find('(')].rstrip(' ')
        return "{}".format(s.replace(' ', '\n').replace('https://', ''))

    def _cleanp(self, s):
        """ Used to clean predicates """
        return s.replace('_', '\n')

    def view_nx(self, layout='adjacent'):
        """ Use nx, experimental code """
        G = nx.MultiDiGraph()
        G.add_edges_from([(i, k) for i, j, k in self.clean_triples])

        if layout == 'adjacent':
            pos = shells_with_adjacent_layout(G, 'Archer')
        elif layout == 'kamada':
            pos = nx.kamada_kawai_layout(G, scale=2)
        else:
            raise ValueError(f'Unknown layout option {layout}')

        otherlabels = {n: n for n in self.others}
        doclabels = {n: n for n in self.docs}
        urllabels = {n: n for n in self.urls}

        fig, ax = plt.subplots(figsize=(12, 12))
        ax.set_xlim((-6, 6))
        ax.set_ylim((-6, 6))

        nx.draw_networkx_nodes(G, pos, self.others, node_size=5800, node_color='lightcoral')
        nx.draw_networkx_labels(G, pos, otherlabels, font_size=10)
        nx.draw_networkx_nodes(G, pos, self.urls, node_size=5800, node_color='gainsboro')
        nx.draw_networkx_labels(G, pos, urllabels, font_size=10)
        nx.draw_networkx_nodes(G, pos, self.docs, node_size=5800, node_color='lightblue')
        nx.draw_networkx_labels(G, pos, doclabels, font_size=12)
        nx.draw_networkx_edges(G, pos)
        edge_labels = {(i, k): j for i, j, k in self.clean_triples}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)

        plt.axis('off')
        plt.axis('square')
        plt.savefig('archer.pdf')


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

    def test_semantic_triples(self):
        viewer = Viewer(self.a)
        viewer.view_nx()
        #viewer.view_nx(layout='kamada')



if __name__ == "__main__":
    unittest.main()
